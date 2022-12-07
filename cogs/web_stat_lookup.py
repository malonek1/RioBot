import itertools

import discord
import requests
from discord.ext import commands

from resources import characters

BASE_WEB_URL = "https://api.projectrio.app/detailed_stats/"


async def ostat_user_char(ctx, user: str, char: str):
    all_url = BASE_WEB_URL + "?exclude_pitching=1&exclude_fielding=1&tag=Normal&tag=Ranked&char_id=" + str(
        characters.reverse_mappings[char])
    url = all_url + "&username=" + user

    all_response = requests.get(all_url).json()
    response = requests.get(url).json()

    stats = response["Stats"]["Batting"]
    pa = stats["summary_at_bats"] + stats["summary_walks_bb"] + stats["summary_walks_hbp"] + stats[
        "summary_sac_flys"]
    avg = stats["summary_hits"] / stats["summary_at_bats"]
    obp = (stats["summary_hits"] + stats["summary_walks_hbp"] + stats["summary_walks_bb"]) / pa
    slg = (stats["summary_singles"] + (stats["summary_doubles"] * 2) + (stats["summary_triples"] * 3) + (
            stats["summary_homeruns"] * 4)) / stats["summary_at_bats"]
    ops = obp + slg
    # pa = stats["plate_appearances"]

    overall = all_response["Stats"]["Batting"]
    overall_pa = overall["summary_at_bats"] + overall["summary_walks_bb"] + overall["summary_walks_hbp"] + \
                 overall["summary_sac_flys"]
    overall_obp = (overall["summary_hits"] + overall["summary_walks_hbp"] + overall[
        "summary_walks_bb"]) / overall_pa
    overall_slg = (overall["summary_singles"] + (overall["summary_doubles"] * 2) + (
            overall["summary_triples"] * 3) + (
                           overall["summary_homeruns"] * 4)) / overall["summary_at_bats"]

    ops_plus = ((obp / overall_obp) + (slg / overall_slg) - 1) * 100

    misc = response["Stats"]["Misc"]
    winrate = (misc["home_wins"] + misc["away_wins"]) / (
            misc["home_wins"] + misc["away_wins"] + misc["home_loses"] + misc["away_loses"])

    embed = discord.Embed(title=user + " - " + char + " (" + str(pa) + " PA)")
    embed.add_field(name="G", value=str(misc["game_appearances"]), inline=True)
    embed.add_field(name="Win%", value="{:.1f}".format(winrate * 100), inline=True)
    embed.add_field(name="AB", value=str(stats["summary_at_bats"]), inline=True)
    embed.add_field(name="H", value=str(stats["summary_hits"]), inline=True)
    embed.add_field(name="2B", value=str(stats["summary_doubles"]), inline=True)
    embed.add_field(name="3B", value=str(stats["summary_triples"]), inline=True)
    embed.add_field(name="HR", value=str(stats["summary_homeruns"]), inline=True)
    embed.add_field(name="RBI", value=str(stats["summary_rbi"]), inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)
    embed.add_field(name="SO", value=str(stats["summary_strikeouts"]), inline=True)
    embed.add_field(name="BB", value=str(stats["summary_walks_bb"] + stats["summary_walks_hbp"]), inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)
    embed.add_field(name="AVG", value="{:.3f}".format(avg), inline=True)
    embed.add_field(name="OBP", value="{:.3f}".format(obp), inline=True)
    embed.add_field(name="SLG", value="{:.3f}".format(slg), inline=True)
    embed.add_field(name="OPS", value="{:.3f}".format(ops), inline=True)
    embed.add_field(name="cOPS+", value=str(round(ops_plus)), inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)

    embed.set_thumbnail(url=characters.images[char])

    await ctx.send(embed=embed)


async def ostat_user(ctx, user: str):
    all_url = BASE_WEB_URL + "?exclude_pitching=1&exclude_fielding=1&exclude_misc=1&tag=Normal&tag=Ranked"
    user_url = all_url + "&username=" + user
    all_by_char_url = all_url + "&by_char=1"
    user_by_char_url = all_by_char_url + "&username=" + user

    all_response = requests.get(all_url).json()
    user_response = requests.get(user_url).json()
    all_by_char_response = requests.get(all_by_char_url).json()
    user_by_char_response = requests.get(user_by_char_url).json()

    all_dict = {"all": all_response["Stats"]["Batting"]}
    for char in all_by_char_response["Stats"]:
        all_dict[char] = all_by_char_response["Stats"][char]["Batting"]

    user_dict = {"all": user_response["Stats"]["Batting"]}
    for char in user_by_char_response["Stats"]:
        user_dict[char] = user_by_char_response["Stats"][char]["Batting"]

    user_stats = user_dict["all"]
    pa = user_stats["summary_at_bats"] + user_stats["summary_walks_hbp"] + user_stats[
        "summary_walks_bb"] + user_stats["summary_sac_flys"]
    # TODO: pa = user_stats["plate_appearances"]
    avg = user_stats["summary_hits"] / user_stats["summary_at_bats"]
    obp = (user_stats["summary_hits"] + user_stats["summary_walks_hbp"] + user_stats[
        "summary_walks_bb"]) / pa
    slg = (user_stats["summary_singles"] + (user_stats["summary_doubles"] * 2) + (
            user_stats["summary_triples"] * 3) + (
                   user_stats["summary_homeruns"] * 4)) / user_stats["summary_at_bats"]

    all_stats = all_dict["all"]
    overall_pa = all_stats["summary_at_bats"] + all_stats["summary_walks_hbp"] + all_stats["summary_walks_bb"] + \
                 all_stats[
                     "summary_sac_flys"]
    overall_obp = (all_stats["summary_hits"] + all_stats["summary_walks_hbp"] + all_stats[
        "summary_walks_bb"]) / overall_pa
    overall_slg = (all_stats["summary_singles"] + (all_stats["summary_doubles"] * 2) + (
            all_stats["summary_triples"] * 3) + (
                           all_stats["summary_homeruns"] * 4)) / all_stats["summary_at_bats"]
    ops_plus = ((obp / overall_obp) + (slg / overall_slg) - 1) * 100
    desc = "**Char** (PA): AVG / OBP / SLG, cOPS+"
    title = "\n" + user + " (" + str(pa) + " PA): " + "{:.3f}".format(avg) + " / " + "{:.3f}".format(
        obp) + " / " + "{:.3f}".format(slg) + ", " + str(ops_plus) + " OPS+"

    del user_dict["all"]
    try:
        sorted_char_list = sorted(user_dict.keys(), key=lambda x: user_dict[x]["plate_appearances"], reverse=True)
    except KeyError:
        print("There was an error sorting the character list")
        sorted_char_list = sorted(user_dict.keys())

    for char in sorted_char_list:
        char_stats = user_dict[char]
        if char_stats["summary_at_bats"] > 0 and char_stats["plate_appearances"] > 0:
            pa = char_stats["summary_at_bats"] + char_stats["summary_walks_hbp"] + char_stats["summary_walks_bb"] + \
                 char_stats["summary_sac_flys"]
            avg = char_stats["summary_hits"] / char_stats["summary_at_bats"]
            obp = (char_stats["summary_hits"] + char_stats["summary_walks_hbp"] + char_stats["summary_walks_bb"]) / pa
            slg = (char_stats["summary_singles"] + (char_stats["summary_doubles"] * 2) + (
                    char_stats["summary_triples"] * 3) + (char_stats["summary_homeruns"] * 4)) / char_stats[
                      "summary_at_bats"]

            all_stats = all_dict[char]
            overall_pa = all_stats["summary_at_bats"] + all_stats["summary_walks_hbp"] + all_stats["summary_walks_bb"] + \
                         all_stats["summary_sac_flys"]
            overall_obp = (all_stats["summary_hits"] + all_stats["summary_walks_hbp"] + all_stats[
                "summary_walks_bb"]) / overall_pa
            overall_slg = (all_stats["summary_singles"] + (all_stats["summary_doubles"] * 2) + (
                    all_stats["summary_triples"] * 3) + (all_stats["summary_homeruns"] * 4)) / all_stats[
                              "summary_at_bats"]
            ops_plus = ((obp / overall_obp) + (slg / overall_slg) - 1) * 100
            desc += "\n**" + char + "** (" + str(pa) + " PA): " + "{:.3f}".format(avg) + " / " + "{:.3f}".format(
                obp) + " / " + "{:.3f}".format(slg) + ", " + str(
                round(ops_plus)) + " cOPS+"

    embed = discord.Embed(title=title, description=desc)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    embed.set_thumbnail(url=characters.images["all"])

    await ctx.send(embed=embed)


async def ostat_char(ctx, char: str):
    all_url = BASE_WEB_URL + "?exclude_pitching=1&exclude_fielding=1&exclude_misc=1&tag=Normal&tag=Ranked"
    char_url = all_url + "&char_id=" + str(characters.reverse_mappings[char])
    char_by_user_url = all_url + "&by_user=1" + "&char_id=" + str(characters.reverse_mappings[char])

    char_response = requests.get(char_url).json()
    char_by_user_response = requests.get(char_by_user_url).json()

    user_dict = {"all": char_response["Stats"]["Batting"]}

    for user in char_by_user_response["Stats"]:
        user_dict[user] = char_by_user_response["Stats"][user]["Batting"]

    char_stats = user_dict["all"]
    pa = char_stats["summary_at_bats"] + char_stats["summary_walks_hbp"] + char_stats[
        "summary_walks_bb"] + char_stats["summary_sac_flys"]
    # TODO: pa = user_stats["plate_appearances"]
    avg = char_stats["summary_hits"] / char_stats["summary_at_bats"]
    obp = (char_stats["summary_hits"] + char_stats["summary_walks_hbp"] + char_stats[
        "summary_walks_bb"]) / pa
    slg = (char_stats["summary_singles"] + (char_stats["summary_doubles"] * 2) + (
            char_stats["summary_triples"] * 3) + (
                   char_stats["summary_homeruns"] * 4)) / char_stats["summary_at_bats"]

    desc = "**User** (PA): AVG / OBP / SLG, cOPS+"
    title = "\n" + char + " (" + str(pa) + " PA): " + "{:.3f}".format(avg) + " / " + "{:.3f}".format(
        obp) + " / " + "{:.3f}".format(slg)

    del user_dict["all"]

    output_dict = {}
    for user in user_dict:
        user_stats = user_dict[user]
        if user_stats["summary_at_bats"] > 0 and user_stats["plate_appearances"] > 0:
            user_pa = user_stats["summary_at_bats"] + user_stats["summary_walks_hbp"] + user_stats["summary_walks_bb"] + \
                      user_stats["summary_sac_flys"]
            user_avg = user_stats["summary_hits"] / user_stats["summary_at_bats"]
            user_obp = (user_stats["summary_hits"] + user_stats["summary_walks_hbp"] + user_stats[
                "summary_walks_bb"]) / user_pa
            user_slg = (user_stats["summary_singles"] + (user_stats["summary_doubles"] * 2) + (
                    user_stats["summary_triples"] * 3) + (user_stats["summary_homeruns"] * 4)) / user_stats[
                           "summary_at_bats"]

            ops_plus = ((user_obp / obp) + (user_slg / slg) - 1) * 100

            if user_pa > (pa / 200) and user != "GenericHomeUser" and user != "GenericAwayUser":
                output_dict[user] = (user_pa, user_avg, user_obp, user_slg, ops_plus)

    sorted_user_list = sorted(output_dict.keys(), key=lambda x: output_dict[x][4], reverse=True)

    for index, user in zip(range(20), sorted_user_list):
        user_pa = output_dict[user][0]
        user_avg = output_dict[user][1]
        user_obp = output_dict[user][2]
        user_slg = output_dict[user][3]
        ops_plus = output_dict[user][4]
        desc += "\n**" + str(index + 1) + ". " + user + "** (" + str(user_pa) + " PA): " + "{:.3f}".format(
            user_avg) + " / " + "{:.3f}".format(
            user_obp) + " / " + "{:.3f}".format(user_slg) + ", " + str(round(ops_plus)) + " cOPS+"

    embed = discord.Embed(title=title, description=desc)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    embed.set_thumbnail(url=characters.images[char])

    await ctx.send(embed=embed)


async def ostat_all(ctx):
    all_url = BASE_WEB_URL + "?exclude_pitching=1&exclude_fielding=1&exclude_misc=1&tag=Normal&tag=Ranked"
    all_by_char_url = all_url + "&by_char=1"

    all_response = requests.get(all_url).json()
    all_by_char_response = requests.get(all_by_char_url).json()

    all_dict = {"all": all_response["Stats"]["Batting"]}
    for char in all_by_char_response["Stats"]:
        all_dict[char] = all_by_char_response["Stats"][char]["Batting"]

    all_stats = all_dict["all"]
    all_pa = all_stats["summary_at_bats"] + all_stats["summary_walks_hbp"] + all_stats[
        "summary_walks_bb"] + all_stats["summary_sac_flys"]
    all_avg = all_stats["summary_hits"] / all_stats["summary_at_bats"]
    all_obp = (all_stats["summary_hits"] + all_stats["summary_walks_hbp"] + all_stats["summary_walks_bb"]) / all_pa
    all_slg = (all_stats["summary_singles"] + (all_stats["summary_doubles"] * 2) + (
            all_stats["summary_triples"] * 3) + (all_stats["summary_homeruns"] * 4)) / all_stats["summary_at_bats"]
    # TODO: pa = user_dict["all"]["plate_appearances"]
    desc = "**Char** (PA): AVG / OBP / SLG, OPS+"
    title = "\nAll (" + str(all_pa) + " PA): " + "{:.3f}".format(all_avg) + " / " + "{:.3f}".format(
        all_obp) + " / " + "{:.3f}".format(all_slg)

    del all_dict["all"]

    try:
        sorted_char_list = sorted(all_dict.keys(), key=lambda x: all_dict[x]["plate_appearances"], reverse=True)
    except KeyError:
        print("There was an error sorting the character list")
        sorted_char_list = sorted(all_dict.keys())

    for char in sorted_char_list:
        char_stats = all_dict[char]
        # TODO: pa = user_dict["all"]["plate_appearances"]
        pa = char_stats["summary_at_bats"] + char_stats["summary_walks_hbp"] + char_stats[
            "summary_walks_bb"] + char_stats["summary_sac_flys"]
        avg = char_stats["summary_hits"] / char_stats["summary_at_bats"]
        obp = (char_stats["summary_hits"] + char_stats["summary_walks_hbp"] + char_stats["summary_walks_bb"]) / pa
        slg = (char_stats["summary_singles"] + (char_stats["summary_doubles"] * 2) + (
                char_stats["summary_triples"] * 3) + (char_stats["summary_homeruns"] * 4)) / char_stats[
                  "summary_at_bats"]

        ops_plus = ((obp / all_obp) + (slg / all_slg) - 1) * 100

        desc += "\n**" + char + "** (" + str(pa) + " PA): " + "{:.3f}".format(avg) + " / " + "{:.3f}".format(
            obp) + " / " + "{:.3f}".format(slg) + ", " + str(round(ops_plus)) + " OPS+"

    embed = discord.Embed(title=title, description=desc)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    embed.set_thumbnail(url=characters.images["all"])

    await ctx.send(embed=embed)


class WebStatLookup(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="ostat", help="Look up player batting stats on Project Rio")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def o_stat(self, ctx, user="all", char="all"):
        if char.lower() in characters.aliases:
            char = characters.mappings[characters.aliases[char.lower()]]
        if char == "all" and user == "all":
            await ostat_all(ctx)
        elif char == "all" and user != "all":
            await ostat_user(ctx, user)
        elif char != "all" and user == "all":
            await ostat_char(ctx, char)
        elif char != "all" and user != "all":
            await ostat_user_char(ctx, user, char)

    @commands.command(name="pstat", help="Look up player pitching stats on Project Rio")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def p_stat(self, ctx, user="all", char="all"):
        url = "https://api.projectrio.app/detailed_stats/?exclude_batting=1&exclude_fielding=1&exclude_misc=1&tag=Normal&tag=Ranked"
        all_url = url

        if char.lower() in characters.aliases:
            char = characters.mappings[characters.aliases[char.lower()]]
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
