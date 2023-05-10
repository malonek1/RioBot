import discord
import requests
from json import JSONDecodeError
from resources import characters

BASE_WEB_URL = "https://api.projectrio.app/stats/"


async def ostat_user_char(ctx, user: str, char: str, mode: str):
    try:
        char_id = characters.reverse_mappings[char]
        all_url = f"{BASE_WEB_URL}?exclude_pitching=1&exclude_fielding=1&tag={mode}&char_id={char_id}&by_char=1"
        url = f"{all_url}&username={user}"
        response = requests.get(url).json()
        all_response = requests.get(all_url).json()
        stats = response.get("Stats", {}).get(char, {}).get("Batting", {})
    except (JSONDecodeError, KeyError):
        embed = discord.Embed(
            title=f"There are no stats for user {user} with character {char} in {mode} or the user/character alias was not found.",
            color=0xEA7D07)
        await ctx.send(embed=embed)
        return

    pa, avg, obp, slg = calc_slash_line(stats)
    ops = obp + slg

    all_stats = all_response.get("Stats", {}).get(char, {}).get("Batting", {})
    overall_pa, overall_avg, overall_obp, overall_slg = calc_slash_line(all_stats)
    ops_plus = ((obp / overall_obp) + (slg / overall_slg) - 1) * 100 if overall_obp > 0 and overall_slg > 0 else -100

    misc = response.get("Stats", {}).get(char, {}).get("Misc", {})
    games = misc["home_wins"] + misc["away_wins"] + misc["home_loses"] + misc["away_loses"]
    winrate = (misc["home_wins"] + misc["away_wins"]) / games if games > 0 else 0

    embed = discord.Embed(title=f"{user} - {char} ({pa} PA)")
    fields = [("G", str(games)),
              ("Win%", "{:.1f}".format(winrate * 100)),
              ("AB", str(stats["summary_at_bats"])),
              ("H", str(stats["summary_hits"])),
              ("2B", str(stats["summary_doubles"])),
              ("3B", str(stats["summary_triples"])),
              ("HR", str(stats["summary_homeruns"])),
              ("RBI", str(stats["summary_rbi"])),
              ("\u200b", "\u200b"),
              ("SO", str(stats["summary_strikeouts"])),
              ("BB", str(stats["summary_walks_bb"] + stats["summary_walks_hbp"])),
              ("\u200b", "\u200b"),
              ("AVG", "{:.3f}".format(avg)),
              ("OBP", "{:.3f}".format(obp)),
              ("SLG", "{:.3f}".format(slg)),
              ("OPS", "{:.3f}".format(ops)),
              ("cOPS+", str(round(ops_plus))),
              ("\u200b", "\u200b")]

    for name, value in fields:
        embed.add_field(name=name, value=value, inline=True)

    embed.set_thumbnail(url=characters.images[char])

    await ctx.send(embed=embed)


async def ostat_user(ctx, user: str, mode: str):
    all_url = f"{BASE_WEB_URL}?exclude_pitching=1&exclude_fielding=1&exclude_misc=1&tag={mode}"
    user_url = f"{all_url}&username={user}"
    all_by_char_url = f"{all_url}&by_char=1"
    user_by_char_url = f"{all_by_char_url}&username={user}"
    try:
        user_response = requests.get(user_url).json()
        user_by_char_response = requests.get(user_by_char_url).json()
        all_response = requests.get(all_url).json()
        all_by_char_response = requests.get(all_by_char_url).json()
    except JSONDecodeError:
        embed = discord.Embed(
            title=f"There are no stats for user {user} in {mode} or the username was not found.",
            color=0xEA7D07)
        await ctx.send(embed=embed)
        return

    all_dict = {"all": all_response["Stats"]["Batting"]}
    for char in all_by_char_response["Stats"]:
        all_dict[char] = all_by_char_response["Stats"][char]["Batting"]

    user_dict = {"all": user_response["Stats"]["Batting"]}
    for char in user_by_char_response["Stats"]:
        user_dict[char] = user_by_char_response["Stats"][char]["Batting"]

    user_stats = user_dict["all"]
    pa, avg, obp, slg = calc_slash_line(user_stats)

    all_stats = all_dict["all"]
    overall_pa, overall_avg, overall_obp, overall_slg = calc_slash_line(all_stats)
    if overall_obp > 0 and overall_slg > 0:
        ops_plus = ((obp / overall_obp) + (slg / overall_slg) - 1) * 100
    else:
        ops_plus = -100
    title = f"\n{user} ({pa} PA): {avg:.3f} / {obp:.3f} / {slg:.3f}, {round(ops_plus)} OPS+"

    desc = "**Char** (PA): AVG / OBP / SLG, cOPS+"

    del user_dict["all"]
    try:
        sorted_char_list = sorted(user_dict.keys(), key=lambda x: user_dict[x]["summary_at_bats"] + user_dict[x]["summary_walks_bb"] +
                                                                  user_dict[x]["summary_walks_hbp"] + user_dict[x]["summary_sac_flys"], reverse=True)
    except KeyError:
        print("There was an error sorting the character list")
        sorted_char_list = sorted(user_dict.keys())

    for char in sorted_char_list:
        char_stats = user_dict[char]
        pa, avg, obp, slg = calc_slash_line(char_stats)
        all_stats = all_dict[char]
        overall_pa, overall_avg, overall_obp, overall_slg = calc_slash_line(all_stats)
        if overall_obp > 0 and overall_slg > 0:
            ops_plus = ((obp / overall_obp) + (slg / overall_slg) - 1) * 100
        else:
            ops_plus = -100
        desc += f'\n**{char}** ({pa} PA): {avg:.3f} / {obp:.3f} / {slg:.3f}, {round(ops_plus)} cOPS+'

    embed = discord.Embed(title=title, description=desc)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    embed.set_thumbnail(url=characters.images["all"])

    await ctx.send(embed=embed)


async def ostat_char(ctx, char: str, mode: str):
    try:
        all_url = f"{BASE_WEB_URL}?exclude_pitching=1&exclude_fielding=1&exclude_misc=1&tag={mode}"
        if char != "all":
            char_url = f"{all_url}&char_id={str(characters.reverse_mappings[char])}"
            char_by_user_url = f"{all_url}&by_user=1&char_id={str(characters.reverse_mappings[char])}"
        else:
            char_url = all_url
            char_by_user_url = all_url + "&by_user=1"

        char_response = requests.get(char_url).json()
        char_by_user_response = requests.get(char_by_user_url).json()
    except (JSONDecodeError, KeyError):
        embed = discord.Embed(
            title=f"There are no stats for character {char} in {mode} or the character alias was not found.",
            color=0xEA7D07)
        await ctx.send(embed=embed)
        return

    user_list = [("all", char_response["Stats"]["Batting"])]

    for user, stats in char_by_user_response["Stats"].items():
        user_list.append((user, stats["Batting"]))

    char_stats = user_list[0][1]
    pa, avg, obp, slg = calc_slash_line(char_stats)

    title = f"\n{char} ({pa} PA): {avg:.3f} / {obp:.3f} / {slg:.3f}"
    desc = "**User** (PA): AVG / OBP / SLG, cOPS+"

    output_list = []
    for user, user_stats in user_list[1:]:
        user_pa, user_avg, user_obp, user_slg = calc_slash_line(user_stats)
        if obp > 0 and slg > 0:
            ops_plus = ((user_obp / obp) + (user_slg / slg) - 1) * 100
        else:
            ops_plus = 0

        if user_pa > (pa / 200):
            output_list.append((user, user_pa, user_avg, user_obp, user_slg, ops_plus))

    sorted_user_list = sorted(output_list, key=lambda x: x[5], reverse=True)

    for index, user_stats in zip(range(20), sorted_user_list):
        user = user_stats[0]
        user_pa = user_stats[1]
        user_avg = user_stats[2]
        user_obp = user_stats[3]
        user_slg = user_stats[4]
        ops_plus = user_stats[5]
        desc += f"\n**{index + 1}. {user}** ({user_pa} PA): {user_avg:.3f} / {user_obp:.3f} / {user_slg:.3f}, {round(ops_plus)} cOPS+"

    embed = discord.Embed(title=title, description=desc)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    embed.set_thumbnail(url=characters.images[char])

    await ctx.send(embed=embed)


async def ostat_all(ctx, mode: str):
    all_url = BASE_WEB_URL + "?exclude_pitching=1&exclude_fielding=1&exclude_misc=1&tag=" + mode
    all_by_char_url = all_url + "&by_char=1"

    all_response = requests.get(all_url).json()
    all_by_char_response = requests.get(all_by_char_url).json()

    all_dict = {"all": all_response["Stats"]["Batting"]}
    for char in all_by_char_response["Stats"]:
        all_dict[char] = all_by_char_response["Stats"][char]["Batting"]

    all_stats = all_dict["all"]
    all_pa, all_avg, all_obp, all_slg = calc_slash_line(all_stats)
    desc = "**Char** (PA): AVG / OBP / SLG, OPS+"
    title = f"\nAll ({all_pa} PA): {all_avg:.3f} / {all_obp:.3f} / {all_slg:.3f}"

    del all_dict["all"]

    try:
        sorted_char_list = sorted(all_dict.keys(),
                                  key=lambda x: all_dict[x]["summary_at_bats"] + all_dict[x]["summary_walks_bb"] +
                                                all_dict[x]["summary_walks_hbp"] + all_dict[x]["summary_sac_flys"], reverse=True)
    except KeyError:
        print("There was an error sorting the character list")
        sorted_char_list = sorted(all_dict.keys())

    for char in sorted_char_list:
        char_stats = all_dict[char]
        pa, avg, obp, slg = calc_slash_line(char_stats)

        ops_plus = ((obp / all_obp) + (slg / all_slg) - 1) * 100

        desc += f"\n**{char}** ({pa} PA): {avg:.3f} / {obp:.3f} / {slg:.3f}, {round(ops_plus)} OPS+"

    embed = discord.Embed(title=title, description=desc)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    embed.set_thumbnail(url=characters.images["all"])

    await ctx.send(embed=embed)


def calc_slash_line(raw_dict):
    pa = sum(raw_dict.get(key, 0) for key in ["summary_at_bats", "summary_walks_bb", "summary_walks_hbp", "summary_sac_flys"])
    avg = raw_dict["summary_hits"] / raw_dict["summary_at_bats"] if raw_dict["summary_at_bats"] > 0 else 0
    obp = (raw_dict["summary_hits"] + raw_dict["summary_walks_hbp"] + raw_dict["summary_walks_bb"]) / pa if pa > 0 else 0
    slg = (raw_dict["summary_singles"] + (raw_dict["summary_doubles"] * 2) + (
            raw_dict["summary_triples"] * 3) + (raw_dict["summary_homeruns"] * 4)) / raw_dict["summary_at_bats"] if raw_dict["summary_at_bats"] > 0 else 0
    return pa, avg, obp, slg
