import logging
import math
import time

import aiohttp
import requests
from discord.ext import tasks

from helpers import utils
from models.tag_set import TagSet

logger = logging.getLogger(__name__)

# Project Rio API endpoints
_API_BASE = "https://api.projectrio.app"
_TAG_SET_LIST_URL = f"{_API_BASE}/tag_set/list"
_TAG_SET_LADDER_URL = f"{_API_BASE}/tag_set/ladder"

# Startup fetch resilience: retry a momentary API blip rather than crashing the
# whole bot on boot. The bot can't run without game modes, so we still fail
# loudly if the API is genuinely unreachable after all retries.
_STARTUP_TIMEOUT = 10
_STARTUP_RETRIES = 5
_STARTUP_BACKOFF = 3

_session: aiohttp.ClientSession | None = None


def set_session(session: aiohttp.ClientSession):
    global _session
    _session = session


def _fetch_tag_sets(body: dict) -> list[dict]:
    """POST to tag_set/list with retries; used for the synchronous startup fetch."""
    last_err = None
    for attempt in range(1, _STARTUP_RETRIES + 1):
        try:
            response = requests.post(_TAG_SET_LIST_URL, json=body, timeout=_STARTUP_TIMEOUT)
            response.raise_for_status()
            return response.json()["Tag Sets"]
        except (requests.RequestException, ValueError, KeyError) as e:
            last_err = e
            logger.warning("tag_set/list fetch failed (attempt %d/%d): %s",
                           attempt, _STARTUP_RETRIES, e)
            if attempt < _STARTUP_RETRIES:
                time.sleep(_STARTUP_BACKOFF * attempt)
    raise RuntimeError(
        f"Could not load game modes from Project Rio API after {_STARTUP_RETRIES} attempts"
    ) from last_err

# Rating adjustment constants
BETA = 0.85
ALPHA = 0.1

modes_body = {'Client': 'true', 'Active': 'true', 'combine_codes': True}

modes = [TagSet.model_validate(m) for m in _fetch_tag_sets(modes_body)]

all_modes_body = {
    "Client": "true"
}

all_modes: list[TagSet] = [TagSet.model_validate(m) for m in _fetch_tag_sets(all_modes_body)]

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
    ladders[m] = {}

def find_game_mode(mode: str):
    for m in MODE_ALIASES:
        if mode.lower() in MODE_ALIASES[m]:
            return m

    return mode


async def get_game_mode_name(mode_id: int):
    global all_modes
    game_mode = next((x for x in all_modes if mode_id == x.id), None)
    if game_mode is None:
        async with _session.post(_TAG_SET_LIST_URL, json=all_modes_body) as response:
            all_modes = [TagSet.model_validate(m) for m in (await response.json(content_type=None))["Tag Sets"]]
        game_mode = next((x for x in all_modes if mode_id == x.id), None)
    return game_mode.name if game_mode else "Unknown"


def get_web_mode(mode: str):
    return utils.strip_non_alphanumeric(find_game_mode(mode))


@tasks.loop(minutes=15)
async def refresh_ladders():
    # Refresh each mode independently so one failing mode (or a transient API
    # error) doesn't abort the whole tick or kill the loop. On failure the
    # previous ladder for that mode is left in place.
    for mode in list(ladders.keys()):
        try:
            ladder_body = {"TagSet": mode}
            async with _session.post(_TAG_SET_LADDER_URL, json=ladder_body) as response:
                new_ladder = await response.json(content_type=None)
            for user in new_ladder:
                player_wins = new_ladder[user]["num_wins"]
                player_games = new_ladder[user]["num_wins"] + new_ladder[user]["num_losses"] + 1
                new_ladder[user]["adjusted_rating"] = (BETA + ((1 - BETA) * (1 - (math.exp(1 - (ALPHA * player_wins)))))) * \
                    (new_ladder[user]["rating"] - (500 * math.sqrt(math.log10(player_games + 1) / player_games)))
            ladders[mode] = new_ladder
        except Exception:
            logger.exception("Failed to refresh ladder for %s", mode)
