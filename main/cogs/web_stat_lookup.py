import discord
from discord.ext import commands

from helpers.offensive_stat_calcs import ostat_user_char, ostat_user, ostat_char, ostat_all
from helpers.pitching_stat_calcs import pstat_user_char, pstat_user, pstat_char, pstat_all
from resources import ladders, characters

class WebStatLookup(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def _dispatch_stat(self, ctx, user, char, mode, user_char_fn, user_fn, char_fn, all_fn):
        mode = ladders.get_web_mode(mode)
        if char.lower() in characters.aliases:
            char = characters.mappings[characters.aliases[char.lower()]]
        session = self.client.session
        if char == "all" and user == "all":
            await all_fn(ctx, mode, session)
        elif char == "all":
            await user_fn(ctx, user, mode, session)
        elif user == "all":
            await char_fn(ctx, char, mode, session)
        else:
            await user_char_fn(ctx, user, char, mode, session)

    @commands.command(name="ostat", help="Look up player batting stats on Project Rio")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def o_stat(self, ctx, user="all", char="all", mode=ladders.STARS_OFF_MODE):
        await self._dispatch_stat(ctx, user, char, mode, ostat_user_char, ostat_user, ostat_char, ostat_all)

    @commands.command(name="orank", help="Get a ranking of all players offensively")
    async def o_rank(self, ctx, mode="off"):
        mode = ladders.get_web_mode(mode)
        await ostat_char(ctx, "all", mode, self.client.session)

    @commands.command(name="pstat", help="Look up player pitching stats on Project Rio")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def p_stat(self, ctx, user="all", char="all", mode=ladders.STARS_OFF_MODE):
        await self._dispatch_stat(ctx, user, char, mode, pstat_user_char, pstat_user, pstat_char, pstat_all)

    @commands.command(name="prank", help="Get a ranking of all players defensively")
    async def p_rank(self, ctx, mode="off"):
        mode = ladders.get_web_mode(mode)
        await pstat_char(ctx, "all", mode, self.client.session)


async def setup(client):
    await client.add_cog(WebStatLookup(client))
