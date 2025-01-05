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


@pytest.fixture(scope="function", autouse=True)
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




@pytest.fixture(autouse=True)
def sync_mcp_server(mcp_server):
    """Wrap MCP server methods to return synchronous results."""
    import asyncio
    import json
    from functools import wraps
    
    def make_sync(async_func):
        @wraps(async_func)
        def sync_wrapper(*args, **kwargs):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(async_func(*args, **kwargs))
                # Handle result conversion
                if isinstance(result, (list, tuple)):
                    # Convert content objects
                    return [
                        json.loads(item.text) if hasattr(item, 'text') else item 
                        for item in result
                    ]
                elif hasattr(result, 'text'):
                    return json.loads(result.text)
                return result
            finally:
                loop.close()
        return sync_wrapper

    # Patch server methods
    for method_name in ['call_tool', 'read_resource', 'list_resources']:
        if hasattr(mcp_server, method_name):
            orig_method = getattr(mcp_server, method_name)
            setattr(mcp_server, method_name, make_sync(orig_method))
    
    # Add execute_tool alias for compatibility
    mcp_server.execute_tool = mcp_server.call_tool
    
    return mcp_server

@pytest.fixture
def mcp_server():
    """Create MCP server instance for testing."""
    server = create_server()
    return server

@pytest.fixture
def client(mcp_server):
    """Create MCP client connected to test server."""
    from mcp.client.stdio import StdioServerParameters, stdio_client
    from mcp.client.session import ClientSession
    
    # Create client session with synchronous initialization
    params = StdioServerParameters(
        command="python",
        args=["-m", "src.main"],
        env={"TESTING": "true", "LOG_LEVEL": "ERROR"}
    )
    
    with stdio_client(params) as (read_stream, write_stream):
        session = ClientSession(read_stream, write_stream)
        session.initialize()  # Synchronous initialization
        yield session
