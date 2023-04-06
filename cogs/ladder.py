import discord
from discord.ext import commands
import re
import requests

modes_body = {
    "communities": 1,
    "active": True
}
modes = requests.post("https://api.projectrio.app/tag_set/list", data=modes_body).json()["Tag Sets"]

STARS_OFF_MODE = next(x for x in modes if "Stars Off" in x["name"])["name"]
STARS_ON_MODE = next(x for x in modes if "Stars On" in x["name"])["name"]
BIG_BALLA_MODE = next(x for x in modes if "Big Balla" in x["name"])["name"]


class Ladder(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(help="display the ladder")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def ladder(self, ctx, mode="off"):
        if mode in ["on", "starson", "ston", "stars"]:
            mode = STARS_ON_MODE
        elif mode in ["bb", "bigballa", "balla", "big"]:
            mode = BIG_BALLA_MODE
        else:
            mode = STARS_OFF_MODE

        ladder_body = {"TagSet": mode}
        ladder = requests.post("https://api.projectrio.app/tag_set/ladder", json=ladder_body).json()
        ladder_values = sorted(ladder.values(), key=lambda x: x["rating"], reverse=True)
        message = "```"
        for index, user in enumerate(ladder_values):
            buffer1 = " " * (4 - len(str(index)))
            buffer2 = " " * (20 - len(user["username"]))
            message += str(index) + "." + buffer1 + user["username"] + buffer2 + str(user["rating"]) + "\n"
        message += "```"

        await ctx.send(message)


async def setup(client):
    await client.add_cog(Ladder(client))
