import pytest

from helpers.wrc import (
    build_schedules,
    calc_woba,
    calc_wrc_plus,
    league_runs_per_pa,
    opponent_adjusted_wrc_plus,
    schedule_run_prevention,
    shrunk_run_prevention,
)
from models.batting_stats import BattingStats
from models.pitching_stats import PitchingStats
from resources.stat_constants import DEFAULT_LEAGUE_RUNS_PER_PA, LINEAR_WEIGHTS

BATTING_DEFAULTS = {
    "summary_at_bats": 0,
    "summary_hits": 0,
    "summary_singles": 0,
    "summary_doubles": 0,
    "summary_triples": 0,
    "summary_homeruns": 0,
    "summary_rbi": 0,
    "summary_strikeouts": 0,
    "summary_walks_bb": 0,
    "summary_walks_hbp": 0,
    "summary_sac_flys": 0,
}

PITCHING_DEFAULTS = {
    "batters_faced": 0,
    "outs_pitched": 0,
    "hits_allowed": 0,
    "runs_allowed": 0,
    "strikeouts_pitched": 0,
    "walks_bb": 0,
    "walks_hbp": 0,
}


def make_batting(**overrides) -> BattingStats:
    return BattingStats(**{**BATTING_DEFAULTS, **overrides})


def make_pitching(**overrides) -> PitchingStats:
    return PitchingStats(**{**PITCHING_DEFAULTS, **overrides})


class TestCalcWoba:
    def test_no_plate_appearances_is_zero(self):
        assert calc_woba(make_batting()) == 0.0

    def test_single_over_one_pa_equals_single_weight(self):
        stats = make_batting(summary_at_bats=1, summary_hits=1, summary_singles=1)
        assert calc_woba(stats) == pytest.approx(LINEAR_WEIGHTS["singles"])

    def test_walks_count_in_pa_denominator(self):
        # 1 single + 1 walk over 2 PA (1 AB + 1 BB).
        stats = make_batting(summary_at_bats=1, summary_hits=1, summary_singles=1, summary_walks_bb=1)
        expected = (LINEAR_WEIGHTS["singles"] + LINEAR_WEIGHTS["walks_bb"]) / 2
        assert calc_woba(stats) == pytest.approx(expected)


class TestCalcWrcPlus:
    def _population(self) -> BattingStats:
        return make_batting(
            summary_at_bats=100,
            summary_hits=30,
            summary_singles=20,
            summary_doubles=5,
            summary_triples=1,
            summary_homeruns=4,
            summary_walks_bb=10,
            summary_walks_hbp=2,
            summary_sac_flys=1,
        )

    def test_player_equal_to_population_is_100(self):
        pop = self._population()
        assert calc_wrc_plus(pop, pop) == pytest.approx(100.0)

    def test_better_than_population_exceeds_100(self):
        pop = self._population()
        masher = make_batting(
            summary_at_bats=100, summary_hits=50, summary_singles=20, summary_homeruns=30, summary_walks_bb=15
        )
        assert calc_wrc_plus(masher, pop) > 100

    def test_worse_than_population_below_100(self):
        pop = self._population()
        scrub = make_batting(summary_at_bats=100, summary_hits=10, summary_singles=10)
        assert calc_wrc_plus(scrub, pop) < 100

    def test_empty_population_is_zero(self):
        assert calc_wrc_plus(self._population(), make_batting()) == 0.0

    def test_nonpositive_league_rpa_is_zero(self):
        pop = self._population()
        assert calc_wrc_plus(pop, pop, league_runs_per_pa=0) == 0.0


class TestLeagueRunsPerPa:
    def test_pools_runs_over_batters_faced(self):
        table = {
            "a": make_pitching(runs_allowed=10, batters_faced=100),
            "b": make_pitching(runs_allowed=20, batters_faced=100),
        }
        assert league_runs_per_pa(table) == pytest.approx(0.15)

    def test_empty_table_falls_back_to_default(self):
        assert league_runs_per_pa({}) == DEFAULT_LEAGUE_RUNS_PER_PA


class TestShrunkRunPrevention:
    def test_zero_batters_faced_returns_league(self):
        assert shrunk_run_prevention(make_pitching(), 0.17) == 0.17

    def test_small_sample_pulled_toward_league(self):
        # raw 0.0 over only 10 BF: regressed most of the way back to 0.17.
        result = shrunk_run_prevention(make_pitching(runs_allowed=0, batters_faced=10), 0.17, regression_bf=100)
        assert 0.0 < result < 0.17
        assert result == pytest.approx(0.17 + (10 / 110) * (0.0 - 0.17))

    def test_large_sample_approaches_raw(self):
        result = shrunk_run_prevention(make_pitching(runs_allowed=0, batters_faced=100000), 0.17, regression_bf=100)
        assert result == pytest.approx(0.0, abs=1e-3)


class TestScheduleRunPrevention:
    def test_games_weighted_average_relative_to_league(self):
        table = {
            "tough": make_pitching(runs_allowed=0, batters_faced=100),
            "soft": make_pitching(runs_allowed=34, batters_faced=100),
        }
        # regression_bf=0 so shrunk == raw, keeping the arithmetic exact.
        d, total = schedule_run_prevention({"tough": 3, "soft": 1}, table, 0.17, regression_bf=0)
        assert total == 4
        assert d == pytest.approx(((3 * -0.17) + (1 * 0.17)) / 4)

    def test_unknown_opponents_are_skipped(self):
        table = {"tough": make_pitching(runs_allowed=0, batters_faced=100)}
        d, total = schedule_run_prevention({"tough": 3, "ghost": 5}, table, 0.17, regression_bf=0)
        assert total == 3
        assert d == pytest.approx(-0.17)

    def test_empty_schedule_is_neutral(self):
        assert schedule_run_prevention({}, {}, 0.17) == (0.0, 0)


class TestOpponentAdjustedWrcPlus:
    def test_tough_schedule_raises_wrc(self):
        # D = -0.085 over 0.17 league => -50 raw points; full reliability.
        adj = opponent_adjusted_wrc_plus(100, -0.085, 4, 0.17, regression_games=0)
        assert adj == pytest.approx(150.0)

    def test_soft_schedule_lowers_wrc(self):
        adj = opponent_adjusted_wrc_plus(100, 0.085, 4, 0.17, regression_games=0)
        assert adj == pytest.approx(50.0)

    def test_small_sample_is_damped(self):
        # Same effect, but only 4 games against a 10-game regression constant.
        adj = opponent_adjusted_wrc_plus(100, -0.085, 4, 0.17, regression_games=10)
        assert adj == pytest.approx(100 + 50 * (4 / 14))
        assert 100 < adj < 150  # moved toward, but not all the way to, the full adjustment

    def test_no_games_leaves_wrc_unchanged(self):
        assert opponent_adjusted_wrc_plus(120, -0.5, 0, 0.17) == 120

    def test_nonpositive_league_rpa_leaves_wrc_unchanged(self):
        assert opponent_adjusted_wrc_plus(120, -0.5, 10, 0) == 120

    def test_transfer_coefficient_scales_adjustment(self):
        full = opponent_adjusted_wrc_plus(100, -0.085, 4, 0.17, transfer_coeff=1.0, regression_games=0)
        half = opponent_adjusted_wrc_plus(100, -0.085, 4, 0.17, transfer_coeff=0.5, regression_games=0)
        assert half - 100 == pytest.approx((full - 100) * 0.5)


class TestBuildSchedules:
    def test_counts_opponents_both_directions_and_lowercases(self):
        games = [
            {"home_user": "Alice", "away_user": "Bob"},
            {"home_user": "bob", "away_user": "alice"},
            {"home_user": "Alice", "away_user": "Carol"},
        ]
        schedules = build_schedules(games)
        assert schedules["alice"] == {"bob": 2, "carol": 1}
        assert schedules["bob"] == {"alice": 2}
        assert schedules["carol"] == {"alice": 1}

    def test_skips_games_missing_a_user(self):
        games = [
            {"home_user": "alice", "away_user": ""},
            {"home_user": None, "away_user": "bob"},
            {"home_user": "alice", "away_user": "bob"},
        ]
        schedules = build_schedules(games)
        assert schedules == {"alice": {"bob": 1}, "bob": {"alice": 1}}

    def test_empty_log(self):
        assert build_schedules([]) == {}
