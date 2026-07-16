"""Strength-of-schedule (opponent-quality) adjustment that turns raw wRC+ and the
pitching index into BSI / PSI. Pure functions — no I/O — unit-tested offline.

Additive on the run scale: facing tougher competition raises the skill number.

    BSI = wRC+           - (D / L) * 100 * transfer * schedule_reliability
    PSI = pitching index + (O / L) * 100 * transfer * schedule_reliability

L is the league run rate (runs per inning). D is the games-weighted average of each
opponent's run prevention vs league (tough = D < 0 -> raises BSI); O is the same for
opponent offense (tough = O > 0 -> raises PSI).

Opponent quality is computed LEAVE-ONE-OUT from the game log: an opponent's runs
allowed/scored EXCLUDE their games against the player being evaluated. In 1v1 this
removes the endogeneity where a player's own results inflate their opponents' stats
— validated across three seasons to flip the adjustment from harmful to helpful
mid-season (see scratch/loo_validation.py).
"""

from resources.stat_constants import (
    OPPONENT_REGRESSION_INN,
    OPPONENT_TRANSFER_COEFF,
    SCHEDULE_REGRESSION_GAMES,
)


def build_matchup_stats(games: list[dict]) -> dict:
    """From a mode's game log, build everything the LOO adjustment needs:

        {
          "schedules": {user: {opponent: games_played}},
          "defense":   {user: {"runs": runs allowed, "inn": innings, "vs": {opp: (runs, inn)}}},
          "offense":   {user: {"runs": runs scored,  "inn": innings, "vs": {opp: (runs, inn)}}},
          "league_runs_per_inning": float,
        }

    All usernames lowercased. Games missing a user or with no innings are skipped.
    """
    schedules: dict[str, dict[str, int]] = {}
    defense: dict[str, dict] = {}
    offense: dict[str, dict] = {}
    total_runs = 0
    total_innings = 0

    def add(side: dict, user: str, runs: int, innings: int, opp: str):
        s = side.setdefault(user, {"runs": 0, "inn": 0, "vs": {}})
        s["runs"] += runs
        s["inn"] += innings
        prev_r, prev_i = s["vs"].get(opp, (0, 0))
        s["vs"][opp] = (prev_r + runs, prev_i + innings)

    for game in games:
        home = (game.get("home_user") or "").lower()
        away = (game.get("away_user") or "").lower()
        innings = game.get("innings_played", 0) or 0
        if not home or not away or innings <= 0:
            continue
        home_score = game.get("home_score", 0)
        away_score = game.get("away_score", 0)
        total_runs += home_score + away_score
        total_innings += 2 * innings

        schedules.setdefault(home, {})[away] = schedules.setdefault(home, {}).get(away, 0) + 1
        schedules.setdefault(away, {})[home] = schedules.setdefault(away, {}).get(home, 0) + 1
        add(defense, home, away_score, innings, away)  # defense = runs allowed (opponent's score)
        add(defense, away, home_score, innings, home)
        add(offense, home, home_score, innings, away)  # offense = runs scored
        add(offense, away, away_score, innings, home)

    league_runs_per_inning = total_runs / total_innings if total_innings else 0.0
    return {
        "schedules": schedules,
        "defense": defense,
        "offense": offense,
        "league_runs_per_inning": league_runs_per_inning,
    }


def build_char_schedules(by_game: dict) -> dict:
    """Per-character opponent schedules, weighted by plate exposure.

    ``by_game`` is the ``/stats?by_user&by_char&by_game`` payload
    (``{game_id: {username: {char: {"Batting": ..., "Pitching": ...}}}}``). For each
    character a user actually appeared with, accumulate the opponents they faced,
    weighted by plate appearances (batting) or batters faced (pitching) — so a
    relief cameo counts far less than a full start. Returns::

        {"batting":  {(user, char): ({opponent: pa}, game_count)},
         "pitching": {(user, char): ({opponent: bf}, game_count)}}

    Usernames are lowercased; character names are kept as the API returns them (the
    same canonical names the lookups use). ``game_count`` (appearances, not exposure)
    drives the schedule-reliability damping, matching the mode-wide path.
    """
    batting: dict[tuple[str, str], tuple[dict[str, int], int]] = {}
    pitching: dict[tuple[str, str], tuple[dict[str, int], int]] = {}

    def add(store, key, opp, weight):
        schedule, games = store.get(key, ({}, 0))
        schedule[opp] = schedule.get(opp, 0) + weight
        store[key] = (schedule, games + 1)

    for users in by_game.values():
        names = [u.lower() for u in users]
        if len(names) != 2:  # only well-formed 1v1 games
            continue
        for username, chars in users.items():
            user = username.lower()
            opp = names[0] if names[1] == user else names[1]
            for char, summary in chars.items():
                bat = summary.get("Batting") or {}
                pa = (
                    (bat.get("summary_at_bats") or 0)
                    + (bat.get("summary_walks_bb") or 0)
                    + (bat.get("summary_walks_hbp") or 0)
                    + (bat.get("summary_sac_flys") or 0)
                )
                if pa > 0:
                    add(batting, (user, char), opp, pa)
                bf = (summary.get("Pitching") or {}).get("batters_faced") or 0
                if bf > 0:
                    add(pitching, (user, char), opp, bf)

    return {"batting": batting, "pitching": pitching}


def char_schedule_effect(
    player: str,
    side_stats: dict[str, dict],
    char_schedule: tuple[dict[str, int], int],
    league_run_rate: float,
    regression_inn: int = OPPONENT_REGRESSION_INN,
) -> tuple[float, int]:
    """Opponent effect for one character's slate (from :func:`build_char_schedules`).

    ``char_schedule`` is ``({opponent: exposure_weight}, game_count)``. The opponent
    rates are exposure-weighted (PA/BF) rather than game-weighted, but the returned
    count is game *appearances* so the caller's reliability damping stays in game
    units. Returns ``(effect, game_count)`` for ``opponent_adjusted_*``.
    """
    weights, game_count = char_schedule
    effect, _ = loo_schedule_effect(player, side_stats, weights, league_run_rate, regression_inn)
    return effect, game_count


def loo_schedule_effect(
    player: str,
    side_stats: dict[str, dict],
    schedule: dict[str, int],
    league_run_rate: float,
    regression_inn: int = OPPONENT_REGRESSION_INN,
) -> tuple[float, int]:
    """Games-weighted average opponent quality vs league (runs/inning), leave-one-out.

    ``side_stats`` is the ``defense`` map (for BSI) or ``offense`` map (for PSI) from
    :func:`build_matchup_stats`. Each opponent's rate excludes their games against
    ``player`` and is regressed toward league by the leftover innings. Returns
    ``(effect, total_games)``. Sign follows the side: for defense, negative = tough
    pitching faced; for offense, positive = tough hitting faced.
    """
    weighted = 0.0
    total_games = 0
    for opponent, games in schedule.items():
        stats = side_stats.get(opponent)
        if stats is None:
            continue
        runs = stats["runs"]
        innings = stats["inn"]
        seen_runs, seen_inn = stats["vs"].get(player, (0, 0))
        runs -= seen_runs
        innings -= seen_inn
        if innings <= 0:
            rate = league_run_rate
        else:
            reliability = innings / (innings + regression_inn)
            rate = league_run_rate + reliability * (runs / innings - league_run_rate)
        weighted += games * (rate - league_run_rate)
        total_games += games
    if total_games == 0:
        return 0.0, 0
    return weighted / total_games, total_games


def opponent_adjusted_wrc_plus(
    raw_wrc_plus: float,
    schedule_effect: float,
    total_games: int,
    league_run_rate: float,
    transfer_coeff: float = OPPONENT_TRANSFER_COEFF,
    regression_games: int = SCHEDULE_REGRESSION_GAMES,
) -> float:
    """Apply the strength-of-schedule adjustment to a raw wRC+ (-> BSI).

    ``schedule_effect`` is D from :func:`loo_schedule_effect` on the defense map.
    A tougher schedule (D < 0) raises the result; a soft one lowers it. Damped for
    thin schedules via games / (games + regression_games).
    """
    if league_run_rate <= 0 or total_games == 0:
        return raw_wrc_plus
    schedule_reliability = total_games / (total_games + regression_games)
    delta = (schedule_effect / league_run_rate) * 100 * transfer_coeff * schedule_reliability
    return raw_wrc_plus - delta


def opponent_adjusted_pitching_index(
    raw_index: float,
    schedule_effect: float,
    total_games: int,
    league_run_rate: float,
    transfer_coeff: float = OPPONENT_TRANSFER_COEFF,
    regression_games: int = SCHEDULE_REGRESSION_GAMES,
) -> float:
    """Apply the strength-of-schedule adjustment to a raw pitching index (-> PSI).

    ``schedule_effect`` is O from :func:`loo_schedule_effect` on the offense map.
    Facing tougher offenses (O > 0) raises the index; weaker offenses lower it.
    Mirror of :func:`opponent_adjusted_wrc_plus`, but the effect is *added*.
    """
    if league_run_rate <= 0 or total_games == 0:
        return raw_index
    schedule_reliability = total_games / (total_games + regression_games)
    delta = (schedule_effect / league_run_rate) * 100 * transfer_coeff * schedule_reliability
    return raw_index + delta
