import logging
import math
from json import JSONDecodeError

import aiohttp
import discord

from helpers import stat_cache
from helpers.offensive_stat_calcs import _get_matchup_stats
from helpers.opponent_adjustment import loo_schedule_effect, opponent_adjusted_pitching_index
from helpers.sabermetrics import calc_pitching_index
from helpers.stat_utils import BASE_STATS_URL, send_error_embed, send_stat_embed
from models.misc_stats import MiscStats
from models.pitching_stats import PitchingStats
from resources import characters

logger = logging.getLogger(__name__)


def _league_rpa(all_pitching: PitchingStats) -> float:
    """League runs allowed per batter faced — the PSI denominator."""
    return all_pitching.runs_allowed / all_pitching.batters_faced if all_pitching.batters_faced > 0 else 0.0


async def _get_pitching_baseline(mode: str, session: aiohttp.ClientSession) -> PitchingStats:
    key = f"pitching:all:{mode}"
    cached = stat_cache.get(key)
    if cached is not None:
        return cached
    url = f"{BASE_STATS_URL}?exclude_batting=1&exclude_fielding=1&exclude_misc=1&tag={mode}"
    async with session.get(url) as response:
        data = (await response.json(content_type=None))["Stats"]
    pitching = PitchingStats.model_validate(data["Pitching"])
    stat_cache.set(key, pitching)
    return pitching


async def _get_pitching_by_char_baseline(mode: str, session: aiohttp.ClientSession) -> dict[str, PitchingStats]:
    key = f"pitching:by_char:{mode}"
    cached = stat_cache.get(key)
    if cached is not None:
        return cached
    url = f"{BASE_STATS_URL}?exclude_batting=1&exclude_fielding=1&exclude_misc=1&tag={mode}&by_char=1"
    async with session.get(url) as response:
        data = (await response.json(content_type=None))["Stats"]
    result = {char: PitchingStats.model_validate(char_data["Pitching"]) for char, char_data in data.items()}
    stat_cache.set(key, result)
    return result


async def refresh_baselines(mode: str, session: aiohttp.ClientSession):
    all_url = f"{BASE_STATS_URL}?exclude_batting=1&exclude_fielding=1&exclude_misc=1&tag={mode}"
    by_char_url = all_url + "&by_char=1"

    async with session.get(all_url) as response:
        all_data = (await response.json(content_type=None))["Stats"]
    stat_cache.set(f"pitching:all:{mode}", PitchingStats.model_validate(all_data["Pitching"]))

    async with session.get(by_char_url) as response:
        by_char_data = (await response.json(content_type=None))["Stats"]
    by_char_result = {
        char: PitchingStats.model_validate(char_data["Pitching"]) for char, char_data in by_char_data.items()
    }
    stat_cache.set(f"pitching:by_char:{mode}", by_char_result)


async def pstat_user_char(ctx, user: str, char: str, mode: str, session: aiohttp.ClientSession):
    try:
        char_id = characters.reverse_mappings[char]
        url = f"{BASE_STATS_URL}?exclude_batting=1&exclude_fielding=1&tag={mode}&char_id={char_id}&by_char=1&username={user}"
        async with session.get(url) as response:
            data = await response.json(content_type=None)
        by_char_baseline = await _get_pitching_by_char_baseline(mode, session)
        all_pitching = await _get_pitching_baseline(mode, session)
        matchup = await _get_matchup_stats(mode, session)
        stats = PitchingStats.model_validate(data.get("Stats", {}).get(char, {}).get("Pitching", {}))
    except (JSONDecodeError, KeyError):
        await send_error_embed(
            ctx,
            f"There are no stats for user {user} with character {char} in {mode} or the user/character alias was not found.",
        )
        return

    ip, avg, k_rate, era = calc_slash_line(stats)

    league_rpa = _league_rpa(all_pitching)
    char_ref = by_char_baseline.get(char)
    if char_ref is not None:
        raw_psi = calc_pitching_index(stats, char_ref, league_rpa)
        # The schedule is the user's overall slate in this mode (per-character
        # matchup data isn't available) — same approximation as the batting side.
        league_rpi = matchup["league_runs_per_inning"]
        schedule = matchup["schedules"].get(user.lower(), {})
        offense_effect, total_games = loo_schedule_effect(user.lower(), matchup["offense"], schedule, league_rpi)
        psi = opponent_adjusted_pitching_index(raw_psi, offense_effect, total_games, league_rpi)
    else:
        psi = 0.0

    misc = MiscStats.model_validate(data.get("Stats", {}).get(char, {}).get("Misc", {}))
    games = misc.home_wins + misc.away_wins + misc.home_loses + misc.away_loses
    winrate = (misc.home_wins + misc.away_wins) / games if games > 0 else 0

    ip_str = str(math.floor(ip)) + "." + str(stats.outs_pitched % 3)
    embed = discord.Embed(title=f"{user} - {char} ({ip_str} IP)")
    fields = [
        ("G", str(games)),
        ("Win%", "{:.1f}".format(winrate * 100)),
        ("Batters Faced", str(stats.batters_faced)),
        ("Hits Allowed", str(stats.hits_allowed)),
        ("IP", str(round(stats.outs_pitched / 3, 1))),
        ("Runs Allowed", str(stats.runs_allowed)),
        ("​", "​"),
        ("K", str(stats.strikeouts_pitched)),
        ("BB", str(stats.walks_bb + stats.walks_hbp)),
        ("​", "​"),
        ("Opp. AVG", "{:.3f}".format(avg)),
        ("K%", "{:.1%}".format(k_rate)),
        ("ERA", "{:.2f}".format(era)),
        ("PSI", str(round(psi))),
        ("​", "​"),
    ]

    for name, value in fields:
        embed.add_field(name=name, value=value, inline=True)

    embed.set_thumbnail(url=characters.images[char])
    await ctx.send(embed=embed)


async def pstat_user(ctx, user: str, mode: str, session: aiohttp.ClientSession):
    base_url = f"{BASE_STATS_URL}?exclude_batting=1&exclude_fielding=1&exclude_misc=1&tag={mode}"
    user_url = f"{base_url}&username={user}"
    user_by_char_url = f"{base_url}&by_char=1&username={user}"
    try:
        all_pitching = await _get_pitching_baseline(mode, session)
        by_char_baseline = await _get_pitching_by_char_baseline(mode, session)
        matchup = await _get_matchup_stats(mode, session)
        async with session.get(user_url) as response:
            user_response = await response.json(content_type=None)
        async with session.get(user_by_char_url) as response:
            user_by_char_response = await response.json(content_type=None)
    except (JSONDecodeError, KeyError):
        await send_error_embed(ctx, f"There are no stats for user {user} in {mode} or the username was not found.")
        return

    user_dict: dict[str, PitchingStats] = {"all": PitchingStats.model_validate(user_response["Stats"]["Pitching"])}
    for char in user_by_char_response["Stats"]:
        user_dict[char] = PitchingStats.model_validate(user_by_char_response["Stats"][char]["Pitching"])

    user_stats = user_dict["all"]
    ip, avg, k_rate, era = calc_slash_line(user_stats)

    league_rpa = _league_rpa(all_pitching)
    league_rpi = matchup["league_runs_per_inning"]
    schedule = matchup["schedules"].get(user.lower(), {})
    offense_effect, total_games = loo_schedule_effect(user.lower(), matchup["offense"], schedule, league_rpi)

    raw_psi = calc_pitching_index(user_stats, all_pitching, league_rpa)
    psi = opponent_adjusted_pitching_index(raw_psi, offense_effect, total_games, league_rpi)

    ip_str = str(math.floor(ip)) + "." + str(user_stats.outs_pitched % 3)
    title = f"\n{user} ({ip_str} IP): {avg:.3f} / {k_rate:.1%} / {era:.2f} ERA, {round(psi)} PSI"

    desc = "**Char** (IP): Opp. AVG / K% / ERA, PSI"

    del user_dict["all"]
    try:
        sorted_char_list = sorted(user_dict.keys(), key=lambda x: user_dict[x].outs_pitched, reverse=True)
    except KeyError:
        logger.warning("Error sorting the character list; falling back to name order")
        sorted_char_list = sorted(user_dict.keys())

    for char in sorted_char_list:
        char_stats = user_dict[char]
        ip, avg, k_rate, era = calc_slash_line(char_stats)
        char_ref = by_char_baseline.get(char)
        if char_ref is not None:
            raw_char_psi = calc_pitching_index(char_stats, char_ref, league_rpa)
            char_psi = opponent_adjusted_pitching_index(raw_char_psi, offense_effect, total_games, league_rpi)
        else:
            char_psi = 0.0
        if char_stats.batters_faced > 0 and char_stats.outs_pitched > 3:
            ip_str = str(math.floor(ip)) + "." + str(char_stats.outs_pitched % 3)
            desc += f"\n**{char}** ({ip_str} IP): {avg:.3f} / {k_rate:.1%} / {era:.2f}, {round(char_psi)} PSI"

    await send_stat_embed(ctx, title, desc, "all")


async def pstat_char(ctx, char: str, mode: str, session: aiohttp.ClientSession):
    try:
        all_url = f"{BASE_STATS_URL}?exclude_batting=1&exclude_fielding=1&exclude_misc=1&tag={mode}"
        if char != "all":
            char_url = f"{all_url}&char_id={str(characters.reverse_mappings[char])}"
            char_by_user_url = f"{all_url}&by_user=1&char_id={str(characters.reverse_mappings[char])}"
        else:
            char_url = all_url
            char_by_user_url = all_url + "&by_user=1"

        all_pitching = await _get_pitching_baseline(mode, session)
        matchup = await _get_matchup_stats(mode, session)
        async with session.get(char_url) as response:
            char_response = await response.json(content_type=None)
        async with session.get(char_by_user_url) as response:
            char_by_user_response = await response.json(content_type=None)
    except (JSONDecodeError, KeyError):
        await send_error_embed(
            ctx, f"There are no stats for character {char} in {mode} or the character alias was not found."
        )
        return

    user_list: list[tuple[str, PitchingStats]] = [
        ("all", PitchingStats.model_validate(char_response["Stats"]["Pitching"]))
    ]
    for user, stats in char_by_user_response["Stats"].items():
        user_list.append((user, PitchingStats.model_validate(stats["Pitching"])))

    char_stats = user_list[0][1]
    ip, avg, k_rate, era = calc_slash_line(char_stats)
    ip_str = str(math.floor(ip)) + "." + str(char_stats.outs_pitched % 3)

    league_rpa = _league_rpa(all_pitching)
    league_rpi = matchup["league_runs_per_inning"]

    title = f"\n{char} ({ip_str} IP): {avg:.3f} Opp. AVG / {k_rate:.1%} K% / {era:.2f} ERA"
    desc = "**User** (IP): Opp. AVG / K% / ERA, PSI"

    output_list = []
    for user, user_stats in user_list[1:]:
        user_ip, user_avg, user_k_rate, user_era = calc_slash_line(user_stats)
        raw_psi = calc_pitching_index(user_stats, char_stats, league_rpa)
        # Each row is a different user, adjusted by that user's own schedule —
        # all from the one cached game-log structure (no extra calls).
        schedule = matchup["schedules"].get(user.lower(), {})
        offense_effect, total_games = loo_schedule_effect(user.lower(), matchup["offense"], schedule, league_rpi)
        psi = opponent_adjusted_pitching_index(raw_psi, offense_effect, total_games, league_rpi)

        if user_ip > (ip / 100):
            user_ip_str = str(math.floor(user_ip)) + "." + str(user_stats.outs_pitched % 3)
            output_list.append((user, user_ip_str, user_avg, user_k_rate, user_era, psi))

    sorted_user_list = sorted(output_list, key=lambda x: x[5], reverse=True)

    for index, user_stats in zip(range(20), sorted_user_list):
        user = user_stats[0]
        user_ip = user_stats[1]
        user_avg = user_stats[2]
        user_k_rate = user_stats[3]
        user_era = user_stats[4]
        psi = user_stats[5]
        desc += f"\n{index + 1}. **{user}** ({user_ip} IP): {user_avg:.3f} / {user_k_rate:.1%} / {user_era:.2f}, {round(psi)} PSI"

    await send_stat_embed(ctx, title, desc, char)


async def pstat_all(ctx, mode: str, session: aiohttp.ClientSession):
    all_url = f"{BASE_STATS_URL}?exclude_batting=1&exclude_fielding=1&exclude_misc=1&tag={mode}"
    by_char_url = all_url + "&by_char=1"

    async with session.get(all_url) as response:
        all_data = (await response.json(content_type=None))["Stats"]
    async with session.get(by_char_url) as response:
        by_char_data = (await response.json(content_type=None))["Stats"]

    all_pitching = PitchingStats.model_validate(all_data["Pitching"])
    all_ip, all_avg, all_k_rate, all_era = calc_slash_line(all_pitching)
    stat_cache.set(f"pitching:all:{mode}", all_pitching)

    league_rpa = _league_rpa(all_pitching)

    by_char_baseline = {
        char: PitchingStats.model_validate(char_data["Pitching"]) for char, char_data in by_char_data.items()
    }
    stat_cache.set(f"pitching:by_char:{mode}", by_char_baseline)

    all_ip_str = str(math.floor(all_ip)) + "." + str(all_pitching.outs_pitched % 3)
    desc = "**Char** (IP): Opp AVG / K% / ERA, PSI"
    title = f"\nAll ({all_ip_str} IP): {all_avg:.3f} Opp. AVG / {all_k_rate:.1%} K% / {all_era:.2f} ERA"

    try:
        sorted_char_list = sorted(by_char_baseline.keys(), key=lambda x: by_char_baseline[x].outs_pitched, reverse=True)
    except KeyError:
        logger.warning("Error sorting the character list; falling back to name order")
        sorted_char_list = sorted(by_char_baseline.keys())

    for char in sorted_char_list:
        char_stats = by_char_baseline[char]
        ip, avg, k_rate, era = calc_slash_line(char_stats)
        psi = calc_pitching_index(char_stats, all_pitching, league_rpa)
        if char_stats.batters_faced > 0 and char_stats.outs_pitched > 27:
            ip_str = str(math.floor(ip)) + "." + str(char_stats.outs_pitched % 3)
            desc += f"\n**{char}** ({ip_str} IP): {avg:.3f} / {k_rate:.1%} / {era:.2f}, {round(psi)} PSI"

    await send_stat_embed(ctx, title, desc, "all")


def calc_slash_line(stats: PitchingStats):
    ip = stats.outs_pitched / 3
    avg = (
        stats.hits_allowed / (stats.batters_faced - stats.walks_bb - stats.walks_hbp) if stats.batters_faced > 0 else 0
    )
    k_rate = (
        stats.strikeouts_pitched / (stats.batters_faced - stats.walks_bb - stats.walks_hbp)
        if stats.batters_faced > 0
        else 0
    )
    era = (9 * stats.runs_allowed) / ip if ip > 0 else 0
    return ip, avg, k_rate, era
