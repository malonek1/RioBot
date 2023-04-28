from discord.ext import commands
import discord
import requests
from resources import ladders
from resources import EnvironmentVariables as ev

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
            for index, user in enumerate(ladder_values):
                buffer1 = " " * (4 - len(str(index + 1)))
                buffer2 = " " * (20 - len(user["username"]))

                # PLACEHOLDERS

                message += str(index + 1) + "." + buffer1 + user["username"] + buffer2 + str(round(user["adjusted_rating"])) + "\n"
                if (index + 1) % 40 == 0:
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
