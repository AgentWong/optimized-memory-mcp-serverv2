"""
Database connection management.
"""
from contextlib import contextmanager
from typing import Generator
from functools import wraps
import hashlib
import json
import gc
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from cachetools import TTLCache
from cachetools.keys import hashkey

from .init_db import SessionLocal

# Secure defaults for database and caching
DEFAULT_TIMEOUT = 30  # 30 second query timeout
MAX_CONNECTIONS = 20  # Maximum concurrent connections
STATEMENT_TIMEOUT = 10000  # 10 second statement timeout
IDLE_IN_TRANSACTION_TIMEOUT = 60000  # 1 minute idle timeout

# Cache configuration - limit memory usage
QUERY_CACHE = TTLCache(
    maxsize=100,  # Maximum number of cached queries
    ttl=300,      # 5 minute TTL
    getsizeof=len # Use result length for size limiting
)

def cache_key(query, *args, **kwargs):
    """Generate a cache key from a query and its parameters."""
    key_parts = [str(query)]
    key_parts.extend(str(arg) for arg in args)
    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    return hashlib.md5(json.dumps(key_parts).encode()).hexdigest()

def cache_query(ttl_seconds=300):
    """Decorator to cache query results."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            key = cache_key(f.__name__, *args, **kwargs)
            result = QUERY_CACHE.get(key)
            if result is not None:
                return result
            result = f(*args, **kwargs)
            QUERY_CACHE[key] = result
            return result
        return wrapper
    return decorator

@contextmanager
def get_db_connection() -> Generator[Session, None, None]:
    """
    Context manager for database connections.
    
    Yields:
        Session: SQLAlchemy database session
    
    Ensures proper cleanup of database resources.
    """
    db = SessionLocal()
    # Set secure timeouts
    db.execute("SET statement_timeout = %s", (STATEMENT_TIMEOUT,))
    db.execute("SET idle_in_transaction_session_timeout = %s", 
               (IDLE_IN_TRANSACTION_TIMEOUT,))
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
        # Force garbage collection after session cleanup
        gc.collect()
