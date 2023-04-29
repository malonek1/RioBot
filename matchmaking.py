import discord
from discord import ButtonStyle
from discord.ext import tasks, commands
from discord.ui import View, Button
import time
import asyncio
import datetime as dt
import pytz

from resources import EnvironmentVariables as ev
from resources import ladders
from services.random_functions import rfRandomTeamsWithoutDupes, rfRandomStadium, rfFlipCoin
from services.image_functions import ifBuildTeamImageFile
from helpers import utils

mode_list = [ladders.STARS_OFF_MODE, ladders.STARS_ON_MODE, ladders.BIG_BALLA_MODE]

# Constant for starting percentile range for matchmaking search
BASE_PERCENTILE_RANGE = 0.5
# Constant to tell the bot where the matchmaking buttons appear
BUTTON_CHANNEL_ID = int(ev.get_var("mm_button_channel_id"))

# Constant to tell the bot where to post matchmaking updates
MATCH_CHANNEL_ID = int(ev.get_var("mm_match_channel_id"))
MOD_CHANNEL_ID = int(ev.get_var("mod_channel_id"))
MOD_ROLE_ID = int(ev.get_var("mod_role_id"))

# The matchmaking queue
queue = {}
for m in mode_list:
    queue[m] = {}
# The message with the matchmaking bot stuff
mm_message: discord.Message

match_count = {}
for m in mode_list:
    match_count[m] = 1

last_ping_time = {}
for m in mode_list:
    last_ping_time[m] = 0.0

recent_matches = {}
for m in mode_list:
    recent_matches[m] = []


async def init_buttons(bot: commands.Bot):
    # Initialize matchmaking buttons
    global mm_message

    new_view = View(timeout=None)

    for i in range(len(mode_list)):
        button = Button(label=mode_list[i], style=ButtonStyle.blurple)

        async def press(interaction, mode=mode_list[i]):
            await interaction.response.defer()
            await enter_queue(interaction, bot, mode)
            embed = discord.Embed()
            embed.add_field(name='Queue Status:',
                            value="You have entered the " + mode + " queue.")
            await interaction.followup.send(embed=embed, ephemeral=True)

        button.callback = press
        new_view.add_item(button)

    dequeue_button = Button(label="Leave Queue", style=ButtonStyle.red)

    async def dequeue_press(interaction):
        await interaction.response.defer()
        await exit_queue(interaction)
        embed = discord.Embed()
        embed.add_field(name='Queue Status:',
                        value="You have left the matchmaking queue.")
        await interaction.followup.send(embed=embed, ephemeral=True)

    dequeue_button.callback = dequeue_press

    feedback_button = Button(label="Give Feedback", style=ButtonStyle.url, url="https://forms.gle/KNKwp86VFxrgkZiW9")

    # button_view.add_item(stars_unranked_button)
    new_view.add_item(dequeue_button)
    new_view.add_item(feedback_button)
    channel = bot.get_channel(BUTTON_CHANNEL_ID)
    history = channel.history()
    async for msg in history:
        if msg.author == bot.user:
            await msg.delete()

    embed = discord.Embed()
    embed.add_field(name="Matchmaking queue initialized! Press buttons below to search for a game.",
                    value="Queue details will appear here when a user has entered the queue")
    mm_message = await channel.send(embed=embed,
                                    view=new_view)


# Button for a player to enter the matchmaking queue
# If they are in the queue already, it will refresh their presence in the queue
async def enter_queue(interaction, bot: commands.Bot, game_type):
    player_rating = 1400
    player_id = str(interaction.user.id)
    player_name = interaction.user.name
    mm_channel = bot.get_channel(MATCH_CHANNEL_ID)
    mod_channel = bot.get_channel(MOD_CHANNEL_ID)
    account_age = interaction.user.joined_at
    sysdate = dt.datetime.now(pytz.utc) - dt.timedelta(hours=1)
    if account_age < sysdate:
        if utils.strip_non_alphanumeric(player_name) in (utils.strip_non_alphanumeric(user) for user in ladders.ladders[game_type]):
            player_rating = ladders.ladders[game_type][player_name]["rating"]
        elif utils.strip_non_alphanumeric(interaction.user.display_name) in (utils.strip_non_alphanumeric(user) for user in ladders.ladders[game_type]):
            player_rating = ladders.ladders[game_type][interaction.user.display_name]["rating"]

        # put player in queue
        queue[game_type][player_id] = {
            "Name": player_name,
            "Rating": player_rating,
            "Time": time.time()
        }

        # calculate search range
        min_rating, max_rating = calc_search_range(player_rating, game_type, 0)

        # check for match
        await check_for_match(bot, game_type, player_id, min_rating, max_rating)

        await update_queue_status()

    else:
        print("User " + str(player_name) + " tried entering a queue with an invalid discord account age of " + str(
            account_age))
        mm_embed = discord.Embed(
            title=f"User {player_name} hasn't been in the server long enough to join the queue!",
            description="New server members must wait 1 hour before being able to join the Queue. In the meantime "
                        "feel free to ping `@LFGNewNetPlayer` in order to find a game.",
            color=0xFF5733)

        mod_embed = discord.Embed(
            title=f'Suspicious activity detected!',
            color=0xFF5733)
        mod_embed.add_field(name=f'Discord User Name:', value=player_name, inline=False)
        mod_embed.add_field(name=f'Discord User ID:', value=player_id, inline=False)
        mod_embed.add_field(name=f'Joined Server:', value=account_age, inline=False)
        mod_embed.add_field(name=f'Channel Activity:', value=f'<#{MATCH_CHANNEL_ID}>', inline=False)
        await mm_channel.send(embed=mm_embed)
        await mod_channel.send(embed=mod_embed)


# Button for a player to remove themselves from the queue
# If they aren't in the queue, it will just post a message with the queue status
async def exit_queue(interaction):
    for m in mode_list:
        if str(interaction.user.id) in queue[m]:
            try:
                del queue[m][str(interaction.user.id)]
            except KeyError:
                print("Key error")
            except RuntimeError:
                print("Runtime error")
    await update_queue_status()


# refresh to see if a match can now be created with players waiting in the queue
@tasks.loop(seconds=15)
async def refresh_queue(bot: commands.Bot):
    match_found = False
    rm_delta = 0

    t = time.time() - 3600
    for m in mode_list:
        rm_delta += len(recent_matches[m])
        recent_matches[m] = list(filter(lambda s: s > t, recent_matches[m]))
        rm_delta -= len(recent_matches[m])

    try:
        for m in mode_list:
            for player in queue[m]:
                time_in_queue = time.time() - queue[m][player]["Time"]
                min_rating, max_rating = calc_search_range(queue[m][player]["Rating"], m, time_in_queue)
                if await check_for_match(bot, m, player, min_rating, max_rating):
                    match_found = True
                    break

        if match_found or rm_delta != 0:
            await update_queue_status()

    except KeyError:
        print("Key error")
    except RuntimeError:
        print("Runtime error")


# Update message with the current queue status
async def update_queue_status():
    try:
        global mm_message
        details = ""
        total = 0
        rm_total = 0
        for m in mode_list:
            total += len(queue[m])
            rm_total += len(recent_matches[m])
            details += m + ": " + str(len(queue[m])) + "\n"

        matches_made = "There have been " + str(rm_total) + " matches made in the past hour!"

        new_message = str(total) + " player(s) in the matchmaking queue:"
        embed = discord.Embed()
        embed.add_field(name=new_message,
                        value=details)
        embed.set_footer(text=matches_made)
        await mm_message.edit(embed=embed)
    except KeyError:
        print("Key error")
    except RuntimeError:
        print("Runtime error")


# params: player's rating and amount of time they've spent in queue
# return: min and max rating the player can match against
def calc_search_range(rating, game_type, time_in_queue):
    percentile = BASE_PERCENTILE_RANGE / (len(recent_matches[game_type]) + 1)
    percentile += (percentile * time_in_queue / 180)
    rating_list_copy = []
    for user in ladders.ladders[game_type]:
        rating_list_copy.append(ladders.ladders[game_type][user]["rating"])
    rating_list_copy.append(rating)
    rating_list_copy.append(0)
    rating_list_copy.append(3000)
    pct_list = sorted(rating_list_copy, reverse=True)
    max_index = round(pct_list.index(rating) - (len(pct_list) * percentile))
    min_index = round(pct_list.index(rating) + (len(pct_list) * percentile))
    if max_index < 0:
        max_index = 0
    if min_index >= len(pct_list):
        min_index = len(pct_list) - 1

    max_rating = pct_list[max_index]
    min_rating = pct_list[min_index]

    return min_rating, max_rating


# Checks if there is an available match for a user.
# Uses their user_id, search range (min-max ratings).
async def check_for_match(bot: commands.Bot, game_type, user_id, min_rating, max_rating):
    print("Player:", queue[game_type][user_id]["Name"], "Rating:", queue[game_type][user_id]["Rating"], "Time:",
          round(time.time() - queue[game_type][user_id]["Time"]), "Search Range", min_rating, max_rating)
    channel = bot.get_channel(MATCH_CHANNEL_ID)
    if len(queue[game_type]) >= 2:
        try:
            best_match = False
            for player in queue[game_type]:
                if max_rating >= queue[game_type][player]["Rating"] >= min_rating and player != user_id:
                    if not best_match or abs(queue[game_type][best_match]["Rating"] - queue[game_type][user_id]["Rating"]) \
                            > abs(queue[game_type][player]["Rating"] - queue[user_id]["Rating"]):
                        best_match = player

            # If match is found
            if best_match:
                match_queue = {user_id: queue[game_type][user_id], best_match: queue[game_type][best_match]}
                best_match_queues = []
                user_queues = []
                for mode in mode_list:
                    if best_match in queue[mode]:
                        del queue[mode][best_match]
                        best_match_queues.append(mode)
                    if user_id in queue[mode]:
                        del queue[mode][user_id]
                        user_queues.append(mode)

                global match_count
                log_text = str(match_count[game_type]) + " " + game_type + " match: " + \
                           match_queue[user_id]["Name"] + " " + str(match_queue[user_id]["Rating"]) + " vs " + \
                           match_queue[best_match]["Name"] + " " + str(match_queue[best_match]["Rating"])
                print(log_text)
                with open("match_log.txt", "w") as file:
                    file.write(log_text)
                embed = discord.Embed()

                # RANDOMS LOGIC
                if "Random" in game_type:
                    team_list = rfRandomTeamsWithoutDupes()
                    captain_list = [team_list[0][0], team_list[1][0]]

                    file = ifBuildTeamImageFile(team_list, captain_list)
                    embed.set_image(url="attachment://image.png")
                    stadium = rfRandomStadium()
                    if rfFlipCoin == "Heads":
                        away = match_queue[user_id]["Name"]
                        home = match_queue[best_match]["Name"]
                    else:
                        away = match_queue[best_match]["Name"]
                        home = match_queue[user_id]["Name"]
                    embed.add_field(name=game_type + " match found!",
                                    value=away + " (top team, away)\n" + home + " (bottom team, home)")
                    embed.add_field(name="Stadium", value=stadium)
                    await channel.send("<@" + user_id + "> <@" + str(
                        best_match) + ">", embed=embed, file=file)
                else:
                    embed.add_field(name=game_type + " match found!",
                                    value=match_queue[user_id]["Name"] + " vs " + str(
                                        match_queue[best_match]["Name"]) + "\n\nFind matches in <#" + str(
                                        BUTTON_CHANNEL_ID) + ">")
                    await channel.send("<@" + user_id + "> <@" + str(
                        best_match) + ">", embed=embed)

                # Increment total match count
                match_count[game_type] += 1

                # Add to recent matches list
                recent_matches[game_type].append(time.time())

                return True
        except KeyError:
            if best_match and best_match_queues and match_queue:
                for mode in best_match_queues:
                    queue[mode][best_match] = match_queue[best_match]
            if user_id and user_queues and match_queue:
                for mode in user_queues:
                    queue[mode][user_id] = match_queue[user_id]
            print("Double match")
        except RuntimeError:
            if best_match and best_match_queues and match_queue:
                for mode in best_match_queues:
                    queue[mode][best_match] = match_queue[best_match]
            if user_id and user_queues and match_queue:
                for mode in user_queues:
                    queue[mode][user_id] = match_queue[user_id]
            print("Timing error")
        except UnboundLocalError:
            print("Something weird went wrong")

    global last_ping_time
    if 120 <= time.time() - queue[game_type][user_id]["Time"] and time.time() - last_ping_time[game_type] > 1800:
        role_id = ""
        role_name = ""
        if game_type == ladders.STARS_OFF_MODE:
            role_id = "<@&998791156794150943>"
            role_name = "STARS-OFF"
        if game_type == ladders.STARS_ON_MODE or game_type == ladders.BIG_BALLA_MODE:
            role_id = "<@&998791464630898808>"
            role_name = "STARS-ON"
        embed = discord.Embed()
        embed.add_field(name=f'ATTENTION {role_name} GAMERS',
                        value="There is a player looking for a " + game_type + " match in queue!")
        last_ping_time[game_type] = time.time()
        await channel.send(role_id, embed=embed)

    if 1800 < time.time() - queue[game_type][user_id]["Time"] < 1815:
        user = await bot.fetch_user(user_id)
        try:
            embed = discord.Embed()
            embed.add_field(name="AFK Reminder",
                            value="You have been in the queue for 30 minutes. "
                                  "Please leave the queue if you have found a match or are no longer looking.")
            await user.send(embed=embed)
        except discord.Forbidden:
            print("DM forbidden")

    return False
