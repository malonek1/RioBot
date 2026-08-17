from helpers.team_sorter import (
    get_character_rank,
    sort_team_by_tier,
    sort_teams_by_tier_exclude_captain,
)
from resources.characters import Char


class TestGetCharacterRank:
    def test_char_enum_member(self):
        assert get_character_rank(Char.BOWSER) == 1
        assert get_character_rank(Char.GOOMBA) == 38

    def test_raw_value_in_dict(self):
        assert get_character_rank(Char.MARIO.value) == 13

    def test_unknown_character_sorts_last(self):
        assert get_character_rank("Not A Character") == 99


class TestSortTeamByTier:
    def test_sorts_in_place_by_rank(self):
        team = [Char.GOOMBA, Char.BOWSER, Char.MARIO]
        sort_team_by_tier(team)
        # Bowser (1) < Mario (13) < Goomba (38)
        assert team == [Char.BOWSER, Char.MARIO, Char.GOOMBA]


class TestSortTeamsExcludeCaptain:
    def test_captain_stays_first(self):
        # Goomba is the captain (worst rank) but must remain at index 0.
        teams = [[Char.GOOMBA, Char.MARIO, Char.BOWSER]]
        result = sort_teams_by_tier_exclude_captain(teams)
        assert result[0][0] == Char.GOOMBA
        # Remaining players sorted: Bowser (1) before Mario (13).
        assert result[0][1:] == [Char.BOWSER, Char.MARIO]

    def test_sorts_each_team_independently(self):
        teams = [
            [Char.MARIO, Char.GOOMBA, Char.BOWSER],
            [Char.BOWSER, Char.GOOMBA, Char.MARIO],
        ]
        result = sort_teams_by_tier_exclude_captain(teams)
        assert result[0][0] == Char.MARIO
        assert result[1][0] == Char.BOWSER
        assert result[0][1:] == [Char.BOWSER, Char.GOOMBA]
        assert result[1][1:] == [Char.MARIO, Char.GOOMBA]
