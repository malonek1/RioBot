import re


def strip_non_alphanumeric(string: str):
    return re.sub(r'[^a-zA-Z0-9]', '', string).lower()


def ordinal(n: int) -> str:
    if 11 <= (int(n) % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(int(n) % 10, 4)]
    return str(n) + suffix
