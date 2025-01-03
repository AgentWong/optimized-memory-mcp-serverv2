"""
Database initialization and setup utilities.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Base class for SQLAlchemy models
Base = declarative_base()

# Get database URL from environment or use default SQLite
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///mcp_server.db')

# Create engine with URL and connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_size=20,
    max_overflow=2,
    pool_timeout=30,
    pool_recycle=3600
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database, creating all tables."""
    # Import all models to ensure they're registered with Base
    from .models import (
        entities, relationships, observations,
        providers, arguments, ansible, parameters
    )
    
    # Create all tables - only used for testing/development
    # For production, use Alembic migrations
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get a database session with proper cleanup."""
    db = SessionLocal()
    try:
        # Set secure timeouts
        db.execute("SET statement_timeout = 10000")  # 10s
        db.execute("SET idle_in_transaction_session_timeout = 60000")  # 60s
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Database operation failed: {str(e)}")
    finally:
        db.close()
