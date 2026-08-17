from helpers.utils import ordinal, strip_non_alphanumeric


class TestOrdinal:
    def test_basic_suffixes(self):
        assert ordinal(1) == "1st"
        assert ordinal(2) == "2nd"
        assert ordinal(3) == "3rd"
        assert ordinal(4) == "4th"
        assert ordinal(5) == "5th"

    def test_teens_are_th(self):
        # 11/12/13 are the special case: "th" despite ending in 1/2/3.
        assert ordinal(11) == "11th"
        assert ordinal(12) == "12th"
        assert ordinal(13) == "13th"

    def test_twenties_resume_normal_suffixes(self):
        assert ordinal(21) == "21st"
        assert ordinal(22) == "22nd"
        assert ordinal(23) == "23rd"
        assert ordinal(24) == "24th"

    def test_hundred_teens_are_th(self):
        assert ordinal(111) == "111th"
        assert ordinal(112) == "112th"
        assert ordinal(113) == "113th"
        assert ordinal(101) == "101st"


class TestStripNonAlphanumeric:
    def test_removes_punctuation_and_spaces(self):
        assert strip_non_alphanumeric("Hello, World!") == "helloworld"

    def test_lowercases(self):
        assert strip_non_alphanumeric("ABC") == "abc"

    def test_keeps_digits(self):
        assert strip_non_alphanumeric("ABC-123") == "abc123"

    def test_strips_underscores_and_dashes(self):
        assert strip_non_alphanumeric("  a-b_c  ") == "abc"

    def test_empty_string(self):
        assert strip_non_alphanumeric("") == ""
