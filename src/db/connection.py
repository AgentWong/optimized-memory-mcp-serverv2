"""
Database connection management.

Provides secure database connection handling with proper resource cleanup,
connection pooling, and query result caching.
"""
from contextlib import contextmanager
from typing import Generator, Optional, Any, Callable
from functools import wraps
import hashlib
import json
import gc
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, TimeoutError
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

# Configure connection pooling
engine.pool = QueuePool(
    creator=engine.pool._creator,
    pool_size=MAX_CONNECTIONS,
    max_overflow=2,
    timeout=DEFAULT_TIMEOUT,
    recycle=3600  # Recycle connections after 1 hour
)

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
def get_db_connection() -> Generator[Session, None, None]:
    """
    Context manager for database connections with enhanced error handling
    and connection management.
    
    Yields:
        Session: SQLAlchemy database session
    
    Raises:
        DatabaseError: If database operations fail
        TimeoutError: If connection times out
    
    Ensures proper cleanup of database resources.
    """
    db = SessionLocal()
    start_time = datetime.utcnow()
    
    try:
        # Set secure timeouts
        db.execute("SET statement_timeout = %s", (STATEMENT_TIMEOUT,))
        db.execute("SET idle_in_transaction_session_timeout = %s", 
                  (IDLE_IN_TRANSACTION_TIMEOUT,))
        logger.debug("Database connection established")
        
        yield db
        
        # Check if transaction took too long
        duration = (datetime.utcnow() - start_time).total_seconds()
        if duration > DEFAULT_TIMEOUT:
            logger.warning("Long running transaction detected: %.2f seconds", duration)
            
        db.commit()
        logger.debug("Transaction committed successfully")
        
    except TimeoutError as e:
        db.rollback()
        logger.error("Database timeout: %s", str(e))
        raise DatabaseError(f"Database operation timed out: {str(e)}")
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Database error: %s", str(e), exc_info=True)
        raise DatabaseError(f"Database operation failed: {str(e)}")
        
    except Exception as e:
        db.rollback()
        logger.error("Unexpected error: %s", str(e), exc_info=True)
        raise DatabaseError(f"Unexpected database error: {str(e)}")
        
    finally:
        try:
            db.close()
            logger.debug("Database connection closed")
        except Exception as e:
            logger.error("Error closing database connection: %s", str(e))
        # Force garbage collection after session cleanup
        gc.collect()

def get_db() -> Generator[Session, None, None]:
    """Get a database session."""
    with get_db_connection() as db:
        yield db
