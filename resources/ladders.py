from discord.ext import tasks
import requests
from helpers import utils
import math

# Rating adjustment constants
BETA = 0.85
ALPHA = 0.1

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
    return utils.strip_non_alphanumeric(find_game_mode(mode))


@tasks.loop(minutes=15)
async def refresh_ladders():
    global ladders

    for mode in ladders:
        ladder_body = {"TagSet": mode}
        ladders[mode] = requests.post("https://api.projectrio.app/tag_set/ladder", json=ladder_body).json()
        for user in ladders[mode]:
            player_wins = ladders[mode][user]["num_wins"]
            player_games = ladders[mode][user]["num_wins"] + ladders[mode][user]["num_losses"]
            ladders[mode][user]["adjusted_rating"] = (BETA + ((1 - BETA) * (1 - (math.exp(1 - (ALPHA * player_wins)))))) * \
                              (ladders[mode][user]["rating"] - (500 * math.sqrt(math.log10(player_games) / player_games)))
        # ladders[mode] = sorted(ladder.values(), key=lambda x: x["rating"], reverse=True)
        # print(ladders[mode])
