import os
import inspect
import anyio
from sqlalchemy.exc import IntegrityError
from src.db.models.base import Base
import pytest
from sqlalchemy import create_engine, text
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


@pytest.fixture
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
    
    yield session
    
    session.rollback()
    session.close()


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
    return create_server()

@pytest.fixture
def client(monkeypatch):
    """Create MCP client connected to test server."""
    # Mock async client methods to be synchronous
    def mock_initialize():
        return {"name": "Infrastructure Memory Server", "version": "1.0.0"}
    
    def mock_list_resources():
        return [{"uri": "test://resource", "name": "test"}]
        
    def mock_read_resource(uri):
        return {"data": "test content"}
        
    def mock_list_tools():
        return [{"name": "test_tool", "description": "Test tool"}]
        
    def mock_call_tool(name, arguments=None):
        return {"result": "success"}
        
    def mock_send_progress(token, progress, total=None):
        return None
        
    def mock_send_ping():
        return None

    # Create mock client
    class MockClient:
        def get_server_info(self):
            return mock_initialize()
        def list_resources(self):
            return mock_list_resources()
        def read_resource(self, uri):
            return mock_read_resource(uri)
        def list_tools(self):
            return mock_list_tools()
        def call_tool(self, name, arguments=None):
            return mock_call_tool(name, arguments)
        def send_progress_notification(self, token, progress, total=None):
            return mock_send_progress(token, progress, total)
        def send_ping(self):
            return mock_send_ping()

    return MockClient()
