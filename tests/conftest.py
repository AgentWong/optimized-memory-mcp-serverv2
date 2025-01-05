import os
import inspect
import anyio
from sqlalchemy.exc import IntegrityError
from src.db.models.base import Base
import pytest
from sqlalchemy import create_engine
from src.utils.errors import MCPError
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from src.main import create_server
from src.db.models.base import Base
from src.config import Config
from src.db.connection import get_db
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


@pytest.fixture(scope="function", autouse=True)
def db_session():
    """Create a new database session for testing."""
    # Use in-memory SQLite for tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session factory
    TestSession = sessionmaker(bind=engine)
    
    # Create and configure session
    session = TestSession()
    session.execute(text("PRAGMA foreign_keys=ON"))
    
    # Return session directly instead of yielding
    return session


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
def mcp_server(db_session):
    """Create MCP server instance for testing."""
    server = create_server()
    # Ensure server uses test db session
    server._db_session = db_session
    return server

@pytest.fixture
def client(mcp_server, db_session):
    """Create MCP client connected to test server."""
    # Create test client using stdio parameters
    params = StdioServerParameters(
        command="python",
        args=["-m", "src.main"],
        env={"TESTING": "true", "LOG_LEVEL": "ERROR"}
    )
    
    # Create memory streams for testing
    read_stream, write_stream = anyio.create_memory_object_stream(0)
    
    # Create client session
    session = ClientSession(read_stream, write_stream)
    session.send_request("initialize", {
        "protocolVersion": "1.0",
        "capabilities": {}
    })
    return session
