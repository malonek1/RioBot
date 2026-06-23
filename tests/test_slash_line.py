import pytest

from helpers.offensive_stat_calcs import calc_slash_line
from models.batting_stats import BattingStats

REQUIRED_DEFAULTS = {
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


def make_batting(**overrides) -> BattingStats:
    """BattingStats with all required fields zeroed, overridable per test."""
    return BattingStats(**{**REQUIRED_DEFAULTS, **overrides})


class TestCalcSlashLine:
    def test_typical_line(self):
        stats = make_batting(
            summary_at_bats=10,
            summary_hits=4,
            summary_singles=2,
            summary_doubles=1,
            summary_triples=0,
            summary_homeruns=1,
            summary_walks_bb=1,
        )
        pa, avg, obp, slg = calc_slash_line(stats)
        assert pa == 11  # 10 AB + 1 BB
        assert avg == pytest.approx(0.4)  # 4/10
        assert obp == pytest.approx(5 / 11)  # (4 hits + 1 BB) / 11 PA
        assert slg == pytest.approx(0.8)  # (2 + 2 + 4) total bases / 10 AB

    def test_hbp_and_sac_fly_count_toward_pa(self):
        stats = make_batting(
            summary_at_bats=3,
            summary_hits=1,
            summary_singles=1,
            summary_walks_bb=1,
            summary_walks_hbp=1,
            summary_sac_flys=1,
        )
        pa, avg, obp, slg = calc_slash_line(stats)
        assert pa == 6  # 3 + 1 + 1 + 1
        assert obp == pytest.approx(3 / 6)  # (1 hit + 1 HBP + 1 BB) / 6 PA

    def test_zero_at_bats_no_division_error(self):
        # Walked every plate appearance: AVG/SLG guard against /0, OBP still computes.
        stats = make_batting(summary_walks_bb=2)
        pa, avg, obp, slg = calc_slash_line(stats)
        assert pa == 2
        assert avg == 0
        assert slg == 0
        assert obp == pytest.approx(1.0)  # 2 walks / 2 PA

    def test_all_zero_is_all_zero(self):
        pa, avg, obp, slg = calc_slash_line(make_batting())
        assert (pa, avg, obp, slg) == (0, 0, 0, 0)

    def test_slugging_weights_extra_base_hits(self):
        # One of each hit type: total bases = 1 + 2 + 3 + 4 = 10 over 4 AB.
        stats = make_batting(
            summary_at_bats=4,
            summary_hits=4,
            summary_singles=1,
            summary_doubles=1,
            summary_triples=1,
            summary_homeruns=1,
        )
        _, avg, _, slg = calc_slash_line(stats)
        assert avg == pytest.approx(1.0)
        assert slg == pytest.approx(2.5)
