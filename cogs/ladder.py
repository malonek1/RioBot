from discord.ext import commands
import discord
import requests
from resources import ladders
from resources import EnvironmentVariables as ev
import math

# Rating adjustment constants
BETA = 0.85
ALPHA = 0.1

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
            if mode.lower() in ["on", "starson", "ston", "stars"]:
                mode = ladders.STARS_ON_MODE
            elif mode.lower() in ["bb", "bigballa", "balla", "big"]:
                mode = ladders.BIG_BALLA_MODE
            else:
                mode = ladders.STARS_OFF_MODE

            ladder_values = sorted(ladders.ladders[mode].values(), key=lambda x: x["rating"], reverse=True)
            message = "**" + mode + " Ladder**\n```"
            for index, user in enumerate(ladder_values):
                buffer1 = " " * (4 - len(str(index + 1)))
                buffer2 = " " * (20 - len(user["username"]))

                # PLACEHOLDERS
                player_wins = 1
                player_games = 1
                adjusted_rating = (BETA + ((1 - BETA) * (1 - (math.exp(1 - (ALPHA * player_wins)))))) * \
                                  (user["rating"] - (500 * math.sqrt(math.log10(player_games) / player_games)))

                message += str(index + 1) + "." + buffer1 + user["username"] + buffer2 + str(user["rating"]) + "\n"
                if (index + 1) % 50 == 0:
                    message += "```"
                    await ctx.send(message)
                    message = "```"
            message += "```"

            await ctx.send(message)
        else:
            embed = discord.Embed(color=0xEA7D07)
            embed.add_field(name='The !ladder command must be used here:', value=f'<#{ev.get_var("bot_spam_channel_id")}>')
            await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(Ladder(client))
