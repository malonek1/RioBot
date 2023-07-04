import discord
import requests
from json import JSONDecodeError
from resources import characters

BASE_WEB_URL = "https://api.projectrio.app/stats/"

all_stats = {}
all_by_char_stats = {}


async def pstat_user_char(ctx, user: str, char: str, mode: str):
    global all_by_char_stats
    try:
        all_by_char_url = f"{BASE_WEB_URL}?exclude_batting=1&exclude_fielding=1&tag={mode}&by_char=1"
        char_id = characters.reverse_mappings[char]
        url = f"{BASE_WEB_URL}?exclude_batting=1&exclude_fielding=1&tag={mode}&char_id={char_id}&by_char=1&username={user}"
        response = requests.get(url).json()
        if not all_by_char_stats.get(mode, {}).get("Pitching", {}):
            all_by_char_stats[mode] = requests.get(all_by_char_url).json()["Stats"]
        stats = response.get("Stats", {}).get(char, {}).get("Pitching", {})
    except (JSONDecodeError, KeyError):
        embed = discord.Embed(
            title=f"There are no stats for user {user} with character {char} in {mode} or the user/character alias was not found.",
            color=0xEA7D07)
        await ctx.send(embed=embed)
        return

    ip, avg, k_rate, era = calc_slash_line(stats)

    all_char_stats = all_by_char_stats.get(mode, {}).get(char, {}).get("Pitching", {})
    overall_ip, overall_avg, overall_k_rate, overall_era = calc_slash_line(all_char_stats)
    era_minus = ((era / overall_era) * 100) if overall_era > 0 and overall_ip > 0 else 200

    misc = response.get("Stats", {}).get(char, {}).get("Misc", {})
    games = misc["home_wins"] + misc["away_wins"] + misc["home_loses"] + misc["away_loses"]
    winrate = (misc["home_wins"] + misc["away_wins"]) / games if games > 0 else 0

    embed = discord.Embed(title=f"{user} - {char} ({ip:.1f} IP)")
    fields = [("G", str(games)),
              ("Win%", "{:.1f}".format(winrate * 100)),
              ("Batters Faced", str(stats["batters_faced"])),
              ("Hits Allowed", str(stats["hits_allowed"])),
              ("IP", str(round(stats["outs_pitched"] / 3, 1))),
              ("Runs Allowed", str(stats["runs_allowed"])),
              ("\u200b", "\u200b"),
              ("K", str(stats["strikeouts_pitched"])),
              ("BB", str(stats["walks_bb"] + stats["walks_hbp"])),
              ("\u200b", "\u200b"),
              ("Opp. AVG", "{:.3f}".format(avg)),
              ("K%", "{:.1%}".format(k_rate)),
              ("ERA", "{:.2f}".format(era)),
              ("ERA-", str(round(era_minus))),
              ("\u200b", "\u200b")]

    for name, value in fields:
        embed.add_field(name=name, value=value, inline=True)

    embed.set_thumbnail(url=characters.images[char])

    await ctx.send(embed=embed)


async def pstat_user(ctx, user: str, mode: str):
    global all_stats, all_by_char_stats
    all_url = f"{BASE_WEB_URL}?exclude_batting=1&exclude_fielding=1&exclude_misc=1&tag={mode}"
    user_url = f"{all_url}&username={user}"
    all_by_char_url = f"{all_url}&by_char=1"
    user_by_char_url = f"{all_by_char_url}&username={user}"
    try:
        if not all_stats.get(mode, {}).get("Pitching", {}):
            print("getting all stats")
            all_stats[mode] = requests.get(all_url).json()["Stats"]
        if not all_by_char_stats.get(mode, {}):
            print("Getting all by char stats")
            all_by_char_stats[mode] = requests.get(all_by_char_url).json()["Stats"]
        user_response = requests.get(user_url).json()
        user_by_char_response = requests.get(user_by_char_url).json()
    except JSONDecodeError:
        embed = discord.Embed(
            title=f"There are no stats for user {user} in {mode} or the username was not found.",
            color=0xEA7D07)
        await ctx.send(embed=embed)
        return

    user_dict = {"all": user_response["Stats"]["Pitching"]}
    for char in user_by_char_response["Stats"]:
        user_dict[char] = user_by_char_response["Stats"][char]["Pitching"]

    user_stats = user_dict["all"]
    ip, avg, k_rate, era = calc_slash_line(user_stats)

    overall_ip, overall_avg, overall_k_rate, overall_era = calc_slash_line(all_stats[mode]["Pitching"])
    if overall_era > 0 and overall_ip > 0:
        era_minus = (era / overall_era) * 100
    else:
        era_minus = 200
    title = f"\n{user} ({ip:.1f} IP): {avg:.3f} / {k_rate:.1%} / {era:.2f} ERA, {round(era_minus)} ERA-"

    desc = "**Char** (IP): Opp. AVG / K% / ERA, cERA-"

    del user_dict["all"]
    try:
        sorted_char_list = sorted(user_dict.keys(),
                                  key=lambda x: user_dict[x]["outs_pitched"],
                                  reverse=True)
    except KeyError:
        print("There was an error sorting the character list")
        sorted_char_list = sorted(user_dict.keys())

    for char in sorted_char_list:
        char_stats = user_dict[char]
        ip, avg, k_rate, era = calc_slash_line(char_stats)
        all_char_stats = all_by_char_stats[mode][char]["Pitching"]
        overall_ip, overall_avg, overall_k_rate, overall_era = calc_slash_line(all_char_stats)
        if overall_ip > 0 and overall_era > 0:
            era_minus = (era / overall_era) * 100
        else:
            era_minus = 200
        if char_stats['batters_faced'] > 0 and char_stats['outs_pitched'] > 3:

            desc += f'\n**{char}** ({ip:.1f} IP): {avg:.3f} Opp. AVG / {k_rate:.1%} K% / {era:.2f} ERA, {round(era_minus)} cERA-'

    embed = discord.Embed(title=title, description=desc)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    embed.set_thumbnail(url=characters.images["all"])

    await ctx.send(embed=embed)


async def pstat_char(ctx, char: str, mode: str):
    try:
        all_url = f"{BASE_WEB_URL}?exclude_batting=1&exclude_fielding=1&exclude_misc=1&tag={mode}"
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

    user_list = [("all", char_response["Stats"]["Pitching"])]

    for user, stats in char_by_user_response["Stats"].items():
        user_list.append((user, stats["Pitching"]))

    char_stats = user_list[0][1]
    ip, avg, k_rate, era = calc_slash_line(char_stats)

    title = f"\n{char} ({ip:.1f} IP): {avg:.3f} Opp. AVG / {k_rate:.1%} K% / {era:.2f} ERA"
    desc = "**User** (IP): Opp. AVG / K% / ERA, ERA-"

    output_list = []
    for user, user_stats in user_list[1:]:
        user_ip, user_avg, user_k_rate, user_era = calc_slash_line(user_stats)
        if ip > 0 and era > 0:
            era_minus = (user_era / era) * 100
        else:
            era_minus = 200

        if user_ip > (ip / 200):
            output_list.append((user, user_ip, user_avg, user_k_rate, user_era, era_minus))

    sorted_user_list = sorted(output_list, key=lambda x: x[5], reverse=False)

    for index, user_stats in zip(range(20), sorted_user_list):
        user = user_stats[0]
        user_ip = user_stats[1]
        user_avg = user_stats[2]
        user_k_rate = user_stats[3]
        user_era = user_stats[4]
        era_minus = user_stats[5]
        desc += f"\n**{index + 1}. {user}** ({user_ip:.1f} IP): {user_avg:.3f} / {user_k_rate:.1%} / {user_era:.2f} ERA, {round(era_minus)} ERA-"

    embed = discord.Embed(title=title, description=desc)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    embed.set_thumbnail(url=characters.images[char])

    await ctx.send(embed=embed)


async def pstat_all(ctx, mode: str):
    global all_stats, all_by_char_stats
    all_url = BASE_WEB_URL + "?exclude_batting=1&exclude_fielding=1&exclude_misc=1&tag=" + mode
    all_by_char_url = all_url + "&by_char=1"

    all_stats[mode] = requests.get(all_url).json()["Stats"]
    all_by_char_stats[mode] = requests.get(all_by_char_url).json()["Stats"]

    all_ip, all_avg, all_k_rate, all_era = calc_slash_line(all_stats[mode]["Pitching"])
    desc = "**Char** (IP): Opp AVG / K% / ERA, ERA-"
    title = f"\nAll ({all_ip:.1f} IP): {all_avg:.3f} Opp. AVG / {all_k_rate:.1%} K% / {all_era:.2f} ERA"

    try:
        sorted_char_list = sorted(all_by_char_stats[mode].keys(),
                                  key=lambda x: all_by_char_stats[mode][x]["Pitching"]["outs_pitched"],
                                  reverse=True)
    except KeyError:
        print("There was an error sorting the character list")
        sorted_char_list = sorted(all_by_char_stats[mode].keys())

    for char in sorted_char_list:
        char_stats = all_by_char_stats[mode][char]["Pitching"]
        ip, avg, k_rate, era = calc_slash_line(char_stats)

        era_minus = (era / all_era) * 100
        if char_stats['batters_faced'] > 0 and char_stats['outs_pitched'] > 27:
            desc += f"\n**{char}** ({ip:.1f} IP): {avg:.3f} / {k_rate:.1%} / {era:.2f} ERA, {round(era_minus)} ERA-"

    embed = discord.Embed(title=title, description=desc)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    embed.set_thumbnail(url=characters.images["all"])

    await ctx.send(embed=embed)


def calc_slash_line(raw_dict):
    ip = sum(raw_dict.get(key, 0) for key in
             ["outs_pitched"]) / 3
    avg = raw_dict["hits_allowed"] / (raw_dict["batters_faced"] - raw_dict['walks_bb'] - raw_dict['walks_hbp']) if raw_dict["batters_faced"] > 0 else 0
    k_rate = (raw_dict["strikeouts_pitched"] / (raw_dict["batters_faced"] - raw_dict['walks_bb'] - raw_dict['walks_hbp'])) if raw_dict['batters_faced'] > 0 else 0
    era = (9 * raw_dict['runs_allowed']) / ip if ip > 0 else 0
    return ip, avg, k_rate, era
