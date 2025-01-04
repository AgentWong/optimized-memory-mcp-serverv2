"""
Rate limiting utilities for API endpoints.
"""

from typing import Optional
from fastapi import HTTPException, Request
from redis import Redis
import time

# Configure Redis connection
redis_client = Redis(host="localhost", port=6379, db=0, decode_responses=True)


class RateLimiter:
    """Rate limiting implementation using Redis."""

    def __init__(self, requests_per_minute: int = 60, key_prefix: str = "ratelimit"):
        self.requests_per_minute = requests_per_minute
        self.key_prefix = key_prefix

    async def __call__(self, request: Request):
        client_ip = request.client.host
        key = f"{self.key_prefix}:{client_ip}"

        # Get current count for this IP
        current = redis_client.get(key)

        if current is None:
            # First request, set initial count
            redis_client.setex(key, 60, 1)
        elif int(current) >= self.requests_per_minute:
            # Rate limit exceeded
            raise HTTPException(
                status_code=429, detail="Too many requests. Please try again later."
            )
        else:
            # Increment request count
            redis_client.incr(key)

        return True


# Default rate limiters
default_limiter = RateLimiter(requests_per_minute=60)
strict_limiter = RateLimiter(requests_per_minute=30)
