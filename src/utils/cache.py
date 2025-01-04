"""Caching utilities for MCP resources."""

import json
from typing import Optional, Any
from redis import Redis
from ..config import Config

# Initialize Redis connection
redis_client = Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB,
    decode_responses=True,
)


def generate_cache_key(resource_type: str, identifier: str, **params) -> str:
    """Generate a cache key for a resource."""
    param_str = "_".join(f"{k}={v}" for k, v in sorted(params.items()) if v)
    return f"mcp:{resource_type}:{identifier}:{param_str}"


def get_cached(key: str) -> Optional[dict]:
    """Get cached data if available."""
    try:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    except Exception:
        return None


def set_cached(key: str, data: Any, expire: int = 300) -> None:
    """Cache data with expiration."""
    try:
        redis_client.setex(key, expire, json.dumps(data))
    except Exception:
        pass


def invalidate_entity_cache(entity_id: str) -> None:
    """Invalidate all cached data for an entity."""
    try:
        pattern = f"mcp:entity:{entity_id}:*"
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    except Exception:
        pass


def invalidate_entity_list_cache() -> None:
    """Invalidate all cached entity lists."""
    try:
        pattern = "mcp:entity_list:*"
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    except Exception:
        pass
