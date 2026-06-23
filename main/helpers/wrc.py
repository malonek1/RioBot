"""Pure calculation logic for wOBA, wRC+, and the opponent-quality (strength-of-
schedule) adjustment. No I/O — everything here is unit-tested offline.

The adjustment models run production additively on the run scale:

    observed batter runs/PA ~= L + (batter skill) + (opponent run-prevention vs L)

where L is league runs/PA. Subtracting the opponents' run-prevention effect
isolates batter skill, which collapses to a clean wRC+ shift:

    adjusted wRC+ = raw wRC+ - (D / L) * 100 * transfer * schedule_reliability

D is the games-weighted average of each opponent's runs-allowed-per-PA relative
to league (D < 0 means a tougher-than-average schedule, which raises wRC+).
"""

from models.batting_stats import BattingStats
from models.pitching_stats import PitchingStats
from resources.stat_constants import (
    DEFAULT_LEAGUE_RUNS_PER_PA,
    LINEAR_WEIGHTS,
    OPPONENT_REGRESSION_BF,
    OPPONENT_TRANSFER_COEFF,
    SCHEDULE_REGRESSION_GAMES,
)


def calc_woba(stats: BattingStats) -> float:
    """Weighted on-base average: linear-weighted offensive value per plate appearance."""
    pa = stats.summary_at_bats + stats.summary_walks_bb + stats.summary_walks_hbp + stats.summary_sac_flys
    if pa == 0:
        return 0.0
    weighted = (
        stats.summary_singles * LINEAR_WEIGHTS["singles"]
        + stats.summary_doubles * LINEAR_WEIGHTS["doubles"]
        + stats.summary_triples * LINEAR_WEIGHTS["triples"]
        + stats.summary_homeruns * LINEAR_WEIGHTS["homeruns"]
        + stats.summary_walks_bb * LINEAR_WEIGHTS["walks_bb"]
        + stats.summary_walks_hbp * LINEAR_WEIGHTS["walks_hbp"]
    )
    return weighted / pa


def calc_wrc_plus(
    stats: BattingStats,
    overall_stats: BattingStats,
    league_runs_per_pa: float = DEFAULT_LEAGUE_RUNS_PER_PA,
) -> float:
    """wRC+ for ``stats`` relative to the reference population ``overall_stats``.

    100 is the reference average by construction (player wOBA == overall wOBA).
    """
    overall_pa = (
        overall_stats.summary_at_bats
        + overall_stats.summary_walks_bb
        + overall_stats.summary_walks_hbp
        + overall_stats.summary_sac_flys
    )
    if overall_pa == 0 or league_runs_per_pa <= 0:
        return 0.0

    overall_obp = (
        overall_stats.summary_hits + overall_stats.summary_walks_hbp + overall_stats.summary_walks_bb
    ) / overall_pa

    overall_woba = calc_woba(overall_stats)
    if overall_woba == 0:
        return 0.0

    player_woba = calc_woba(stats)
    woba_scale = overall_obp / overall_woba

    return (((player_woba - overall_woba) / woba_scale + league_runs_per_pa) / league_runs_per_pa) * 100


def league_runs_per_pa(pitching_table: dict[str, PitchingStats]) -> float:
    """League runs allowed per batter faced, pooled over every pitcher in a mode.

    By symmetry this equals league runs *scored* per PA, so it doubles as the
    wRC+ denominator. Falls back to the default constant when the table is empty.
    """
    total_runs = sum(p.runs_allowed for p in pitching_table.values())
    total_bf = sum(p.batters_faced for p in pitching_table.values())
    if total_bf == 0:
        return DEFAULT_LEAGUE_RUNS_PER_PA
    return total_runs / total_bf


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
    """Apply the strength-of-schedule adjustment to a raw wRC+.

    ``schedule_effect`` is D from :func:`schedule_run_prevention`. A tougher
    schedule (D < 0) raises the result; a soft one lowers it. The shift is damped
    for thin schedules via games / (games + regression_games).
    """
    if league_rpa <= 0 or total_games == 0:
        return raw_wrc_plus
    schedule_reliability = total_games / (total_games + regression_games)
    delta = (schedule_effect / league_rpa) * 100 * transfer_coeff * schedule_reliability
    return raw_wrc_plus - delta
