import discord
import requests
from discord.ext import commands

from helpers.offensive_stat_calcs import ostat_user_char, ostat_user, ostat_char, ostat_all
from helpers.pitching_stat_calcs import pstat_user_char, pstat_user, pstat_char, pstat_all
from resources import ladders, characters

BASE_WEB_URL = "https://api.projectrio.app/stats/"


class WebStatLookup(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="ostat", help="Look up player batting stats on Project Rio")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def o_stat(self, ctx, user="all", char="all", mode=ladders.STARS_OFF_MODE):
        mode = ladders.get_web_mode(mode)
        if char.lower() in characters.aliases:
            char = characters.mappings[characters.aliases[char.lower()]]
        if char == "all" and user == "all":
            await ostat_all(ctx, mode)
        elif char == "all" and user != "all":
            await ostat_user(ctx, user, mode)
        elif char != "all" and user == "all":
            await ostat_char(ctx, char, mode)
        elif char != "all" and user != "all":
            await ostat_user_char(ctx, user, char, mode)

    @commands.command(name="orank", help="Get a ranking of all players offensively")
    async def o_rank(self, ctx, mode="off"):
        mode = ladders.get_web_mode(mode)
        await ostat_char(ctx, "all", mode)

    @commands.command(name="pstat", help="Look up player pitching stats on Project Rio")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def p_stat(self, ctx, user="all", char="all", mode=ladders.STARS_OFF_MODE):
        mode = ladders.get_web_mode(mode)
        if char.lower() in characters.aliases:
            char = characters.mappings[characters.aliases[char.lower()]]
        if char == "all" and user == "all":
            await pstat_all(ctx, mode)
        elif char == "all" and user != "all":
            await pstat_user(ctx, user, mode)
        elif char != "all" and user == "all":
            await pstat_char(ctx, char, mode)
        elif char != "all" and user != "all":
            await pstat_user_char(ctx, user, char, mode)

    @commands.command(name="prank", help="Get a ranking of all players defensively")
    async def p_rank(self, ctx, mode="off"):
        mode = ladders.get_web_mode(mode)
        await pstat_char(ctx, "all", mode)


async def setup(client):
    await client.add_cog(WebStatLookup(client))
