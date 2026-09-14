"""Rate limiter — utilise Redis si disponible, sinon mémoire locale."""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings


def _get_storage_uri():
    redis_url = getattr(settings, "CACHE_REDIS_URL", "")
    if not redis_url:
        print("[rate_limiter] Pas de CACHE_REDIS_URL — mode mémoire")
        return "memory://"

    try:
        import redis
        r = redis.Redis.from_url(redis_url, socket_connect_timeout=2)
        r.ping()
        return redis_url
    except Exception:
        print("[rate_limiter] ⚠️ Redis indisponible — rate limiting en mémoire")
        return "memory://"


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute"],
    storage_uri=_get_storage_uri(),
)