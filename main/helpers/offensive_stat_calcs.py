import logging

import aiohttp
import discord
from json import JSONDecodeError
from resources import characters
from models.batting_stats import BattingStats
from models.misc_stats import MiscStats
from helpers.stat_utils import BASE_STATS_URL, FRONTEND_URL, send_error_embed, send_stat_embed
from helpers import stat_cache

logger = logging.getLogger(__name__)


async def _get_batting_baseline(mode: str, session: aiohttp.ClientSession) -> dict:
    key = f"batting:all:{mode}"
    cached = stat_cache.get(key)
    if cached is not None:
        return cached
    url = f"{BASE_STATS_URL}?exclude_pitching=1&exclude_fielding=1&exclude_misc=1&exclude_nonfair=1&tag={mode}"
    async with session.get(url) as response:
        data = (await response.json(content_type=None))["Stats"]
    batting = BattingStats.model_validate(data["Batting"])
    _, _, obp, slg = calc_slash_line(batting)
    result = {"obp": obp, "slg": slg}
    stat_cache.set(key, result)
    return result


async def _get_batting_by_char_baseline(mode: str, session: aiohttp.ClientSession) -> dict:
    key = f"batting:by_char:{mode}"
    cached = stat_cache.get(key)
    if cached is not None:
        return cached
    url = f"{BASE_STATS_URL}?exclude_pitching=1&exclude_fielding=1&exclude_misc=1&exclude_nonfair=1&tag={mode}&by_char=1"
    async with session.get(url) as response:
        data = (await response.json(content_type=None))["Stats"]
    result = {}
    for char, char_data in data.items():
        char_batting = BattingStats.model_validate(char_data["Batting"])
        _, _, obp, slg = calc_slash_line(char_batting)
        result[char] = {"obp": obp, "slg": slg}
    stat_cache.set(key, result)
    return result


async def refresh_baselines(mode: str, session: aiohttp.ClientSession):
    all_url = f"{BASE_STATS_URL}?exclude_pitching=1&exclude_fielding=1&exclude_misc=1&exclude_nonfair=1&tag={mode}"
    by_char_url = all_url + "&by_char=1"

    async with session.get(all_url) as response:
        all_data = (await response.json(content_type=None))["Stats"]
    batting = BattingStats.model_validate(all_data["Batting"])
    _, _, obp, slg = calc_slash_line(batting)
    stat_cache.set(f"batting:all:{mode}", {"obp": obp, "slg": slg})

    async with session.get(by_char_url) as response:
        by_char_data = (await response.json(content_type=None))["Stats"]
    by_char_result = {}
    for char, char_data in by_char_data.items():
        char_batting = BattingStats.model_validate(char_data["Batting"])
        _, _, char_obp, char_slg = calc_slash_line(char_batting)
        by_char_result[char] = {"obp": char_obp, "slg": char_slg}
    stat_cache.set(f"batting:by_char:{mode}", by_char_result)


async def ostat_user_char(ctx, user: str, char: str, mode: str, session: aiohttp.ClientSession):
    try:
        char_id = characters.reverse_mappings[char]
        url = f"{BASE_STATS_URL}?exclude_pitching=1&exclude_fielding=1&tag={mode}&char_id={char_id}&by_char=1&username={user}&exclude_nonfair=1"
        async with session.get(url) as response:
            data = await response.json(content_type=None)
        by_char_baseline = await _get_batting_by_char_baseline(mode, session)
        stats = BattingStats.model_validate(data.get("Stats", {}).get(char, {}).get("Batting", {}))
    except (JSONDecodeError, KeyError):
        await send_error_embed(ctx, f"There are no stats for user {user} with character {char} in {mode} or the user/character alias was not found.")
        return

    pa, avg, obp, slg = calc_slash_line(stats)
    ops = obp + slg

    char_baseline = by_char_baseline.get(char, {})
    overall_obp = char_baseline.get("obp", 0)
    overall_slg = char_baseline.get("slg", 0)
    ops_plus = ((obp / overall_obp) + (slg / overall_slg) - 1) * 100 if overall_obp > 0 and overall_slg > 0 else -100

    misc = MiscStats.model_validate(data.get("Stats", {}).get(char, {}).get("Misc", {}))
    games = misc.home_wins + misc.away_wins + misc.home_loses + misc.away_loses
    winrate = (misc.home_wins + misc.away_wins) / games if games > 0 else 0

    embed = discord.Embed(title=f"{user} - {char} ({pa} PA)")
    fields = [("G", str(games)),
              ("Win%", "{:.1f}".format(winrate * 100)),
              ("AB", str(stats.summary_at_bats)),
              ("H", str(stats.summary_hits)),
              ("2B", str(stats.summary_doubles)),
              ("3B", str(stats.summary_triples)),
              ("HR", str(stats.summary_homeruns)),
              ("RBI", str(stats.summary_rbi)),
              ("​", "​"),
              ("SO", str(stats.summary_strikeouts)),
              ("BB", str(stats.summary_walks_bb + stats.summary_walks_hbp)),
              ("​", "​"),
              ("Perfect", str(stats.perfect_hits)),
              ("Nice", str(stats.nice_hits)),
              ("Sour", str(stats.sour_hits)),
              ("AVG", "{:.3f}".format(avg)),
              ("OBP", "{:.3f}".format(obp)),
              ("SLG", "{:.3f}".format(slg)),
              ("OPS", "{:.3f}".format(ops)),
              ("cOPS+", str(round(ops_plus))),
              ("​", "​")]

    for name, value in fields:
        embed.add_field(name=name, value=value, inline=True)

    embed.set_thumbnail(url=characters.images[char])
    await ctx.send(embed=embed)


async def ostat_user(ctx, user: str, mode: str, session: aiohttp.ClientSession):
    await ctx.send(f"This information can now be accessed here: {FRONTEND_URL}/user/{user}/batting")
    base_url = f"{BASE_STATS_URL}?exclude_pitching=1&exclude_fielding=1&exclude_misc=1&tag={mode}&exclude_nonfair=1"
    user_url = f"{base_url}&username={user}"
    user_by_char_url = f"{base_url}&by_char=1&username={user}"
    try:
        all_baseline = await _get_batting_baseline(mode, session)
        by_char_baseline = await _get_batting_by_char_baseline(mode, session)
        async with session.get(user_url) as response:
            user_response = await response.json(content_type=None)
        async with session.get(user_by_char_url) as response:
            user_by_char_response = await response.json(content_type=None)
    except (JSONDecodeError, KeyError):
        await send_error_embed(ctx, f"There are no stats for user {user} in {mode} or the username was not found.")
        return

    user_dict: dict[str, BattingStats] = {
        "all": BattingStats.model_validate(user_response["Stats"]["Batting"])
    }
    for char in user_by_char_response["Stats"]:
        user_dict[char] = BattingStats.model_validate(user_by_char_response["Stats"][char]["Batting"])

    user_stats = user_dict["all"]
    pa, avg, obp, slg = calc_slash_line(user_stats)

    overall_obp = all_baseline.get("obp", 0)
    overall_slg = all_baseline.get("slg", 0)
    ops_plus = ((obp / overall_obp) + (slg / overall_slg) - 1) * 100 if overall_obp > 0 and overall_slg > 0 else -100
    title = f"\n{user} ({pa} PA): {avg:.3f} / {obp:.3f} / {slg:.3f}, {round(ops_plus)} OPS+"

    desc = "**Char** (PA): AVG / OBP / SLG, cOPS+"

    del user_dict["all"]
    try:
        sorted_char_list = sorted(user_dict.keys(),
                                  key=lambda x: user_dict[x].summary_at_bats + user_dict[x].summary_walks_bb +
                                                user_dict[x].summary_walks_hbp + user_dict[x].summary_sac_flys,
                                  reverse=True)
    except KeyError:
        logger.warning("Error sorting the character list; falling back to name order")
        sorted_char_list = sorted(user_dict.keys())

    for char in sorted_char_list:
        char_stats = user_dict[char]
        pa, avg, obp, slg = calc_slash_line(char_stats)
        char_baseline = by_char_baseline.get(char, {})
        overall_obp = char_baseline.get("obp", 0)
        overall_slg = char_baseline.get("slg", 0)
        ops_plus = ((obp / overall_obp) + (slg / overall_slg) - 1) * 100 if overall_obp > 0 and overall_slg > 0 else -100
        desc += f'\n**{char}** ({pa} PA): {avg:.3f} / {obp:.3f} / {slg:.3f}, {round(ops_plus)} cOPS+'

    await send_stat_embed(ctx, title, desc, "all")


async def ostat_char(ctx, char: str, mode: str, session: aiohttp.ClientSession):
    try:
        all_url = f"{BASE_STATS_URL}?exclude_pitching=1&exclude_fielding=1&exclude_misc=1&tag={mode}&exclude_nonfair=1"
        if char != "all":
            char_url = f"{all_url}&char_id={str(characters.reverse_mappings[char])}"
            char_by_user_url = f"{all_url}&by_user=1&char_id={str(characters.reverse_mappings[char])}"
        else:
            char_url = all_url
            char_by_user_url = all_url + "&by_user=1"

        async with session.get(char_url) as response:
            char_response = await response.json(content_type=None)
        async with session.get(char_by_user_url) as response:
            char_by_user_response = await response.json(content_type=None)
    except (JSONDecodeError, KeyError):
        await send_error_embed(ctx, f"There are no stats for character {char} in {mode} or the character alias was not found.")
        return

    user_list: list[tuple[str, BattingStats]] = [
        ("all", BattingStats.model_validate(char_response["Stats"]["Batting"]))
    ]
    for user, stats in char_by_user_response["Stats"].items():
        user_list.append((user, BattingStats.model_validate(stats["Batting"])))

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

        if user_pa > (pa / 100):
            output_list.append((user, user_pa, user_avg, user_obp, user_slg, ops_plus))

    sorted_user_list = sorted(output_list, key=lambda x: x[5], reverse=True)

    for index, user_stats in zip(range(20), sorted_user_list):
        user = user_stats[0]
        user_pa = user_stats[1]
        user_avg = user_stats[2]
        user_obp = user_stats[3]
        user_slg = user_stats[4]
        ops_plus = user_stats[5]
        desc += f"\n{index + 1}. **{user}** ({user_pa} PA): {user_avg:.3f} / {user_obp:.3f} / {user_slg:.3f}, {round(ops_plus)} cOPS+"

    await send_stat_embed(ctx, title, desc, char)


async def ostat_all(ctx, mode: str, session: aiohttp.ClientSession):
    all_url = f"{BASE_STATS_URL}?exclude_pitching=1&exclude_fielding=1&exclude_nonfair=1&exclude_misc=1&tag={mode}"
    by_char_url = all_url + "&by_char=1"

    async with session.get(all_url) as response:
        all_data = (await response.json(content_type=None))["Stats"]
    async with session.get(by_char_url) as response:
        by_char_data = (await response.json(content_type=None))["Stats"]

    all_batting = BattingStats.model_validate(all_data["Batting"])
    all_pa, all_avg, all_obp, all_slg = calc_slash_line(all_batting)
    stat_cache.set(f"batting:all:{mode}", {"obp": all_obp, "slg": all_slg})

    by_char_baseline = {}
    for char, char_data in by_char_data.items():
        char_batting = BattingStats.model_validate(char_data["Batting"])
        _, _, char_obp, char_slg = calc_slash_line(char_batting)
        by_char_baseline[char] = {"obp": char_obp, "slg": char_slg}
    stat_cache.set(f"batting:by_char:{mode}", by_char_baseline)

    desc = "**Char** (PA): AVG / OBP / SLG, OPS+"
    title = f"\nAll ({all_pa} PA): {all_avg:.3f} / {all_obp:.3f} / {all_slg:.3f}"

    try:
        sorted_char_list = sorted(by_char_data.keys(),
                                  key=lambda x: by_char_data[x]["Batting"].get("summary_at_bats", 0) +
                                                by_char_data[x]["Batting"].get("summary_walks_bb", 0) +
                                                by_char_data[x]["Batting"].get("summary_walks_hbp", 0) +
                                                by_char_data[x]["Batting"].get("summary_sac_flys", 0),
                                  reverse=True)
    except KeyError:
        logger.warning("Error sorting the character list; falling back to name order")
        sorted_char_list = sorted(by_char_data.keys())

    for char in sorted_char_list:
        char_batting = BattingStats.model_validate(by_char_data[char]["Batting"])
        pa, avg, obp, slg = calc_slash_line(char_batting)
        ops_plus = ((obp / all_obp) + (slg / all_slg) - 1) * 100
        desc += f"\n**{char}** ({pa} PA): {avg:.3f} / {obp:.3f} / {slg:.3f}, {round(ops_plus)} OPS+"

    await send_stat_embed(ctx, title, desc, "all")


def calc_slash_line(stats: BattingStats):
    pa = stats.summary_at_bats + stats.summary_walks_bb + stats.summary_walks_hbp + stats.summary_sac_flys
    avg = stats.summary_hits / stats.summary_at_bats if stats.summary_at_bats > 0 else 0
    obp = (stats.summary_hits + stats.summary_walks_hbp + stats.summary_walks_bb) / pa if pa > 0 else 0
    slg = (stats.summary_singles + (stats.summary_doubles * 2) + (stats.summary_triples * 3) + (
            stats.summary_homeruns * 4)) / stats.summary_at_bats if stats.summary_at_bats > 0 else 0
    return pa, avg, obp, slg
