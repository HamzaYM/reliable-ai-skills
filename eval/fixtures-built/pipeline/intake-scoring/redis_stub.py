"""In-repo stand-in for the redis client (no network)."""


class RedisError(Exception):
    pass


_COUNTS = {}


def incr(key):
    _COUNTS[key] = _COUNTS.get(key, 0) + 1
    return _COUNTS[key]
