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
        # if char == "all" and user == "all":
        #     await pstat_all(ctx, mode)
        # elif char == "all" and user != "all":
        #     await pstat_user(ctx, user, mode)
        # elif char != "all" and user == "all":
        #     await pstat_char(ctx, char, mode)
        # elif char != "all" and user != "all":
        #     await pstat_user_char(ctx, user, char, mode)
        url = "https://api.projectrio.app/stats/?exclude_batting=1&exclude_fielding=1&exclude_misc=1&tag=" + mode
        all_url = url

        if char != "all":
            url += "&char_id=" + str(characters.reverse_mappings[char])
            if user != "all":
                all_url = url

        if user != "all":
            url += "&username=" + user

        all_response = requests.get(all_url).json()
        response = requests.get(url).json()

        stats = response["Stats"]["Pitching"]

        # batter avg vs pitcher
        d_avg = stats["hits_allowed"] / (stats["batters_faced"] - stats["walks_bb"] - stats["walks_hbp"])
        era = 9 * stats["runs_allowed"] / (stats["outs_pitched"] / 3)
        # strikeout percentage
        kp = (stats["strikeouts_pitched"] / stats["batters_faced"]) * 100

        ip = stats["outs_pitched"] // 3
        ip_str = str(ip + (0.1 * (stats["outs_pitched"] % 3)))

        overall = all_response["Stats"]["Pitching"]
        overall_era = 9 * overall["runs_allowed"] / (overall["outs_pitched"] / 3)
        # character ERA-
        cera_minus = (era / overall_era) * 100

        char_or_all = " cERA-"
        if char == "all" or user == "all":
            char_or_all = " ERA-"

        embed = discord.Embed(title=user + " - " + char + " (" + ip_str + " IP)",
                              description="opp. AVG: " + "{:.3f}".format(d_avg) + "\nERA: " + "{:.2f}".format(era) +
                                          "\nK%: " + "{:.1f}".format(kp) + "\n" + char_or_all + ": " + str(
                                  round(cera_minus)))

        embed.set_thumbnail(url=characters.images[char])

        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(WebStatLookup(client))
