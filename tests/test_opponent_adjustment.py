import pytest

from helpers.opponent_adjustment import (
    build_schedules,
    offense_runs_above_league,
    opponent_adjusted_pitching_index,
    opponent_adjusted_wrc_plus,
    schedule_offense,
    schedule_run_prevention,
    shrunk_offense,
    shrunk_run_prevention,
)
from models.batting_stats import BattingStats
from models.pitching_stats import PitchingStats

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
        assert build_schedules(games) == {"alice": {"bob": 1}, "bob": {"alice": 1}}

    def test_empty_log(self):
        assert build_schedules([]) == {}


class TestShrunkRunPrevention:
    def test_zero_batters_faced_returns_league(self):
        assert shrunk_run_prevention(make_pitching(), 0.17) == 0.17

    def test_small_sample_pulled_toward_league(self):
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
        adj = opponent_adjusted_wrc_plus(100, -0.085, 4, 0.17, regression_games=0)
        assert adj == pytest.approx(150.0)

    def test_soft_schedule_lowers_wrc(self):
        adj = opponent_adjusted_wrc_plus(100, 0.085, 4, 0.17, regression_games=0)
        assert adj == pytest.approx(50.0)

    def test_small_sample_is_damped(self):
        adj = opponent_adjusted_wrc_plus(100, -0.085, 4, 0.17, regression_games=10)
        assert adj == pytest.approx(100 + 50 * (4 / 14))
        assert 100 < adj < 150

    def test_no_games_leaves_wrc_unchanged(self):
        assert opponent_adjusted_wrc_plus(120, -0.5, 0, 0.17) == 120

    def test_nonpositive_league_rpa_leaves_wrc_unchanged(self):
        assert opponent_adjusted_wrc_plus(120, -0.5, 10, 0) == 120

    def test_transfer_coefficient_scales_adjustment(self):
        full = opponent_adjusted_wrc_plus(100, -0.085, 4, 0.17, transfer_coeff=1.0, regression_games=0)
        half = opponent_adjusted_wrc_plus(100, -0.085, 4, 0.17, transfer_coeff=0.5, regression_games=0)
        assert half - 100 == pytest.approx((full - 100) * 0.5)


class TestShrunkOffense:
    def test_zero_pa_is_zero(self):
        assert shrunk_offense(make_batting(), 0.3, 0.85) == 0.0

    def test_no_regression_equals_raw_offense(self):
        masher = make_batting(summary_at_bats=100, summary_hits=40, summary_homeruns=40)
        raw = offense_runs_above_league(masher, 0.3, 0.85)
        assert shrunk_offense(masher, 0.3, 0.85, regression_pa=0) == pytest.approx(raw)

    def test_small_sample_pulled_toward_zero(self):
        masher = make_batting(summary_at_bats=10, summary_hits=4, summary_homeruns=4)
        raw = offense_runs_above_league(masher, 0.3, 0.85)
        shrunk = shrunk_offense(masher, 0.3, 0.85, regression_pa=100)
        assert abs(shrunk) < abs(raw)


class TestScheduleOffense:
    def test_games_weighted_average_relative_to_league(self):
        strong = make_batting(summary_at_bats=10, summary_hits=10, summary_homeruns=10)  # high wOBA
        weak = make_batting(summary_at_bats=10, summary_hits=0)  # wOBA 0
        table = {"strong": strong, "weak": weak}
        league_woba, scale = 0.8, 1.0
        o, total = schedule_offense({"strong": 3, "weak": 1}, table, league_woba, scale, regression_pa=0)
        expected = (
            3 * offense_runs_above_league(strong, league_woba, scale)
            + 1 * offense_runs_above_league(weak, league_woba, scale)
        ) / 4
        assert total == 4
        assert o == pytest.approx(expected)

    def test_unknown_opponents_are_skipped(self):
        strong = make_batting(summary_at_bats=10, summary_hits=10, summary_homeruns=10)
        o, total = schedule_offense({"strong": 3, "ghost": 5}, {"strong": strong}, 0.8, 1.0, regression_pa=0)
        assert total == 3
        assert o == pytest.approx(offense_runs_above_league(strong, 0.8, 1.0))

    def test_empty_schedule_is_neutral(self):
        assert schedule_offense({}, {}, 0.8, 1.0) == (0.0, 0)


class TestOpponentAdjustedPitchingIndex:
    def test_tough_offense_raises_index(self):
        # O = +0.085 over 0.17 league => +50 points; full reliability.
        psi = opponent_adjusted_pitching_index(100, 0.085, 4, 0.17, regression_games=0)
        assert psi == pytest.approx(150.0)

    def test_weak_offense_lowers_index(self):
        psi = opponent_adjusted_pitching_index(100, -0.085, 4, 0.17, regression_games=0)
        assert psi == pytest.approx(50.0)

    def test_small_sample_is_damped(self):
        psi = opponent_adjusted_pitching_index(100, 0.085, 4, 0.17, regression_games=10)
        assert psi == pytest.approx(100 + 50 * (4 / 14))
        assert 100 < psi < 150

    def test_no_games_leaves_index_unchanged(self):
        assert opponent_adjusted_pitching_index(120, 0.5, 0, 0.17) == 120

    def test_nonpositive_league_leaves_index_unchanged(self):
        assert opponent_adjusted_pitching_index(120, 0.5, 10, 0) == 120
