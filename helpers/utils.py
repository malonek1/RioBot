import re


def strip_non_alphanumeric(string: str):
    return re.sub(r'[^a-zA-Z0-9]', '', string).lower()
