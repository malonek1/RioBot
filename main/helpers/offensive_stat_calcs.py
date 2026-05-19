import aiohttp
import discord
from json import JSONDecodeError
from resources import characters
from resources.api import STATS_URL, GAMES_URL
from resources.stat_constants import LINEAR_WEIGHTS, LEAGUE_RUNS_PER_PA, calc_woba, calc_adj_wrc_plus
from helpers.utils import strip_non_alphanumeric
from models.batting_stats import BattingStats
from models.misc_stats import MiscStats

all_stats = {}
all_by_char_stats = {}
_user_opp_elo_cache: dict[tuple[str, str], float | None] = {}


async def get_user_opp_elo(user: str, mode: str, session: aiohttp.ClientSession) -> float | None:
    key = (user, mode)
    if key in _user_opp_elo_cache:
        return _user_opp_elo_cache[key]

    web_mode = strip_non_alphanumeric(mode)
    async with session.get(GAMES_URL, params={"username": user, "tag": web_mode, "limit_games": 500}) as response:
        games = (await response.json(content_type=None)).get("games", [])
    opp_elos = []
    for game in games:
        if game["home_score"] > game["away_score"]:
            home_elo, away_elo = game["winner_incoming_elo"], game["loser_incoming_elo"]
        else:
            home_elo, away_elo = game["loser_incoming_elo"], game["winner_incoming_elo"]
        opp_elos.append(away_elo if game["home_user"] == user else home_elo)
    result = sum(opp_elos) / len(opp_elos) if opp_elos else None
    _user_opp_elo_cache[key] = result
    return result



async def ostat_user_char(ctx, user: str, char: str, mode: str, session: aiohttp.ClientSession):
    global all_by_char_stats
    try:
        all_by_char_url = f"{STATS_URL}?exclude_pitching=1&exclude_fielding=1&tag={mode}&by_char=1&exclude_nonfair=1"
        char_id = characters.reverse_mappings[char]
        url = f"{STATS_URL}?exclude_pitching=1&exclude_fielding=1&tag={mode}&char_id={char_id}&by_char=1&username={user}&exclude_nonfair=1"
        async with session.get(url) as response:
            data = await response.json(content_type=None)
        if not all_by_char_stats.get(mode, {}).get("Batting", {}):
            async with session.get(all_by_char_url) as response:
                all_by_char_stats[mode] = (await response.json(content_type=None))["Stats"]
        stats = BattingStats.model_validate(data.get("Stats", {}).get(char, {}).get("Batting", {}))
    except (JSONDecodeError, KeyError):
        embed = discord.Embed(
            title=f"There are no stats for user {user} with character {char} in {mode} or the user/character alias was not found.",
            color=0xEA7D07)
        await ctx.send(embed=embed)
        return

    pa, avg, obp, slg = calc_slash_line(stats)
    ops = obp + slg

    all_char_stats = BattingStats.model_validate(all_by_char_stats.get(mode, {}).get(char, {}).get("Batting", {}))
    wrc_plus = calc_wrc_plus(stats, all_char_stats)

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
              ("cwRC+", str(round(wrc_plus))),
              ("​", "​")]

    for name, value in fields:
        embed.add_field(name=name, value=value, inline=True)

    embed.set_thumbnail(url=characters.images[char])

    await ctx.send(embed=embed)


async def ostat_user(ctx, user: str, mode: str, session: aiohttp.ClientSession):
    await ctx.send(f"This information can now be accessed here: https://project-rio-frontend.vercel.app/user/{user}/batting")
    global all_stats, all_by_char_stats
    all_url = f"{STATS_URL}?exclude_pitching=1&exclude_fielding=1&exclude_misc=1&tag={mode}&exclude_nonfair=1"
    user_url = f"{all_url}&username={user}"
    all_by_char_url = f"{all_url}&by_char=1"
    user_by_char_url = f"{all_by_char_url}&username={user}"
    try:
        if not all_stats.get(mode, {}).get("Batting", {}):
            print("getting all stats")
            async with session.get(all_url) as response:
                all_stats[mode] = (await response.json(content_type=None))["Stats"]
        if not all_by_char_stats.get(mode, {}):
            print("Getting all by char stats")
            async with session.get(all_by_char_url) as response:
                all_by_char_stats[mode] = (await response.json(content_type=None))["Stats"]
        async with session.get(user_url) as response:
            user_response = await response.json(content_type=None)
        async with session.get(user_by_char_url) as response:
            user_by_char_response = await response.json(content_type=None)
    except (JSONDecodeError, KeyError):
        embed = discord.Embed(
            title=f"There are no stats for user {user} in {mode} or the username was not found.",
            color=0xEA7D07)
        await ctx.send(embed=embed)
        return

    user_dict: dict[str, BattingStats] = {
        "all": BattingStats.model_validate(user_response["Stats"]["Batting"])
    }
    for char in user_by_char_response["Stats"]:
        user_dict[char] = BattingStats.model_validate(user_by_char_response["Stats"][char]["Batting"])

    user_stats = user_dict["all"]
    pa, avg, obp, slg = calc_slash_line(user_stats)

    all_batting = BattingStats.model_validate(all_stats[mode]["Batting"])
    wrc_plus = calc_wrc_plus(user_stats, all_batting)
    title = f"\n{user} ({pa} PA): {avg:.3f} / {obp:.3f} / {slg:.3f}, {round(wrc_plus)} wRC+"

    desc = "**Char** (PA): AVG / OBP / SLG, cwRC+"

    del user_dict["all"]
    try:
        sorted_char_list = sorted(user_dict.keys(),
                                  key=lambda x: user_dict[x].summary_at_bats + user_dict[x].summary_walks_bb +
                                                user_dict[x].summary_walks_hbp + user_dict[x].summary_sac_flys,
                                  reverse=True)
    except KeyError:
        print("There was an error sorting the character list")
        sorted_char_list = sorted(user_dict.keys())

    for char in sorted_char_list:
        char_stats = user_dict[char]
        pa, avg, obp, slg = calc_slash_line(char_stats)
        all_char_stats = BattingStats.model_validate(all_by_char_stats[mode][char]["Batting"])
        wrc_plus = calc_wrc_plus(char_stats, all_char_stats)
        desc += f'\n**{char}** ({pa} PA): {avg:.3f} / {obp:.3f} / {slg:.3f}, {round(wrc_plus)} cwRC+'

    embed = discord.Embed(title=title, description=desc)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    embed.set_thumbnail(url=characters.images["all"])

    await ctx.send(embed=embed)


async def ostat_char(ctx, char: str, mode: str, session: aiohttp.ClientSession):
    try:
        all_url = f"{STATS_URL}?exclude_pitching=1&exclude_fielding=1&exclude_misc=1&tag={mode}&exclude_nonfair=1"
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
        embed = discord.Embed(
            title=f"There are no stats for character {char} in {mode} or the character alias was not found.",
            color=0xEA7D07)
        await ctx.send(embed=embed)
        return

    user_list: list[tuple[str, BattingStats]] = [
        ("all", BattingStats.model_validate(char_response["Stats"]["Batting"]))
    ]
    for user, stats in char_by_user_response["Stats"].items():
        user_list.append((user, BattingStats.model_validate(stats["Batting"])))

    char_stats = user_list[0][1]
    pa, avg, obp, slg = calc_slash_line(char_stats)

    title = f"\n{char} ({pa} PA): {avg:.3f} / {obp:.3f} / {slg:.3f}"
    desc = "**User** (PA): AVG / OBP / SLG, cwRC+"

    output_list = []
    for user, user_stats in user_list[1:]:
        user_pa, user_avg, user_obp, user_slg = calc_slash_line(user_stats)
        wrc_plus = calc_wrc_plus(user_stats, char_stats)

        if user_pa > (pa / 200) + 20:
            output_list.append((user, user_pa, user_avg, user_obp, user_slg, wrc_plus))

    sorted_user_list = sorted(output_list, key=lambda x: x[5], reverse=True)

    for index, user_stats in zip(range(20), sorted_user_list):
        user = user_stats[0]
        user_pa = user_stats[1]
        user_avg = user_stats[2]
        user_obp = user_stats[3]
        user_slg = user_stats[4]
        wrc_plus = user_stats[5]
        desc += f"\n{index + 1}. **{user}** ({user_pa} PA): {user_avg:.3f} / {user_obp:.3f} / {user_slg:.3f}, {round(wrc_plus)} cwRC+"

    embed = discord.Embed(title=title, description=desc)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    embed.set_thumbnail(url=characters.images[char])

    await ctx.send(embed=embed)


async def ostat_all(ctx, mode: str, session: aiohttp.ClientSession):
    global all_stats, all_by_char_stats
    all_url = STATS_URL + "?exclude_pitching=1&exclude_fielding=1&exclude_nonfair=1&exclude_misc=1&tag=" + mode
    all_by_char_url = all_url + "&by_char=1"

    async with session.get(all_url) as response:
        all_stats[mode] = (await response.json(content_type=None))["Stats"]
    async with session.get(all_by_char_url) as response:
        all_by_char_stats[mode] = (await response.json(content_type=None))["Stats"]

    all_batting = BattingStats.model_validate(all_stats[mode]["Batting"])
    all_pa, all_avg, all_obp, all_slg = calc_slash_line(all_batting)
    desc = "**Char** (PA): AVG / OBP / SLG, wRC+"
    title = f"\nAll ({all_pa} PA): {all_avg:.3f} / {all_obp:.3f} / {all_slg:.3f}"

    try:
        sorted_char_list = sorted(all_by_char_stats[mode].keys(),
                                  key=lambda x: all_by_char_stats[mode][x]["Batting"].get("summary_at_bats", 0) +
                                                all_by_char_stats[mode][x]["Batting"].get("summary_walks_bb", 0) +
                                                all_by_char_stats[mode][x]["Batting"].get("summary_walks_hbp", 0) +
                                                all_by_char_stats[mode][x]["Batting"].get("summary_sac_flys", 0),
                                  reverse=True)
    except KeyError:
        print("There was an error sorting the character list")
        sorted_char_list = sorted(all_by_char_stats[mode].keys())

    for char in sorted_char_list:
        char_stats = BattingStats.model_validate(all_by_char_stats[mode][char]["Batting"])
        pa, avg, obp, slg = calc_slash_line(char_stats)

        wrc_plus = calc_wrc_plus(char_stats, all_batting)

        desc += f"\n**{char}** ({pa} PA): {avg:.3f} / {obp:.3f} / {slg:.3f}, {round(wrc_plus)} wRC+"

    embed = discord.Embed(title=title, description=desc)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    embed.set_thumbnail(url=characters.images["all"])

    await ctx.send(embed=embed)


def calc_slash_line(stats: BattingStats):
    pa = stats.summary_at_bats + stats.summary_walks_bb + stats.summary_walks_hbp + stats.summary_sac_flys
    avg = stats.summary_hits / stats.summary_at_bats if stats.summary_at_bats > 0 else 0
    obp = (stats.summary_hits + stats.summary_walks_hbp + stats.summary_walks_bb) / pa if pa > 0 else 0
    slg = (stats.summary_singles + (stats.summary_doubles * 2) + (stats.summary_triples * 3) + (
            stats.summary_homeruns * 4)) / stats.summary_at_bats if stats.summary_at_bats > 0 else 0
    return pa, avg, obp, slg


def calc_wrc_plus(stats: BattingStats, overall_stats: BattingStats) -> float:
    overall_pa = (overall_stats.summary_at_bats + overall_stats.summary_walks_bb +
                  overall_stats.summary_walks_hbp + overall_stats.summary_sac_flys)
    if overall_pa == 0:
        return 0

    overall_obp = (overall_stats.summary_hits + overall_stats.summary_walks_hbp +
                   overall_stats.summary_walks_bb) / overall_pa

    player_woba = calc_woba(stats)
    overall_woba = calc_woba(overall_stats)

    if overall_woba == 0:
        return 0

    woba_scale = overall_obp / overall_woba

    return (((player_woba - overall_woba) / woba_scale + LEAGUE_RUNS_PER_PA) / LEAGUE_RUNS_PER_PA) * 100
