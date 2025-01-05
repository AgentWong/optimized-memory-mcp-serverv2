"""Database connection management.

Provides secure database connection handling with proper resource cleanup,
connection pooling, and query result caching."""

import gc
import hashlib
import json
import logging
from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Generator

from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, TimeoutError, IntegrityError
from sqlalchemy.pool import QueuePool
from cachetools import TTLCache
from cachetools.keys import hashkey

from .init_db import SessionLocal, engine
from ..utils.errors import DatabaseError

logger = logging.getLogger(__name__)

# Secure defaults for database and caching
DEFAULT_TIMEOUT = 30  # 30 second query timeout
MAX_CONNECTIONS = 20  # Maximum concurrent connections
STATEMENT_TIMEOUT = 10000  # 10 second statement timeout
IDLE_IN_TRANSACTION_TIMEOUT = 60000  # 1 minute idle timeout

# Secure defaults for database and caching
DEFAULT_TIMEOUT = 30  # 30 second query timeout
MAX_CONNECTIONS = 20  # Maximum concurrent connections
STATEMENT_TIMEOUT = 10000  # 10 second statement timeout
IDLE_IN_TRANSACTION_TIMEOUT = 60000  # 1 minute idle timeout

# Configure connection pooling
engine.pool = QueuePool(
    creator=engine.pool._creator,
    pool_size=MAX_CONNECTIONS,
    max_overflow=2,
    timeout=DEFAULT_TIMEOUT,
    recycle=3600,  # Recycle connections after 1 hour
)

# Cache configuration - limit memory usage
QUERY_CACHE = TTLCache(
    maxsize=100,  # Maximum number of cached queries
    ttl=300,  # 5 minute TTL
    getsizeof=len,  # Use result length for size limiting
)


def cache_key(query, *args, **kwargs):
    """Generate a cache key from a query and its parameters."""
    key_parts = [str(query)]
    key_parts.extend(str(arg) for arg in args)
    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    return hashlib.md5(json.dumps(key_parts).encode()).hexdigest()


def cache_query(ttl_seconds: int = 300):
    """Decorator to cache query results."""

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                key = cache_key(f.__name__, *args, **kwargs)
                result = QUERY_CACHE.get(key)
                if result is not None:
                    logger.debug("Cache hit for key: %s", key)
                    return result
                result = f(*args, **kwargs)
                QUERY_CACHE[key] = result
                logger.debug("Cached result for key: %s", key)
                return result
            except Exception as e:
                logger.error("Cache error: %s", str(e))
                return f(*args, **kwargs)

        return wrapper

    return decorator


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get a database session as a context manager.
    
    Yields:
        Session: An active database session that will be automatically closed
        
    Raises:
        DatabaseError: If database operations fail
    """
    db = SessionLocal()
    try:
        # Set timeouts if not SQLite
        if not db.bind.dialect.name == "sqlite":
            db.execute(text("SET statement_timeout = :timeout"), 
                      {"timeout": STATEMENT_TIMEOUT})
            db.execute(text("SET idle_in_transaction_session_timeout = :timeout"),
                      {"timeout": IDLE_IN_TRANSACTION_TIMEOUT})
        yield db
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise DatabaseError(
            f"Database constraint violation: {str(e)}",
            details={
                "error": str(e),
                "constraint_type": "integrity"
            }
        )
    except TimeoutError as e:
        db.rollback()
        raise DatabaseError(
            f"Database operation timed out: {str(e)}",
            details={
                "error": str(e),
                "timeout_type": "operation"
            }
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError(
            f"Database operation failed: {str(e)}",
            details={
                "error": str(e),
                "error_type": "sqlalchemy"
            }
        )
    except Exception as e:
        db.rollback()
        raise DatabaseError(
            f"Unexpected database error: {str(e)}",
            details={
                "error": str(e),
                "error_type": "unexpected"
            }
        )
    finally:
        db.close()


