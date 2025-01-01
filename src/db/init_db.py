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

# Create engine with URL
engine = create_engine(DATABASE_URL, echo=True)

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
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
