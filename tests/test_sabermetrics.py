import pytest

from helpers.sabermetrics import calc_pitching_index, calc_woba, calc_wrc_plus, league_runs_per_pa, woba_scale
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


def population() -> BattingStats:
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


class TestWobaScale:
    def test_empty_population_is_zero(self):
        assert woba_scale(make_batting()) == 0.0

    def test_equals_obp_over_woba(self):
        pop = population()
        pa = 100 + 10 + 2 + 1
        obp = (30 + 2 + 10) / pa
        assert woba_scale(pop) == pytest.approx(obp / calc_woba(pop))


class TestCalcWrcPlus:
    def test_player_equal_to_population_is_100(self):
        pop = population()
        assert calc_wrc_plus(pop, pop) == pytest.approx(100.0)

    def test_better_than_population_exceeds_100(self):
        masher = make_batting(
            summary_at_bats=100, summary_hits=50, summary_singles=20, summary_homeruns=30, summary_walks_bb=15
        )
        assert calc_wrc_plus(masher, population()) > 100

    def test_worse_than_population_below_100(self):
        scrub = make_batting(summary_at_bats=100, summary_hits=10, summary_singles=10)
        assert calc_wrc_plus(scrub, population()) < 100

    def test_empty_population_is_zero(self):
        assert calc_wrc_plus(population(), make_batting()) == 0.0

    def test_nonpositive_league_rpa_is_zero(self):
        pop = population()
        assert calc_wrc_plus(pop, pop, league_runs_per_pa=0) == 0.0


class TestCalcPitchingIndex:
    def test_pitcher_equal_to_reference_is_100(self):
        ref = make_pitching(runs_allowed=17, batters_faced=100)
        assert calc_pitching_index(ref, ref, 0.17) == pytest.approx(100.0)

    def test_better_run_prevention_exceeds_100(self):
        ref = make_pitching(runs_allowed=17, batters_faced=100)
        good = make_pitching(runs_allowed=10, batters_faced=100)
        assert calc_pitching_index(good, ref, 0.17) > 100

    def test_worse_run_prevention_below_100(self):
        ref = make_pitching(runs_allowed=17, batters_faced=100)
        bad = make_pitching(runs_allowed=25, batters_faced=100)
        assert calc_pitching_index(bad, ref, 0.17) < 100

    def test_exact_value(self):
        # ra=0.10 vs ref ra=0.17, L=0.17 -> (0.17 + 0.07)/0.17 * 100
        ref = make_pitching(runs_allowed=17, batters_faced=100)
        good = make_pitching(runs_allowed=10, batters_faced=100)
        assert calc_pitching_index(good, ref, 0.17) == pytest.approx((0.17 + 0.07) / 0.17 * 100)

    def test_zero_batters_faced_is_zero(self):
        ref = make_pitching(runs_allowed=17, batters_faced=100)
        assert calc_pitching_index(make_pitching(), ref, 0.17) == 0.0

    def test_empty_reference_is_zero(self):
        good = make_pitching(runs_allowed=10, batters_faced=100)
        assert calc_pitching_index(good, make_pitching(), 0.17) == 0.0

    def test_nonpositive_league_is_zero(self):
        ref = make_pitching(runs_allowed=17, batters_faced=100)
        good = make_pitching(runs_allowed=10, batters_faced=100)
        assert calc_pitching_index(good, ref, 0) == 0.0


class TestLeagueRunsPerPa:
    def test_pools_runs_over_batters_faced(self):
        table = {
            "a": make_pitching(runs_allowed=10, batters_faced=100),
            "b": make_pitching(runs_allowed=20, batters_faced=100),
        }
        assert league_runs_per_pa(table) == pytest.approx(0.15)

    def test_empty_table_falls_back_to_default(self):
        assert league_runs_per_pa({}) == DEFAULT_LEAGUE_RUNS_PER_PA
