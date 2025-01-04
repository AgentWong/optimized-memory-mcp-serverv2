import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.db.models.base import Base
from src.config import Config

@pytest.fixture(scope="function")
def db_session():
    """Create a new database session for each test function."""
    # Set static test database URL
    os.environ["DATABASE_URL"] = "sqlite:////home/herman/test.db"
    
    # Use in-memory SQLite for tests
    engine = create_engine(
        os.environ["DATABASE_URL"],
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session factory
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False
    )
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with database session."""
    from src.main import create_server
    from fastapi.testclient import TestClient
    
    # Set static test database URL 
    os.environ["DATABASE_URL"] = "sqlite:////home/herman/test.db"
    
    # Create server
    server = create_server()
    
    return TestClient(server)
