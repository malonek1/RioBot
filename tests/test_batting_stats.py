import pytest
from pydantic import ValidationError

from models.batting_stats import BattingStats

REQUIRED = {
    "summary_at_bats": 1,
    "summary_hits": 1,
    "summary_singles": 1,
    "summary_doubles": 0,
    "summary_triples": 0,
    "summary_homeruns": 0,
    "summary_rbi": 0,
    "summary_strikeouts": 0,
    "summary_walks_bb": 0,
    "summary_walks_hbp": 0,
    "summary_sac_flys": 0,
}


class TestBattingStatsValidation:
    def test_extra_fields_are_ignored(self):
        # The API sends more fields than we model; extra="ignore" must not raise.
        stats = BattingStats.model_validate({**REQUIRED, "some_future_field": 999})
        assert not hasattr(stats, "some_future_field")
        assert stats.summary_at_bats == 1

    def test_missing_required_field_raises(self):
        incomplete = dict(REQUIRED)
        del incomplete["summary_at_bats"]
        with pytest.raises(ValidationError):
            BattingStats.model_validate(incomplete)

    def test_optional_fields_default(self):
        stats = BattingStats.model_validate(REQUIRED)
        assert stats.perfect_hits == 0
        assert stats.nice_hits == 0
        assert stats.sour_hits == 0
        assert stats.star_hits == 0

    def test_string_numbers_coerced_to_int(self):
        # Pydantic coerces numeric strings; the API has historically sent both.
        stats = BattingStats.model_validate({**REQUIRED, "summary_at_bats": "42"})
        assert stats.summary_at_bats == 42
