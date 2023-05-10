from discord.ext import commands
import discord
import requests
import copy
from resources import EnvironmentVariables as ev, ladders
from resources.characters import Char

modes_body = {
    "communities": 1,
    "active": True
}
modes = requests.post("https://api.projectrio.app/tag_set/list", data=modes_body).json()["Tag Sets"]

BASE_GAMES_URL = "https://api.projectrio.app/games/"

# tier_captains should be the same length as tier_min_elo
tier_captains = [Char.BOWSER, Char.DK, Char.YOSHI, Char.BIRDO, Char.LUIGI, Char.MARIO, Char.PEACH, Char.DAISY, Char.DIDDY, Char.WALUIGI, Char.WARIO]
tier_min_elo = [2000, 1800, 1600, 1400, 1200, 1000, 800, 600, 400, 200, 0]
# tier_min_elo 's last number should be 0


def win(user_score, opponent_score):
    if user_score > opponent_score:
        return 1
    else:
        return 0


def lose(user_score, opponent_score):
    if user_score < opponent_score:
        return 1
    else:
        return 0


class Ladder(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(help="display the ladder")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def ladder(self, ctx, mode="off"):
        await ladders.refresh_ladders()
        if str(ctx.channel.id) == ev.get_var("bot_spam_channel_id"):
            mode = ladders.find_game_mode(mode)

            ladder_values = sorted(ladders.ladders[mode].values(), key=lambda x: x["adjusted_rating"], reverse=True)
            message = "**" + mode + " Ladder**\n```"
            message += "#    Username          Rtg    W/L      Pct\n"
            for index, user in enumerate(ladder_values):
                buffer1 = " " * (4 - len(str(index + 1)))
                buffer2 = " " * (18 - len(user["username"]))
                buffer3 = " " * (7 - len(str(round(user["adjusted_rating"]))))
                buffer4 = " " * (8 - (len(str(user["num_wins"])) + len(str(user["num_losses"]))))

                win_pct = user["num_wins"] / (user["num_wins"] + user["num_losses"]) * 100

                message += str(index + 1) + "." + buffer1 + user["username"] + buffer2 + str(round(user["adjusted_rating"])) \
                           + buffer3 + str(user["num_wins"]) + "-" + str(user["num_losses"]) + buffer4 + str(round(win_pct, 1)) + "%\n"
                if (index + 1) % 40 == 0:
                    message += "```"
                    await ctx.send(message)
                    message = "```"
            message += "```"

            if message != "``````":
                await ctx.send(message)
        else:
            embed = discord.Embed(color=0xEA7D07)
            embed.add_field(name='The !ladder command must be used here:', value=f'<#{ev.get_var("bot_spam_channel_id")}>')
            await ctx.send(embed=embed)

    @commands.command(name="compactLadder", help="Display the ladder in a compact view [mode] [min]")
    @commands.cooldown(1, 60, commands.BucketType.default)
    async def compact_ladder(self, ctx, mode="off", min_games=0):
        await ladders.refresh_ladders()
        if str(ctx.channel.id) == ev.get_var("bot_spam_channel_id"):
            mode = ladders.find_game_mode(mode)

            ladder_values = sorted(ladders.ladders[mode].values(), key=lambda x: x["adjusted_rating"], reverse=True)

            longest_username = 0
            longest_elo = 0
            pos_gap = 3

            if len(ladder_values) > 99:
                pos_gap = 4

            for index, user in enumerate(ladder_values):
                if len(user["username"]) > longest_username:
                    longest_username = len(user["username"])
                if len(str(round(user["adjusted_rating"]))) > longest_elo:
                    longest_elo = len(str(round(user["adjusted_rating"])))

            message = "**" + mode + " Compact Ladder**\n```"
            message += "#" + (" " * pos_gap) + "Username" + (" " * (longest_username+2-len("Username"))) + "Rtg" \
                       + (" " * (longest_elo+2-len("Rtg"))) + "W/L\n"
            pos = 1
            for index, user in enumerate(ladder_values):
                if user["num_wins"] + user["num_losses"] < min_games:
                    continue

                buffer1 = " " * (pos_gap - len(str(pos)))
                buffer2 = " " * (longest_username + 2 - len(user["username"]))
                buffer3 = " " * (longest_elo + 2 - len(str(round(user["adjusted_rating"]))))

                message += str(pos) + "." + buffer1 + user["username"] + buffer2 + str(round(user["adjusted_rating"])) \
                           + buffer3 + str(user["num_wins"]) + "-" + str(user["num_losses"]) + "\n"
                if pos % 50 == 0:
                    message += "```"
                    await ctx.send(message)
                    message = "```"
                pos += 1
            message += "```"

            if message != "``````":
                await ctx.send(message)
        else:
            embed = discord.Embed(color=0xEA7D07)
            embed.add_field(name='The !ladder command must be used here:', value=f'<#{ev.get_var("bot_spam_channel_id")}>')
            await ctx.send(embed=embed)

    @commands.command(name="ladderTiers", help="Display the ladder with tiers and a minimum of 5 games")
    @commands.cooldown(1, 300, commands.BucketType.default)
    async def ladder_tiers(self, ctx, mode="off"):
        if str(ctx.channel.id) == ev.get_var("bot_spam_channel_id"):
            mode = ladders.find_game_mode(mode)

            ladder_values = sorted(ladders.ladders[mode].values(), key=lambda x: x["adjusted_rating"], reverse=True)

            users_by_tier = []

            current_tier = 0
            user_count = 0
            tier_messages = []
            for index, user in enumerate(ladder_values):
                if (user["num_wins"] + user["num_losses"]) < 5:
                    continue

                user_count += 1
                buffer1 = " " * (4 - len(str(user_count)))
                buffer2 = " " * (18 - len(user["username"]))
                buffer3 = " " * (7 - len(str(round(user["adjusted_rating"]))))
                message = str(user_count) + "." + buffer1 + user["username"] + buffer2 + str(round(user["adjusted_rating"])) \
                           + buffer3 + str(user["num_wins"]) + "-" + str(user["num_losses"]) + "\n"

                while user["adjusted_rating"] < tier_min_elo[current_tier]:
                    users_by_tier.append(tier_messages[:])
                    tier_messages.clear()
                    current_tier += 1

                tier_messages.append(message)

            emojis = ctx.message.guild.emojis
            line_count = 1
            tier_message = "**" + mode + " Ladder Tiers**\n"
            index = 0
            for tier in users_by_tier:
                if len(tier) > 0:
                    tier_captain = next((e for e in emojis if e.name.lower() == str(tier_captains[index].value).replace(" ", "").lower()), "")
                    tier_message += f"** {tier_captain} {str(tier_min_elo[index])}+**"
                    tier_message += " \n```"
                    for line in tier:
                        tier_message += line
                        line_count += 1
                    tier_message += "```\n"
                    line_count += 2
                if line_count > 40:
                    await ctx.send(tier_message)
                    tier_message = "\n"
                    line_count = 0
                index += 1
            if line_count > 2:
                await ctx.send(tier_message)
        else:
            embed = discord.Embed(color=0xEA7D07)
            embed.add_field(name='The !ladderTiers command must be used here:', value=f'<#{ev.get_var("bot_spam_channel_id")}>')
            await ctx.send(embed=embed)

    @commands.command(name="rivalsLadder", help="Display the ladder of player and their opponents for their most recent X games (default 10)")
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def rivals_ladder(self, ctx, user, mode="off", num_games=10):
        if str(ctx.channel.id) == ev.get_var("bot_spam_channel_id") and user:
            mode = ladders.find_game_mode(mode)
            longest_username = len(user)

            api_url = f"{BASE_GAMES_URL}?limit_games={str(num_games)}&tag={mode}"
            if user != "":
                api_url += f"&username={user}"
            games_data = requests.get(api_url).json()

            players = {}
            for index, game in enumerate(games_data["games"]):
                home_user = game["home_user"].lower()
                away_user = game["away_user"].lower()

                if away_user in players:
                    players[away_user]["wins"] = players[away_user]["wins"] + win(game["away_score"], game["home_score"])
                    players[away_user]["losses"] = players[away_user]["losses"] + lose(game["away_score"], game["home_score"])
                else:
                    players[away_user] = {}
                    players[away_user]["wins"] = win(game["away_score"], game["home_score"])
                    players[away_user]["losses"] = lose(game["away_score"], game["home_score"])

                if home_user in players:
                    players[home_user]["wins"] = players[home_user]["wins"] + win(game["home_score"], game["away_score"])
                    players[home_user]["losses"] = players[home_user]["losses"] + lose(game["home_score"], game["away_score"])
                else:
                    players[home_user] = {}
                    players[home_user]["wins"] = win(game["home_score"], game["away_score"])
                    players[home_user]["losses"] = lose(game["home_score"], game["away_score"])

                if len(home_user) > longest_username:
                    longest_username = len(home_user)
                if len(away_user) > longest_username:
                    longest_username = len(away_user)

            ladder_values = sorted(ladders.ladders[mode].values(), key=lambda x: x["adjusted_rating"], reverse=True)
            message = "**" + mode + " " + user + " Rivals Ladder, Last " + str(num_games) + " Games**\n```"
            message += "#    Username" + (" " * (longest_username+2-len("Username"))) + "Rtg   W/L\n"
            line_count = 2
            for index, user in enumerate(ladder_values):
                player = user["username"].lower()
                if player in players.keys():
                    line_count += 1
                    buffer1 = " " * (4 - len(str(index + 1)))
                    buffer2 = " " * (longest_username + 2 - len(user["username"]))
                    buffer3 = " " * (6 - len(str(round(user["adjusted_rating"]))))

                    message += str(index + 1) + "." + buffer1 + user["username"] + buffer2 + str(round(user["adjusted_rating"])) \
                               + buffer3 + str(players[player]["wins"]) + "-" + str(players[player]["losses"]) + "\n"
                    if line_count >= 50:
                        message += "```"
                        await ctx.send(message)
                        message = "```"
            message += "```"

            if message != "``````":
                await ctx.send(message)
        elif user is None:
            embed = discord.Embed(color=0xE8E337)
            embed.add_field(name="No user specified!", value="Please specify a user")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(color=0xEA7D07)
            embed.add_field(name='The !ladder command must be used here:', value=f'<#{ev.get_var("bot_spam_channel_id")}>')
            await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(Ladder(client))
