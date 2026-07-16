"""Run-scale batting and pitching metrics: wOBA, wRC+, and the pitching
run-prevention index, plus the league baseline they share. Pure functions —
no I/O — unit-tested offline.

These are the *unadjusted* metrics. The strength-of-schedule layer that turns
them into BSI / PSI lives in helpers/opponent_adjustment.py.
"""

from models.batting_stats import BattingStats
from models.pitching_stats import PitchingStats
from resources.stat_constants import DEFAULT_LEAGUE_RUNS_PER_PA, LINEAR_WEIGHTS


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


def woba_scale(overall_stats: BattingStats) -> float:
    """OBP/wOBA for a reference population — converts a wOBA gap into runs/PA."""
    pa = (
        overall_stats.summary_at_bats
        + overall_stats.summary_walks_bb
        + overall_stats.summary_walks_hbp
        + overall_stats.summary_sac_flys
    )
    if pa == 0:
        return 0.0
    obp = (overall_stats.summary_hits + overall_stats.summary_walks_hbp + overall_stats.summary_walks_bb) / pa
    woba = calc_woba(overall_stats)
    if woba == 0:
        return 0.0
    return obp / woba


def calc_wrc_plus(
    stats: BattingStats,
    overall_stats: BattingStats,
    league_runs_per_pa: float = DEFAULT_LEAGUE_RUNS_PER_PA,
) -> float:
    """wRC+ for ``stats`` relative to the reference population ``overall_stats``.

    100 is the reference average by construction (player wOBA == overall wOBA).
    """
    scale = woba_scale(overall_stats)
    if scale <= 0 or league_runs_per_pa <= 0:
        return 0.0

    overall_woba = calc_woba(overall_stats)
    player_woba = calc_woba(stats)

    return (((player_woba - overall_woba) / scale + league_runs_per_pa) / league_runs_per_pa) * 100


def calc_pitching_index(
    stats: PitchingStats,
    reference_stats: PitchingStats,
    league_runs_per_pa: float = DEFAULT_LEAGUE_RUNS_PER_PA,
) -> float:
    """Run-prevention index vs ``reference_stats``. 100 = reference average,
    higher = better (mirror of wRC+). Uses runs allowed per batter faced."""
    if league_runs_per_pa <= 0 or stats.batters_faced == 0 or reference_stats.batters_faced == 0:
        return 0.0
    ra = stats.runs_allowed / stats.batters_faced
    ra_ref = reference_stats.runs_allowed / reference_stats.batters_faced
    return ((league_runs_per_pa + (ra_ref - ra)) / league_runs_per_pa) * 100


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
