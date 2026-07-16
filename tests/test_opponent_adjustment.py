import pytest

from helpers.opponent_adjustment import (
    build_char_schedules,
    build_matchup_stats,
    char_schedule_effect,
    loo_schedule_effect,
    opponent_adjusted_pitching_index,
    opponent_adjusted_wrc_plus,
)


class TestBuildMatchupStats:
    def _log(self):
        return [
            {"home_user": "Alice", "away_user": "Bob", "home_score": 5, "away_score": 3, "innings_played": 9},
            {"home_user": "Bob", "away_user": "Alice", "home_score": 2, "away_score": 4, "innings_played": 9},
        ]

    def test_schedules_lowercased_both_directions(self):
        m = build_matchup_stats(self._log())
        assert m["schedules"]["alice"] == {"bob": 2}
        assert m["schedules"]["bob"] == {"alice": 2}

    def test_defense_is_runs_allowed(self):
        m = build_matchup_stats(self._log())
        # Alice allowed the opponent's score each game: 3 then 2.
        assert m["defense"]["alice"]["runs"] == 5
        assert m["defense"]["alice"]["inn"] == 18
        assert m["defense"]["alice"]["vs"]["bob"] == (5, 18)

    def test_offense_is_runs_scored(self):
        m = build_matchup_stats(self._log())
        assert m["offense"]["alice"]["runs"] == 9  # 5 + 4
        assert m["offense"]["bob"]["runs"] == 5  # 3 + 2

    def test_league_runs_per_inning(self):
        m = build_matchup_stats(self._log())
        assert m["league_runs_per_inning"] == pytest.approx(14 / 36)

    def test_skips_incomplete_games(self):
        log = [
            {"home_user": "alice", "away_user": "", "home_score": 5, "away_score": 3, "innings_played": 9},
            {"home_user": "alice", "away_user": "bob", "home_score": 1, "away_score": 1, "innings_played": 0},
        ]
        m = build_matchup_stats(log)
        assert m["schedules"] == {}
        assert m["league_runs_per_inning"] == 0.0


class TestLooScheduleEffect:
    def _defense(self):
        return {
            # excl "me": (10-5)/(100-20) = 0.0625
            "tough": {"runs": 10, "inn": 100, "vs": {"me": (5, 20)}},
            # excl "me": 50/100 = 0.5 (never played "me")
            "soft": {"runs": 50, "inn": 100, "vs": {}},
        }

    def test_leave_one_out_excludes_player_games(self):
        effect, total = loo_schedule_effect("me", self._defense(), {"tough": 3, "soft": 1}, 0.3, regression_inn=0)
        assert total == 4
        # tough dev = 0.0625-0.3, soft dev = 0.5-0.3
        assert effect == pytest.approx((3 * (0.0625 - 0.3) + 1 * (0.5 - 0.3)) / 4)

    def test_loo_changes_result_vs_no_exclusion(self):
        # A player who never faced "tough" sees its full rate (10/100=0.1), not the LOO 0.0625.
        excl, _ = loo_schedule_effect("me", self._defense(), {"tough": 1}, 0.3, regression_inn=0)
        full, _ = loo_schedule_effect("other", self._defense(), {"tough": 1}, 0.3, regression_inn=0)
        assert excl == pytest.approx(0.0625 - 0.3)
        assert full == pytest.approx(0.1 - 0.3)
        assert excl != full

    def test_unknown_opponents_skipped(self):
        effect, total = loo_schedule_effect("me", self._defense(), {"soft": 2, "ghost": 9}, 0.3, regression_inn=0)
        assert total == 2
        assert effect == pytest.approx(0.5 - 0.3)

    def test_all_innings_excluded_falls_back_to_league(self):
        defense = {"only_me": {"runs": 8, "inn": 20, "vs": {"me": (8, 20)}}}
        effect, total = loo_schedule_effect("me", defense, {"only_me": 3}, 0.3, regression_inn=0)
        assert total == 3
        assert effect == pytest.approx(0.0)  # rate == league -> zero deviation

    def test_shrinkage_pulls_toward_league(self):
        defense = {"soft": {"runs": 50, "inn": 100, "vs": {}}}  # raw 0.5
        effect, _ = loo_schedule_effect("me", defense, {"soft": 1}, 0.3, regression_inn=100)
        # reliability 100/200 = 0.5 -> rate = 0.3 + 0.5*(0.5-0.3) = 0.4
        assert effect == pytest.approx(0.4 - 0.3)

    def test_empty_schedule_is_neutral(self):
        assert loo_schedule_effect("me", {}, {}, 0.3) == (0.0, 0)


class TestBuildCharSchedules:
    def _by_game(self):
        # Two games. Alice runs Bowser both games (vs Bob, then vs Carl); she also
        # rosters Mario only in game 1. Bob pitches with DK in game 1 only.
        def bat(pa):
            return {"summary_at_bats": pa, "summary_walks_bb": 0, "summary_walks_hbp": 0, "summary_sac_flys": 0}

        return {
            "1": {
                "Alice": {"Bowser": {"Batting": bat(4)}, "Mario": {"Batting": bat(3)}},
                "Bob": {"DK": {"Pitching": {"batters_faced": 30}}},
            },
            "2": {
                "Alice": {"Bowser": {"Batting": bat(5)}},
                "Carl": {"DK": {"Pitching": {"batters_faced": 28}}},
            },
        }

    def test_batting_schedule_pa_weighted_per_character(self):
        cs = build_char_schedules(self._by_game())["batting"]
        # Alice/Bowser faced bob (4 PA) and carl (5 PA), across 2 games.
        assert cs[("alice", "Bowser")] == ({"bob": 4, "carl": 5}, 2)
        # Alice/Mario only appeared game 1 (3 PA vs bob).
        assert cs[("alice", "Mario")] == ({"bob": 3}, 1)

    def test_pitching_schedule_bf_weighted(self):
        cs = build_char_schedules(self._by_game())["pitching"]
        assert cs[("bob", "DK")] == ({"alice": 30}, 1)
        assert cs[("carl", "DK")] == ({"alice": 28}, 1)

    def test_zero_appearance_characters_excluded(self):
        by_game = {
            "1": {
                "Alice": {"Bench": {"Batting": {"summary_at_bats": 0, "summary_walks_bb": 0,
                                                "summary_walks_hbp": 0, "summary_sac_flys": 0}}},
                "Bob": {"DK": {"Pitching": {"batters_faced": 0}}},
            }
        }
        cs = build_char_schedules(by_game)
        assert cs["batting"] == {}
        assert cs["pitching"] == {}

    def test_malformed_games_skipped(self):
        by_game = {"1": {"OnlyOne": {"Bowser": {"Batting": {"summary_at_bats": 4}}}}}
        cs = build_char_schedules(by_game)
        assert cs["batting"] == {}


class TestCharScheduleEffect:
    def _defense(self):
        return {"tough": {"runs": 10, "inn": 100, "vs": {}}}  # raw 0.1

    def test_returns_game_count_not_exposure_weight(self):
        # Weight is PA (200), but the returned count is the appearance count (5).
        effect, games = char_schedule_effect("me", self._defense(), ({"tough": 200}, 5), 0.3, regression_inn=0)
        assert games == 5
        assert effect == pytest.approx(0.1 - 0.3)

    def test_exposure_weights_the_average(self):
        defense = {"a": {"runs": 10, "inn": 100, "vs": {}}, "b": {"runs": 50, "inn": 100, "vs": {}}}  # 0.1, 0.5
        effect, _ = char_schedule_effect("me", defense, ({"a": 1, "b": 3}, 2), 0.3, regression_inn=0)
        # heavily weighted toward b: (1*(0.1-0.3) + 3*(0.5-0.3)) / 4
        assert effect == pytest.approx((1 * (0.1 - 0.3) + 3 * (0.5 - 0.3)) / 4)

    def test_empty_schedule_neutral(self):
        assert char_schedule_effect("me", self._defense(), ({}, 0), 0.3) == (0.0, 0)


class TestOpponentAdjustedWrcPlus:
    def test_tough_schedule_raises(self):
        assert opponent_adjusted_wrc_plus(100, -0.085, 4, 0.17, regression_games=0) == pytest.approx(150.0)

    def test_soft_schedule_lowers(self):
        assert opponent_adjusted_wrc_plus(100, 0.085, 4, 0.17, regression_games=0) == pytest.approx(50.0)

    def test_small_sample_damped(self):
        adj = opponent_adjusted_wrc_plus(100, -0.085, 4, 0.17, regression_games=10)
        assert adj == pytest.approx(100 + 50 * (4 / 14))
        assert 100 < adj < 150

    def test_no_games_unchanged(self):
        assert opponent_adjusted_wrc_plus(120, -0.5, 0, 0.17) == 120

    def test_nonpositive_rate_unchanged(self):
        assert opponent_adjusted_wrc_plus(120, -0.5, 10, 0) == 120

    def test_transfer_scales(self):
        full = opponent_adjusted_wrc_plus(100, -0.085, 4, 0.17, transfer_coeff=1.0, regression_games=0)
        half = opponent_adjusted_wrc_plus(100, -0.085, 4, 0.17, transfer_coeff=0.5, regression_games=0)
        assert half - 100 == pytest.approx((full - 100) * 0.5)


class TestOpponentAdjustedPitchingIndex:
    def test_tough_offense_raises(self):
        assert opponent_adjusted_pitching_index(100, 0.085, 4, 0.17, regression_games=0) == pytest.approx(150.0)

    def test_weak_offense_lowers(self):
        assert opponent_adjusted_pitching_index(100, -0.085, 4, 0.17, regression_games=0) == pytest.approx(50.0)

    def test_small_sample_damped(self):
        psi = opponent_adjusted_pitching_index(100, 0.085, 4, 0.17, regression_games=10)
        assert psi == pytest.approx(100 + 50 * (4 / 14))

    def test_no_games_unchanged(self):
        assert opponent_adjusted_pitching_index(120, 0.5, 0, 0.17) == 120

    def test_nonpositive_rate_unchanged(self):
        assert opponent_adjusted_pitching_index(120, 0.5, 10, 0) == 120
