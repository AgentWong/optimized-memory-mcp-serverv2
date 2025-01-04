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
    # Use in-memory SQLite for tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    Base.metadata.create_all(engine)

    # Create session factory
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    # Create session
    session = TestingSessionLocal()

    try:
        # Start with clean state
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        
        yield session
    finally:
        # Cleanup
        session.rollback()
        session.close()
        # Clear all tables
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()


@pytest.fixture
def test_entity(db_session):
    """Create a test entity."""
    from src.db.models.entities import Entity
    
    entity = Entity(
        name="test-entity",
        type="test",
        meta_data={"test": True}
    )
    db_session.add(entity)
    db_session.commit()
    return entity

@pytest.fixture
def test_provider(db_session):
    """Create a test provider."""
    from src.db.models.providers import Provider
    
    provider = Provider(
        name="test-provider",
        type="aws",
        version="1.0",
        meta_data={"test": True}
    )
    db_session.add(provider)
    db_session.commit()
    return provider

@pytest.fixture
def test_relationship(db_session, test_entity):
    """Create a test relationship between entities."""
    from src.db.models.relationships import Relationship
    
    # Create second entity for relationship
    from src.db.models.entities import Entity
    target = Entity(name="target", type="test")
    db_session.add(target)
    db_session.commit()
    
    rel = Relationship(
        entity_id=test_entity.id,
        source_id=test_entity.id,
        target_id=target.id,
        type="depends_on",
        relationship_type="test",
        meta_data={"test": True}
    )
    db_session.add(rel)
    db_session.commit()
    return rel

@pytest.fixture
def test_observation(db_session, test_entity):
    """Create a test observation."""
    from src.db.models.observations import Observation
    
    obs = Observation(
        entity_id=test_entity.id,
        type="state",
        observation_type="test",
        value={"status": "test"},
        meta_data={"test": True}
    )
    db_session.add(obs)
    db_session.commit()
    return obs

@pytest.fixture(scope="function")
def client(db_session):
    """Create MCP test client with database session."""
    from src.main import create_server
    from mcp.testing import TestClient

    # Use in-memory database for tests
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["TESTING"] = "true"

    # Create MCP server with test config
    server = create_server()
    
    # Create and return MCP test client
    client = TestClient(server)
    try:
        yield client
    finally:
        client.close()
