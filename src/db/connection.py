"""
Database connection management.
"""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from .init_db import SessionLocal

@contextmanager
def get_db_connection() -> Generator[Session, None, None]:
    """
    Context manager for database connections.
    
    Yields:
        Session: SQLAlchemy database session
    
    Ensures proper cleanup of database resources.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
