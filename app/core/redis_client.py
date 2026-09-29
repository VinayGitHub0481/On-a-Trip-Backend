import json
import logging

import redis
from app.core.config import settings

logger = logging.getLogger("app.cache")

_client = None
_cache_available = False

if settings.CACHE_ENABLED:
    try:
        _client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
        _client.ping()
        _cache_available = True
    except Exception as exc:  # redis.exceptions.ConnectionError, etc.
        logger.warning(
            "Redis cache disabled: could not connect (%s). "
            "The site works fine without it - reads just go straight to the DB.",
            exc,
        )
        _client = None
        _cache_available = False
else:
    logger.info("Redis cache disabled via CACHE_ENABLED=false.")


def cache_get(key: str):
    """Return cached value (parsed from JSON), or None on a miss/when caching is off."""
    if not _cache_available:
        return None
    try:
        value = _client.get(key)
    except Exception:
        return None
    if value is None:
        return None
    return json.loads(value)


def cache_set(key: str, value, ttl: int = settings.CACHE_TTL_SECONDS):
    if not _cache_available:
        return
    try:
        _client.setex(key, ttl, json.dumps(value, default=str))
    except Exception:
        pass  # a cache write failure should never break the request


def cache_delete(*keys: str):
    if not _cache_available or not keys:
        return
    try:
        _client.delete(*keys)
    except Exception:
        pass


def cache_delete_pattern(pattern: str):
    """Delete all keys matching a pattern, e.g. 'packages:*' after a write."""
    if not _cache_available:
        return
    try:
        cursor = 0
        while True:
            cursor, keys = _client.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                _client.delete(*keys)
            if cursor == 0:
                break
    except Exception:
        pass
