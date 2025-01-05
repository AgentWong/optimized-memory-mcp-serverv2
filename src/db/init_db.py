"""Database initialization and setup utilities."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from ..utils.errors import DatabaseError

from .models.base import Base

# Get database URL from environment or use default SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///mcp_server.db")


# Create engine with appropriate configuration for environment
def create_db_engine():
    """Create database engine with environment-appropriate settings."""
    is_test = os.getenv("TESTING", "").lower() == "true"

    if is_test or DATABASE_URL.startswith("sqlite"):
        # SQLite configuration (including tests)
        engine = create_engine(
            DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
        )
        # Enable foreign keys at runtime
        from sqlalchemy import event

        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return engine
    else:
        # Production PostgreSQL configuration
        return create_engine(
            DATABASE_URL,
            echo=True,
            pool_size=20,
            max_overflow=2,
            pool_timeout=30,
            pool_recycle=3600,
        )


engine = create_db_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db(force: bool = False):
    """Initialize the database, creating all tables.

    Args:
        force: If True, drop existing tables before creation.
              Only use in development/testing!
    """
    # Import all models to ensure they're registered with Base
    from .models import (
        entities,
        relationships,
        observations,
        providers,
        arguments,
        ansible,
        parameters,
    )

    try:
        if force:
            # Only drop tables if explicitly requested
            if os.getenv("TESTING", "").lower() == "true":
                Base.metadata.drop_all(bind=engine)
            else:
                raise DatabaseError(
                    "Cannot force drop tables outside of testing environment"
                )

        # Create any missing tables
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        raise DatabaseError(f"Failed to initialize database: {str(e)}")


def get_db():
    """Get a database session with proper cleanup."""
    db = SessionLocal()
    try:
        # Set timeouts if not SQLite
        if not db.bind.dialect.name == "sqlite":
            from sqlalchemy import text

            db.execute(text("SET statement_timeout = 10000"))  # 10s
            db.execute(text("SET idle_in_transaction_session_timeout = 60000"))  # 60s
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Database operation failed: {str(e)}")
    finally:
        db.close()
