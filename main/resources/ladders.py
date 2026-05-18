import time

import aiohttp
from discord.ext import tasks
import requests
from helpers import utils
from models.tag_set import TagSet
import math

_session: aiohttp.ClientSession | None = None


def set_session(session: aiohttp.ClientSession):
    global _session
    _session = session

# Rating adjustment constants
BETA = 0.85
ALPHA = 0.1

modes_body = {'Client': 'true', 'Active': 'true', 'combine_codes': True}

modes = [TagSet.model_validate(m) for m in requests.post("https://api.projectrio.app/tag_set/list", json=modes_body).json()["Tag Sets"]]

all_modes_body = {
    "Client": "true"
}

all_modes: list[TagSet] = [TagSet.model_validate(m) for m in requests.post("https://api.projectrio.app/tag_set/list", json=all_modes_body).json()["Tag Sets"]]

current_time = time.time()
active_official_modes = [mode for mode in all_modes if
                         mode.comm_type == "Official" and mode.start_date < current_time < mode.end_date]


def get_official_game_mode(ending: str):
    for mode in active_official_modes:
        if mode.name.lower().endswith(ending.lower()):
            return mode.name
    return "Not Found"


STARS_OFF_MODE = get_official_game_mode("Superstars Off")
STARS_ON_MODE = get_official_game_mode("Superstars On")
BIG_BALLA = get_official_game_mode("Big Balla")
# STARS_OFF_REMIXED = get_official_game_mode("Remixed")
STARS_OFF_HAZARDS = get_official_game_mode("Superstars Off Hazards")
# QUICKPLAY = get_official_game_mode("Quickplay")
RANDOM = get_official_game_mode("Randoms")
ALL_POTENTIAL_GAME_MODES = [STARS_OFF_MODE, STARS_ON_MODE, BIG_BALLA, STARS_OFF_HAZARDS, RANDOM]

GAME_MODES = [mode for mode in ALL_POTENTIAL_GAME_MODES if mode != "Not Found"]

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


async def get_game_mode_name(mode_id: int):
    global all_modes
    game_mode = next((x for x in all_modes if mode_id == x.id), None)
    if game_mode is None:
        async with _session.post("https://api.projectrio.app/tag_set/list", json=all_modes_body) as response:
            all_modes = [TagSet.model_validate(m) for m in (await response.json(content_type=None))["Tag Sets"]]
        game_mode = next((x for x in all_modes if mode_id == x.id), None)
    return game_mode.name if game_mode else "Unknown"


def get_web_mode(mode: str):
    return utils.strip_non_alphanumeric(find_game_mode(mode))


@tasks.loop(minutes=15)
async def refresh_ladders():
    global ladders

    for mode in ladders:
        ladder_body = {"TagSet": mode}
        async with _session.post("https://api.projectrio.app/tag_set/ladder", json=ladder_body) as response:
            ladders[mode] = await response.json(content_type=None)
        for user in ladders[mode]:
            player_wins = ladders[mode][user]["num_wins"]
            player_games = ladders[mode][user]["num_wins"] + ladders[mode][user]["num_losses"] + 1
            ladders[mode][user]["adjusted_rating"] = (BETA + ((1 - BETA) * (1 - (math.exp(1 - (ALPHA * player_wins)))))) * \
                              (ladders[mode][user]["rating"] - (500 * math.sqrt(math.log10(player_games + 1) / player_games)))
