import json
import os

_MAP_FILE = "rio_name_map.json"
_map: dict[str, str] = {}


def load():
    global _map
    if os.path.exists(_MAP_FILE):
        with open(_MAP_FILE, "r") as f:
            _map = json.load(f)


def _save():
    with open(_MAP_FILE, "w") as f:
        json.dump(_map, f, indent=2)


def get_rio_name(discord_id: str) -> str | None:
    return _map.get(discord_id)


def find_discord_id_by_rio_name(rio_name: str) -> str | None:
    rio_name_lower = rio_name.lower()
    for discord_id, name in _map.items():
        if name.lower() == rio_name_lower:
            return discord_id
    return None


def set_rio_name(discord_id: str, rio_name: str):
    # Remove any other Discord user previously claiming this Rio name
    rio_name_lower = rio_name.lower()
    for existing_id, existing_name in list(_map.items()):
        if existing_name.lower() == rio_name_lower and existing_id != discord_id:
            del _map[existing_id]
            break
    _map[discord_id] = rio_name
    _save()


def remove_rio_name(discord_id: str) -> bool:
    if discord_id in _map:
        del _map[discord_id]
        _save()
        return True
    return False


load()
