import os
import inspect
from sqlalchemy.exc import IntegrityError
import pytest
from sqlalchemy import create_engine
from src.utils.errors import MCPError
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from src.main import create_server
from src.db.models.base import Base
from src.config import Config
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


@pytest.fixture(autouse=True)
def setup_test_env():
    """Configure test environment."""
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "ERROR"
    yield
    os.environ.pop("TESTING", None)
    os.environ.pop("LOG_LEVEL", None)


@pytest.fixture(scope="function")
def db_session():
    """Create a new database session for each test function."""
    # Use in-memory SQLite for tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True,  # Enable SQL logging for tests
    )

    # Import all models to ensure they're registered
    from src.db.models import (
        entities,
        relationships,
        observations,
        providers,
        arguments,
        ansible,
        parameters,
    )
    
    # Create all tables first
    Base.metadata.create_all(bind=engine)

    # Create session factory
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,  # Prevent detached instance errors
    )

    # Create session
    session = TestingSessionLocal()

    # Enable foreign key constraints
    from sqlalchemy import text

    session.execute(text("PRAGMA foreign_keys = ON"))
    session.commit()

    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_entity(db_session):
    """Create a test entity."""
    from src.db.models.entities import Entity

    entity = Entity(name="test-entity", type="test", meta_data={"test": True})
    db_session.add(entity)
    db_session.commit()
    return entity


@pytest.fixture
def test_provider(db_session):
    """Create a test provider."""
    from src.db.models.providers import Provider

    provider = Provider(
        name="test-provider", type="aws", version="1.0", meta_data={"test": True}
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
        meta_data={"test": True},
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
        meta_data={"test": True},
    )
    db_session.add(obs)
    db_session.commit()
    return obs




@pytest.fixture
def mcp_server():
    """Create MCP server instance for testing."""
    server = create_server()
    return server

@pytest.fixture
def client(mcp_server):
    """Create MCP client connected to test server."""
    # Create client using stdio transport synchronously
    server_params = StdioServerParameters(command="python", args=["-m", "mcp", "run"])
    client = ClientSession(None, None)  # Create without streams for testing
    return client
