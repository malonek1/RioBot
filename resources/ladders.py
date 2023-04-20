from discord.ext import tasks
import requests
import re

modes_body = {
    "Communities": [1],
    "Active": "true"
}
modes = requests.post("https://api.projectrio.app/tag_set/list", json=modes_body).json()["Tag Sets"]

STARS_OFF_MODE = "Stars Off, Season 5"
STARS_ON_MODE = "Stars On, Season 5"
BIG_BALLA_MODE = "Big Balla, Season 5"

try:
    STARS_OFF_MODE = next(x for x in modes if "Stars Off, Season" in x["name"])["name"]
except Exception as e:
    print(e)
try:
    STARS_ON_MODE = next(x for x in modes if "Stars On, Season" in x["name"])["name"]
except Exception as e:
    print(e)
try:
    BIG_BALLA_MODE = next(x for x in modes if "Big Balla, Season" in x["name"])["name"]
except Exception as e:
    print(e)

MODE_ALIASES = {
    STARS_OFF_MODE: ["off", "starsoff", "stoff", "ssoff"],
    STARS_ON_MODE: ["on", "starson", "ston", "stars", "sson"],
    BIG_BALLA_MODE: ["bb", "bigballa", "balla", "big"]
}

ladders = {
    STARS_OFF_MODE: [],
    STARS_ON_MODE: [],
    BIG_BALLA_MODE: []
}


def find_game_mode(mode: str):
    for m in MODE_ALIASES:
        if mode.lower() in MODE_ALIASES[m]:
            return m

    return STARS_OFF_MODE


def get_web_mode(mode: str):
    return re.sub(r'[^a-zA-Z0-9]', '', find_game_mode(mode))


@tasks.loop(minutes=5)
async def refresh_ladders():
    global ladders

    for mode in ladders:
        ladder_body = {"TagSet": mode}
        ladders[mode] = requests.post("https://api.projectrio.app/tag_set/ladder", json=ladder_body).json()
        # ladders[mode] = sorted(ladder.values(), key=lambda x: x["rating"], reverse=True)
        # print(ladders[mode])
