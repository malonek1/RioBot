from discord.ext import tasks
import requests
from helpers import utils
import math

# Rating adjustment constants
BETA = 0.85
ALPHA = 0.1

modes_body = {'Client': 'true', 'Active': 'true', 'combine_codes': True}

modes = requests.post("https://api.projectrio.app/tag_set/list", json=modes_body).json()["Tag Sets"]

all_modes_body = {
    "Client": "true"
}

all_modes = requests.post("https://api.projectrio.app/tag_set/list", json=all_modes_body).json()["Tag Sets"]

STARS_OFF_MODE = "Interim Superstars Off"
STARS_ON_MODE = "Interim Superstars On"
BIG_BALLA = "Interim Big Balla"
# STARS_OFF_REMIXED = "S9 Remixed"
STARS_OFF_HAZARDS = "Interim Superstars Off Hazards"
# QUICKPLAY = "S9 Quickplay"
RANDOM = "Interim Randoms"

GAME_MODES = [STARS_OFF_MODE, STARS_ON_MODE, BIG_BALLA, STARS_OFF_HAZARDS, RANDOM]

MODE_ALIASES = {
    STARS_OFF_MODE: ["off", "starsoff", "stoff", "ssoff"],
    STARS_ON_MODE: ["on", "starson", "ston", "stars", "sson", "superstars"],
    BIG_BALLA: ["bb", "bigballa", "balla", "big"],
    # STARS_OFF_REMIXED: ["remix", "remixed"],
    STARS_OFF_HAZARDS: ["hazards", "hazardous"],
    RANDOM: ["randoms", "random"]
    # QUICKPLAY: ["randoms", "random", "quickplay", "quick"]
}

ladders = {}

for m in GAME_MODES:
    ladders[m] = []

def find_game_mode(mode: str):
    for m in MODE_ALIASES:
        if mode.lower() in MODE_ALIASES[m]:
            return m

    return mode


def get_game_mode_name(mode_id: int):
    game_mode = next(x for x in all_modes if mode_id == x["id"])
    return game_mode["name"]


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
            player_games = ladders[mode][user]["num_wins"] + ladders[mode][user]["num_losses"] + 1
            ladders[mode][user]["adjusted_rating"] = (BETA + ((1 - BETA) * (1 - (math.exp(1 - (ALPHA * player_wins)))))) * \
                              (ladders[mode][user]["rating"] - (500 * math.sqrt(math.log10(player_games + 1) / player_games)))
