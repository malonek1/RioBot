"""Strength-of-schedule (opponent-quality) adjustment that turns raw wRC+ and the
pitching index into BSI / PSI. Pure functions — no I/O — unit-tested offline.

The adjustment is additive on the run scale: facing tougher competition raises
the skill number.

    BSI = wRC+          - (D / L) * 100 * transfer * schedule_reliability
    PSI = pitching index + (O / L) * 100 * transfer * schedule_reliability

where L is league runs/PA, D is the games-weighted average of each opponent's
run prevention vs league (so a tough schedule, D < 0, raises BSI), and O is the
games-weighted average of each opponent's offense vs league (a tough schedule,
O > 0, raises PSI). Opponent offense is measured by wOBA, which the reliability
experiment (scratch/metric_reliability.py) showed beats runs as a skill signal.
"""

from helpers.sabermetrics import calc_woba
from models.batting_stats import BattingStats
from models.pitching_stats import PitchingStats
from resources.stat_constants import (
    OPPONENT_REGRESSION_BF,
    OPPONENT_REGRESSION_PA,
    OPPONENT_TRANSFER_COEFF,
    SCHEDULE_REGRESSION_GAMES,
)


def build_schedules(games: list[dict]) -> dict[str, dict[str, int]]:
    """From a mode's game log, build every user's opponent schedule in one pass.

    Returns ``{user: {opponent: games_played}}`` with all usernames lowercased so
    lookups line up with the opponent stat tables. Games missing either user
    are skipped.
    """
    schedules: dict[str, dict[str, int]] = {}
    for game in games:
        home = (game.get("home_user") or "").lower()
        away = (game.get("away_user") or "").lower()
        if not home or not away:
            continue
        schedules.setdefault(home, {})
        schedules.setdefault(away, {})
        schedules[home][away] = schedules[home].get(away, 0) + 1
        schedules[away][home] = schedules[away].get(home, 0) + 1
    return schedules


# --- Batting adjustment (BSI): adjust for opponents' run prevention ----------


def shrunk_run_prevention(
    stats: PitchingStats,
    league_rpa: float,
    regression_bf: int = OPPONENT_REGRESSION_BF,
) -> float:
    """An opponent's runs allowed per PA, regressed toward league by sample size.

    A pitcher with few batters faced is pulled toward ``league_rpa`` so small
    samples can't read as elite or terrible.
    """
    if stats.batters_faced == 0:
        return league_rpa
    raw = stats.runs_allowed / stats.batters_faced
    reliability = stats.batters_faced / (stats.batters_faced + regression_bf)
    return league_rpa + reliability * (raw - league_rpa)


def schedule_run_prevention(
    opponent_games: dict[str, int],
    pitching_table: dict[str, PitchingStats],
    league_rpa: float,
    regression_bf: int = OPPONENT_REGRESSION_BF,
) -> tuple[float, int]:
    """Games-weighted average opponent run-prevention relative to league (D).

    ``opponent_games`` maps opponent username -> games played against them.
    Opponents missing from ``pitching_table`` are skipped (and don't count toward
    the games total). Returns ``(D, total_games)``; D < 0 is a tough schedule.
    """
    weighted = 0.0
    total_games = 0
    for opponent, games in opponent_games.items():
        opp_stats = pitching_table.get(opponent)
        if opp_stats is None:
            continue
        opp_rpa = shrunk_run_prevention(opp_stats, league_rpa, regression_bf)
        weighted += games * (opp_rpa - league_rpa)
        total_games += games
    if total_games == 0:
        return 0.0, 0
    return weighted / total_games, total_games


def opponent_adjusted_wrc_plus(
    raw_wrc_plus: float,
    schedule_effect: float,
    total_games: int,
    league_rpa: float,
    transfer_coeff: float = OPPONENT_TRANSFER_COEFF,
    regression_games: int = SCHEDULE_REGRESSION_GAMES,
) -> float:
    """Apply the strength-of-schedule adjustment to a raw wRC+ (-> BSI).

    ``schedule_effect`` is D from :func:`schedule_run_prevention`. A tougher
    schedule (D < 0) raises the result; a soft one lowers it. The shift is damped
    for thin schedules via games / (games + regression_games).
    """
    if league_rpa <= 0 or total_games == 0:
        return raw_wrc_plus
    schedule_reliability = total_games / (total_games + regression_games)
    delta = (schedule_effect / league_rpa) * 100 * transfer_coeff * schedule_reliability
    return raw_wrc_plus - delta


# --- Pitching adjustment (PSI): adjust for opponents' offense ----------------


def offense_runs_above_league(stats: BattingStats, league_woba: float, scale: float) -> float:
    """A batter's offensive value above league average, in runs per PA."""
    if scale <= 0:
        return 0.0
    return (calc_woba(stats) - league_woba) / scale


def shrunk_offense(
    stats: BattingStats,
    league_woba: float,
    scale: float,
    regression_pa: int = OPPONENT_REGRESSION_PA,
) -> float:
    """An opponent's offensive value (runs/PA above league), regressed toward
    league average by plate-appearance sample size."""
    pa = stats.summary_at_bats + stats.summary_walks_bb + stats.summary_walks_hbp + stats.summary_sac_flys
    if pa == 0:
        return 0.0
    reliability = pa / (pa + regression_pa)
    return reliability * offense_runs_above_league(stats, league_woba, scale)


def schedule_offense(
    opponent_games: dict[str, int],
    batting_table: dict[str, BattingStats],
    league_woba: float,
    scale: float,
    regression_pa: int = OPPONENT_REGRESSION_PA,
) -> tuple[float, int]:
    """Games-weighted average offensive quality of the batters faced (O), in
    runs/PA above league. Opponents missing from ``batting_table`` are skipped.
    Returns ``(O, total_games)``; O > 0 is a tough (high-offense) schedule."""
    weighted = 0.0
    total_games = 0
    for opponent, games in opponent_games.items():
        opp_stats = batting_table.get(opponent)
        if opp_stats is None:
            continue
        weighted += games * shrunk_offense(opp_stats, league_woba, scale, regression_pa)
        total_games += games
    if total_games == 0:
        return 0.0, 0
    return weighted / total_games, total_games


def opponent_adjusted_pitching_index(
    raw_index: float,
    schedule_offense_effect: float,
    total_games: int,
    league_rpa: float,
    transfer_coeff: float = OPPONENT_TRANSFER_COEFF,
    regression_games: int = SCHEDULE_REGRESSION_GAMES,
) -> float:
    """Apply the strength-of-schedule adjustment to a raw pitching index (-> PSI).

    ``schedule_offense_effect`` is O from :func:`schedule_offense`. Facing tougher
    offenses (O > 0) raises the index; weaker offenses lower it. Mirror of
    :func:`opponent_adjusted_wrc_plus`, but the schedule effect is *added*.
    """
    if league_rpa <= 0 or total_games == 0:
        return raw_index
    schedule_reliability = total_games / (total_games + regression_games)
    delta = (schedule_offense_effect / league_rpa) * 100 * transfer_coeff * schedule_reliability
    return raw_index + delta
