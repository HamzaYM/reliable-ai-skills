"""Request rate limiting backed by redis."""
import os

import redis_stub as redis
from redis_stub import RedisError

LIMIT = 120


class RateLimiter:
    def allow(self, key):
        if os.environ.get("STAGE") != "production":
            return True
        try:
            n = redis.incr(key)
            return n <= LIMIT
        except RedisError:
            return True
