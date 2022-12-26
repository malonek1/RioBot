import discord
from discord import ButtonStyle
from discord.ext import tasks, commands
from discord.ui import View, Button
import time

from resources import EnvironmentVariables as ev
from resources import gspread_client as gs
from services.random_functions import rfRandomTeamsWithoutDupes, rfRandomStadium, rfFlipCoin
from services.image_functions import ifBuildTeamImageFile
from io import BytesIO

mode_list = ["Superstars-Off Ranked", "Superstars-On Ranked", "Superstars-Off Random Teams"]

# Constant for starting percentile range for matchmaking search
PERCENTILE_RANGE = 0.15
# Constant to tell the bot where the matchmaking buttons appear
BUTTON_CHANNEL_ID = int(ev.get_var("mm_button_channel_id"))

# Constant to tell the bot where to post matchmaking updates
MATCH_CHANNEL_ID = int(ev.get_var("mm_match_channel_id"))

# The matchmaking queue
queue = {}
# The message with the matchmaking bot stuff
mm_message: discord.Message

match_count = {}
for m in mode_list:
    match_count[m] = 1

last_ping_time = {}
for m in mode_list:
    last_ping_time[m] = 0.0


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


# Command for a player to enter the matchmaking queue
# If they are in the queue already, it will refresh their presence in the queue
# You can also move from one queue to another with this
# @bot.command(name="queue", aliases=["q"], help="Enter queue")
async def enter_queue(interaction, bot: commands.Bot, game_type):
    player_rating = 1400
    player_id = str(interaction.user.id)
    player_name = interaction.user.name
    if game_type == "Superstars-On Ranked" or game_type == "Superstars-On Unranked":
        # TODO: Avoid accessing the API every time someone queues
        matches = gs.on_log_sheet.findall(player_id)
        if matches:
            player_rating = round(float(gs.on_log_sheet.cell(matches[-1].row, matches[-1].col + 3).value))
    else:
        # TODO: Avoid accessing the API every time someone queues
        matches = gs.off_log_sheet.findall(player_id)
        if matches:
            player_rating = round(float(gs.off_log_sheet.cell(matches[-1].row, matches[-1].col + 3).value))

    # put player in queue
    queue[player_id] = {
        "Name": player_name,
        "Rating": player_rating,
        "Time": time.time(),
        "Game Type": game_type
    }

    # calculate search range
    min_rating, max_rating = calc_search_range(player_rating, game_type, PERCENTILE_RANGE)

    # check for match
    await check_for_match(bot, player_id, min_rating, max_rating, 0)

    await update_queue_status()


# Command for a player to remove themselves from the queue
# If they aren't in the queue, it will just post a message with the queue status
# @bot.command(name="dequeue", aliases=["dq"], help="Exit queue")
async def exit_queue(interaction):
    if str(interaction.user.id) in queue:
        try:
            del queue[str(interaction.user.id)]
        except KeyError:
            print("Key error")
        except RuntimeError:
            print("Runtime error")
    await update_queue_status()


# refresh to see if a match can now be created with players waiting in the queue
@tasks.loop(seconds=15)
async def refresh_queue(bot: commands.Bot):
    try:
        for player in queue:
            time_in_queue = time.time() - queue[player]["Time"]
            new_range = PERCENTILE_RANGE + (PERCENTILE_RANGE * time_in_queue / 180)
            min_rating, max_rating = calc_search_range(queue[player]["Rating"], queue[player]["Game Type"], new_range)
            if await check_for_match(bot, player, min_rating, max_rating, 120):
                await update_queue_status()
                break
    except KeyError:
        print("Key error")
    except RuntimeError:
        print("Runtime error")


# Update message with the current queue status
async def update_queue_status():
    try:
        global mm_message
        queue_numbers = {}
        for mode in mode_list:
            queue_numbers[mode] = 0
        for user in queue:
            queue_numbers[queue[user]["Game Type"]] += 1

        details = ""
        new_message = str(len(queue)) + " player(s) in the matchmaking queue:"
        for mode in mode_list:
            details += mode + ": " + str(queue_numbers[mode]) + "\n"
        embed = discord.Embed()
        embed.add_field(name=new_message,
                        value=details)
        await mm_message.edit(embed=embed)
    except KeyError:
        print("Key error")
    except RuntimeError:
        print("Runtime error")


# params: player's rating and what percentile you want your search range to cover
# return: min and max rating the player can match against
def calc_search_range(rating, game_type, percentile):
    if game_type == "Superstars-On Ranked" or game_type == "Superstars-On Unranked":
        rating_list_copy = gs.on_rating_list.copy()
    else:
        rating_list_copy = gs.off_rating_list.copy()
    if game_type != "Superstars-Off Ranked":
        percentile = 5.00
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
# Uses their user_id, search range (min-max ratings), and the min time an opponent must be searching to be matched.
async def check_for_match(bot: commands.Bot, user_id, min_rating, max_rating, min_time):
    print("Player:", queue[user_id]["Name"], "Rating:", queue[user_id]["Rating"], "Time:",
          round(time.time() - queue[user_id]["Time"]), "Rating Range", min_rating, max_rating)
    channel = bot.get_channel(MATCH_CHANNEL_ID)
    if len(queue) >= 2:
        try:
            best_match = False
            for player in queue:
                if max_rating >= queue[player]["Rating"] >= min_rating and \
                        player != user_id and time.time() - queue[player]["Time"] > min_time and \
                        queue[player]["Game Type"] == queue[user_id]["Game Type"]:
                    if not best_match or abs(queue[best_match]["Rating"] - queue[user_id]["Rating"]) > abs(
                            queue[player]["Rating"] - queue[user_id]["Rating"]):
                        best_match = player

            if best_match:
                global match_count
                log_text = str(match_count[queue[user_id]["Game Type"]]) + " " + queue[user_id][
                    "Game Type"] + " match: " + queue[user_id]["Name"] + " " + str(queue[user_id]["Rating"]) + " vs " + queue[best_match][
                    "Name"] + " " + str(queue[best_match]["Rating"])
                print(log_text)
                with open("match_log.txt", "w") as file:
                    file.write(log_text)
                embed = discord.Embed()

                # RANDOMS LOGIC
                if queue[user_id]["Game Type"] == "Superstars-Off Random Teams":
                    team_list = rfRandomTeamsWithoutDupes()
                    captain_list = [team_list[0][0], team_list[1][0]]

                    file = ifBuildTeamImageFile(team_list, captain_list)
                    embed.set_image(url="attachment://image.png")
                    stadium = rfRandomStadium()
                    if rfFlipCoin == "Heads":
                        away = queue[user_id]["Name"]
                        home = queue[best_match]["Name"]
                    else:
                        away = queue[best_match]["Name"]
                        home = queue[user_id]["Name"]
                    embed.add_field(name=queue[user_id]["Game Type"] + " match found!",
                                    value=away + " (top team, away)\n" + home + " (bottom team, home)")
                    embed.add_field(name="Stadium", value=stadium)
                    await channel.send("<@" + user_id + "> <@" + str(
                        best_match) + ">", embed=embed, file=file)
                else:
                    embed.add_field(name=queue[user_id]["Game Type"] + " match found!",
                                    value=queue[user_id]["Name"] + " vs " + str(
                                        queue[best_match]["Name"]) + "\n\nFind matches in <#" + str(
                                        BUTTON_CHANNEL_ID) + ">")
                    await channel.send("<@" + user_id + "> <@" + str(
                                            best_match) + ">", embed=embed)
                match_count[queue[user_id]["Game Type"]] += 1
                if best_match in queue:
                    del queue[best_match]
                if user_id in queue:
                    del queue[user_id]
                return True
        except KeyError:
            print("Double match")
        except RuntimeError:
            print("Timing error")

    global last_ping_time
    if 300 <= time.time() - queue[user_id]["Time"] and time.time() - last_ping_time[queue[user_id]["Game Type"]] > 900:
        role_id = "<@&998791156794150943>"
        role_name = "STARS-OFF"
        if queue[user_id]["Game Type"] == "Superstars-On Ranked":
            role_id = "<@&998791464630898808>"
            role_name = "STARS-ON"
        embed = discord.Embed()
        embed.add_field(name=f'ATTENTION {role_name} GAMERS',
                        value="There is a player looking for a " + queue[user_id]["Game Type"] + " match in queue!")
        last_ping_time[queue[user_id]["Game Type"]] = time.time()
        await channel.send(role_id, embed=embed)

    if 900 < time.time() - queue[user_id]["Time"] < 915:
        user = await bot.fetch_user(user_id)
        try:
            embed = discord.Embed()
            embed.add_field(name="AFK Reminder",
                            value="You have been in the queue for 15 minutes. "
                                  "Please leave the queue if you have found a match or are no longer looking.")
            await user.send(embed=embed)
        except discord.Forbidden:
            print("DM forbidden")

    return False
