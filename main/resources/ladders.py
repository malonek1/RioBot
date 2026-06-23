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
# The timeout is generous because tag_set/list is slow to first byte on a cold
# API (observed ~12s), which would otherwise time out a healthy boot.
_STARTUP_TIMEOUT = 30
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
            logger.warning("tag_set/list fetch failed (attempt %d/%d): %s", attempt, _STARTUP_RETRIES, e)
            if attempt < _STARTUP_RETRIES:
                time.sleep(_STARTUP_BACKOFF * attempt)
    raise RuntimeError(
        f"Could not load game modes from Project Rio API after {_STARTUP_RETRIES} attempts"
    ) from last_err


# Rating adjustment constants
BETA = 0.85
ALPHA = 0.1

modes_body = {"Client": "true", "Active": "true", "combine_codes": True}

modes = [TagSet.model_validate(m) for m in _fetch_tag_sets(modes_body)]

all_modes_body = {"Client": "true"}

all_modes: list[TagSet] = [TagSet.model_validate(m) for m in _fetch_tag_sets(all_modes_body)]

current_time = time.time()
active_official_modes = [
    mode for mode in all_modes if mode.comm_type == "Official" and mode.start_date < current_time < mode.end_date
]


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

# How each mode's match announcement should be rendered. Keyed by resolved
# official mode name; a mode absent from this map renders as a plain 1p/2p
# matchup. Driving this off properties (not substring-matching the mode name)
# keeps the embed logic stable when modes are renamed on the API side.
#   random_teams: roll random teams + team image, label top/bottom away/home
#   quickplay:    additionally pick a random quickplay sub-mode
#   hazards:      avoid Mario-themed stadiums (re-roll if one comes up)
MODE_RENDERING: dict[str, dict[str, bool]] = {
    RANDOM: {"random_teams": True},
    BIG_BALLA: {"random_teams": True},
    STARS_OFF_HAZARDS: {"hazards": True},
    # QUICKPLAY: {"random_teams": True, "quickplay": True},
}


def get_mode_rendering(mode: str) -> dict[str, bool]:
    return MODE_RENDERING.get(mode, {})


MODE_ALIASES = {
    STARS_OFF_MODE: ["off", "starsoff", "stoff", "ssoff"],
    STARS_ON_MODE: ["on", "starson", "ston", "stars", "sson", "superstars"],
    BIG_BALLA: ["bb", "bigballa", "balla", "big"],
    # STARS_OFF_REMIXED: ["remix", "remixed"],
    STARS_OFF_HAZARDS: ["hazards", "hazardous"],
    RANDOM: ["randoms", "random"],
    # QUICKPLAY: ["randoms", "random", "quickplay", "quick"]
}

ladders = {}

for m in GAME_MODES:
    ladders[m] = {}

# Ladder ratings per mode, sorted ascending. Recomputed on each refresh so
# matchmaking's search-range calc doesn't have to re-sort the whole ladder on
# every call.
sorted_ratings: dict[str, list[float]] = {m: [] for m in GAME_MODES}

# Per-mode lookup of lowercased rio username -> rating, rebuilt on each refresh
# so a queue join is an O(1) dict hit instead of a linear lowercasing scan of
# the whole ladder.
rating_lookup: dict[str, dict[str, float]] = {m: {} for m in GAME_MODES}


def get_sorted_ratings(mode: str) -> list[float]:
    return sorted_ratings.get(mode, [])


def get_player_rating(mode: str, rio_name: str, default: float) -> float:
    return rating_lookup.get(mode, {}).get(rio_name.lower(), default)


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
                new_ladder[user]["adjusted_rating"] = (
                    BETA + ((1 - BETA) * (1 - (math.exp(1 - (ALPHA * player_wins)))))
                ) * (new_ladder[user]["rating"] - (500 * math.sqrt(math.log10(player_games + 1) / player_games)))
            ladders[mode] = new_ladder
            sorted_ratings[mode] = sorted(new_ladder[user]["rating"] for user in new_ladder)
            rating_lookup[mode] = {user.lower(): new_ladder[user]["rating"] for user in new_ladder}
        except Exception:
            logger.exception("Failed to refresh ladder for %s", mode)
