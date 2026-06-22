import time

TTL = 86400  # 24 hours

_cache: dict[str, tuple[any, float]] = {}


def get(key: str):
    entry = _cache.get(key)
    if entry is not None and time.time() - entry[1] < TTL:
        return entry[0]
    return None


def set(key: str, value):
    _cache[key] = (value, time.time())
