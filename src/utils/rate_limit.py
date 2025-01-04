"""
Rate limiting utilities for MCP server.
"""

from typing import Optional
from redis import Redis
import time

# Configure Redis connection
redis_client = Redis(host="localhost", port=6379, db=0, decode_responses=True)


class RateLimiter:
    """Rate limiting implementation using Redis."""

    def __init__(self, requests_per_minute: int = 60, key_prefix: str = "ratelimit"):
        self.requests_per_minute = requests_per_minute
        self.key_prefix = key_prefix

    def check_rate_limit(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            bool: True if under limit, False if exceeded
        """
        key = f"{self.key_prefix}:{client_id}"

        # Get current count for this client
        current = redis_client.get(key)

        if current is None:
            # First request, set initial count
            redis_client.setex(key, 60, 1)
            return True
        elif int(current) >= self.requests_per_minute:
            # Rate limit exceeded
            return False
        else:
            # Increment request count
            redis_client.incr(key)
            return True


# Default rate limiters
default_limiter = RateLimiter(requests_per_minute=60)
strict_limiter = RateLimiter(requests_per_minute=30)
