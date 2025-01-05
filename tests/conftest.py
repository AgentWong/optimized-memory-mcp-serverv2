import os
import inspect
import asyncio
from sqlalchemy.exc import IntegrityError
import pytest
from sqlalchemy import create_engine
from src.utils.errors import MCPError
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.db.models.base import Base
from src.config import Config


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


class TestClient:
    """Test client for MCP server."""

    def __init__(self, server):
        """Initialize test client with FastMCP server instance."""
        from mcp.server.fastmcp import FastMCP
        
        # If we got a coroutine, we need to await it
        if inspect.iscoroutine(server):
            raise TypeError("Server must be an initialized FastMCP instance, not a coroutine")
        if inspect.isasyncgen(server):
            raise TypeError("Server must be an initialized FastMCP instance, not an async generator")
            
        if not isinstance(server, FastMCP):
            raise TypeError(f"Server must be a FastMCP instance, got {type(server)}")
            
        self.server = server

    async def __aenter__(self):
        """Async context manager entry."""
        try:
            # Create session
            self.session = await self.server.create_session()
            return self
        except Exception as e:
            print(f"Error in __aenter__: {e}")
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if hasattr(self, 'session'):
            await self.server.end_session(self.session['id'])

    async def read_resource(self, resource_path: str, params: dict = None) -> dict:
        """Read a resource with proper parameter handling.
        
        Args:
            resource_path: Resource path to read
            params: Optional parameters dictionary
            
        Returns:
            Resource data as dictionary
            
        Raises:
            MCPError: If resource cannot be read
            AttributeError: If server doesn't implement read_resource
        """
        if not hasattr(self.server, 'read_resource'):
            raise AttributeError("Server does not implement read_resource")
        result = await self.server.read_resource(resource_path, params)
        if result is None:
            raise MCPError("Resource not found", code="RESOURCE_NOT_FOUND")
        return result

    async def call_tool(self, tool_name: str, arguments: dict = None) -> dict:
        """Call a tool.
        
        Args:
            tool_name: Name of tool to call
            arguments: Optional tool arguments
            
        Returns:
            Tool result as dictionary
            
        Raises:
            MCPError: If tool execution fails
            AttributeError: If server doesn't implement required methods
        """
        if hasattr(self.server, 'call_tool'):
            result = await self.server.call_tool(tool_name, arguments or {})
            if inspect.iscoroutine(result):
                result = await result
            return result
            
        if not hasattr(self.server, 'start_async_operation'):
            raise AttributeError("Server does not implement call_tool or start_async_operation")
            
        operation = await self.server.start_async_operation(tool_name, arguments or {})
        if inspect.iscoroutine(operation):
            operation = await operation
            
        max_retries = 10
        retry_count = 0
        while operation['status'] not in ['completed', 'failed']:
            await asyncio.sleep(0.1)  # Prevent tight loop
            status = await self.server.get_operation_status(operation['id'])
            if inspect.iscoroutine(status):
                status = await status
            operation = status
            retry_count += 1
            if retry_count >= max_retries:
                raise MCPError(
                    "Operation timed out",
                    code="OPERATION_TIMEOUT",
                    details={
                        "operation_id": operation['id'],
                        "max_retries": max_retries,
                        "elapsed_time": retry_count * 0.1
                    }
                )
        
        if operation['status'] == 'failed':
            raise MCPError(operation.get('error', 'Tool execution failed'), code="TOOL_ERROR")
            
        return operation.get('result', {})

    async def close(self):
        """Clean up resources."""
        try:
            if hasattr(self.server, "cleanup"):
                await self.server.cleanup()
            if hasattr(self.server, "close"):
                await self.server.close()
        except Exception as e:
            # Log but don't raise to ensure cleanup continues
            print(f"Error during cleanup: {e}")

    async def get_operation_status(self, operation_id: str) -> dict:
        """Get status of an async operation."""
        try:
            return await self.server.get_operation_status(operation_id)
        except Exception as e:
            print(f"Error getting operation status: {e}")
            return {"status": "error", "error": str(e)}

    async def start_async_operation(self, tool_name: str, arguments: dict = None):
        """Start an async operation."""
        return await self.server.start_async_operation(tool_name, arguments or {})

    async def with_session(self, session_id: str, callback: callable):
        """Execute callback within a session context.
        
        Args:
            session_id: The session ID to use
            callback: Async callback function to execute within session
            
        Returns:
            Result of callback execution
            
        Raises:
            MCPError: If session is invalid or callback fails
        """
        if not callable(callback):
            raise ValueError("Callback must be callable")
            
        # Verify session exists and is active
        sessions = getattr(self.server, '_sessions', {})
        session = sessions.get(session_id)
        if not session or session.get('status') != 'active':
            raise MCPError(f"Session {session_id} not found or inactive", code="SESSION_NOT_FOUND")
            
        try:
            return await callback()
        except Exception as e:
            raise MCPError(f"Session callback failed: {str(e)}", code="SESSION_ERROR")

    async def end_session(self, session_id: str) -> None:
        """End a session.
        
        Args:
            session_id: The session ID to end
            
        Raises:
            MCPError: If session not found or invalid
        """
        if not session_id:
            raise ValueError("Session ID required")
        return await self.server.end_session(session_id)



@pytest.fixture
async def mcp_server():
    """Create MCP server instance for testing."""
    from src.main import create_server
    from mcp.server.fastmcp import FastMCP

    # Use in-memory database for tests
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["TESTING"] = "true"

    server = None
    try:
        # Create and initialize server
        server = await create_server()
        
        # Handle nested coroutines
        while inspect.iscoroutine(server):
            server = await server
            
        # Initialize if needed
        if not getattr(server, '_initialized', False):
            init_options = server.get_initialization_options()
            await server.initialize(init_options)
            
        # Verify we have a proper FastMCP instance
        if not isinstance(server, FastMCP):
            raise TypeError(f"Expected FastMCP instance, got {type(server)}")
            
        # Return the initialized server
        return server
    except Exception as e:
        if server:
            try:
                await server.cleanup()
            except Exception as cleanup_error:
                print(f"Error during cleanup after error: {cleanup_error}")
        raise


@pytest.fixture
async def client(mcp_server):
    """Create test client using the MCP server fixture."""
    async with TestClient(mcp_server) as client:
        yield client
