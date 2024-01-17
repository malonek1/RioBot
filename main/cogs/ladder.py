from discord.ext import commands
import discord
import requests
from resources import EnvironmentVariables as ev, ladders

modes_body = {
    "communities": 1,
    "active": True
}
modes = requests.post("https://api.projectrio.app/tag_set/list", data=modes_body).json()["Tag Sets"]


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

                if user["num_wins"] + user["num_losses"] > 0:
                    win_pct = user["num_wins"] / (user["num_wins"] + user["num_losses"]) * 100
                else:
                    win_pct = 0

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

    @commands.command(name="ladderCompact", help="Display the ladder in a compact view. Parameters: [mode] [min_games]")
    @commands.cooldown(1, 60, commands.BucketType.default)
    async def ladder_compact(self, ctx, mode="off", min_games=5):
        await ladders.refresh_ladders()
        if str(ctx.channel.id) == ev.get_var("bot_spam_channel_id"):
            mode = ladders.find_game_mode(mode)

            ladder_values = sorted(ladders.ladders[mode].values(), key=lambda x: x["adjusted_rating"], reverse=True)

            pos = 0
            longest_elo = 0
            pos_gap = 3

            for index, user in enumerate(ladder_values):
                if user["num_wins"] + user["num_losses"] < min_games:
                    continue

                pos += 1
                if len(str(round(user["adjusted_rating"]))) > longest_elo:
                    longest_elo = len(str(round(user["adjusted_rating"])))

            if pos > 99:
                pos_gap = 4

            message = "**" + mode + " Compact Ladder, Min " + str(min_games) + " Games **\n```"
            message += "#" + (" " * pos_gap) + "Username" + (" " * (14+2-len("Username"))) + "Rtg" \
                       + (" " * (longest_elo+2-len("Rtg"))) + "W/L\n"
            pos = 1
            for index, user in enumerate(ladder_values):
                if user["num_wins"] + user["num_losses"] < min_games:
                    continue

                username_display = user["username"]

                if len(username_display) > 14:      # MAX USERNAME LENGTH SET HERE
                    username_display = username_display[:11] + "..."      # USING DOTS OVER DASH

                buffer1 = " " * (pos_gap - len(str(pos)))
                buffer2 = " " * (14 + 2 - len(username_display))
                buffer3 = " " * (longest_elo + 2 - len(str(round(user["adjusted_rating"]))))

                message += str(pos) + "." + buffer1 + username_display + buffer2 + str(round(user["adjusted_rating"])) \
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


async def setup(client):
    await client.add_cog(Ladder(client))
