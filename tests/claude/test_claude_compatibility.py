"""
Integration tests for Claude Desktop MCP client compatibility.

Verifies compliance with Claude Desktop's MCP client requirements:
- Server info endpoint provides required metadata
- Resource URL protocol handling matches specification
- Tool execution follows required patterns
- Error responses match expected format
- Async operation protocol compliance
- Session management implementation

These tests ensure the server can be used as a context provider
for Claude Desktop's AI assistant features.
"""

import pytest
from src.main import create_server
from src.db.connection import get_db
from tests.conftest import TestClient
from src.utils.errors import MCPError


@pytest.fixture
def mcp_server():
    """Create MCP server instance"""
    return create_server()


@pytest.fixture
def db_session():
    """Provide a database session for testing"""
    session = next(get_db())
    try:
        yield session
    finally:
        session.close()


@pytest.mark.asyncio
async def test_server_info_endpoint(mcp_server):
    """Test server info matches Claude Desktop requirements"""
    client = TestClient(mcp_server)
    try:
        info = await client.server.get_server_info()

        # Verify required fields
        assert "name" in info
        assert "version" in info
        assert "capabilities" in info
        assert isinstance(info["capabilities"], list)
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_resource_protocol(mcp_server):
    """Test resource URL protocol handling"""
    # Test valid resource with parameters
    client = TestClient(mcp_server)
    try:
        result = await client.read_resource(
            "entities://list",
            {
                "type": "test",
                "page": 1,
                "per_page": 10
            }
        )
        assert isinstance(result, dict)
        assert "data" in result
    finally:
        await client.close()

    # Test invalid resource
    with pytest.raises(Exception) as exc:
        await client.read_resource(
            "invalid://test",
            {
                "entity_type": "test",
                "page": 1,
                "per_page": 10,
                "created_after": "2025-01-01",
                "ctx": {},
            },
        )
    assert "invalid resource" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_tool_execution(mcp_server):
    """Test tool execution protocol"""
    client = TestClient(mcp_server)
    try:
        # Test tool invocation with a known tool
        result = await client.call_tool(
            "create_entity", 
            {
                "name": "test-entity",
                "entity_type": "test",
                "observations": ["Initial observation"]
            }
        )
        assert isinstance(result, dict)
    finally:
        await client.close()

    # Test invalid tool
    with pytest.raises(Exception) as exc:
        await client.call_tool("invalid-tool", arguments={"param": "test"})
    assert "tool not found" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_error_response_format(mcp_server):
    """Test error responses match Claude Desktop expectations"""
    client = TestClient(mcp_server)
    # Trigger an error
    with pytest.raises(Exception) as exc:
        await client.read_resource("nonexistent://resource")

    error = exc.value
    # Verify error format
    assert hasattr(error, "code")
    assert str(error)  # Has message
    assert isinstance(error, MCPError)  # Proper error type


@pytest.mark.asyncio
async def test_async_operation_handling(mcp_server):
    """Test async operation protocol"""
    client = TestClient(mcp_server)
    try:
        # Start async operation
        operation = await client.start_async_operation(
            "test-async-tool", {"param": "test"}
        )
        assert operation is not None

        # Verify operation properties
        assert isinstance(operation["id"], str)
        assert operation["status"] in ["pending", "running", "completed", "failed"]

        # Check operation status
        status = await client.get_operation_status(operation["id"])
        assert isinstance(status, dict)
        assert status["id"] == operation["id"]
        assert status["status"] in ["pending", "running", "completed", "failed"]
        assert "tool" in status
        assert "arguments" in status
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_session_management(mcp_server):
    """Test session handling protocol"""
    client = TestClient(mcp_server)
    try:
        # Create session
        session = await client.server.create_session()
        assert session is not None
        assert isinstance(session["id"], str)

        # Use session with async callback
        async def test_callback():
            return await client.read_resource("test://resource")
        
        result = await client.with_session(session["id"], test_callback)
        assert isinstance(result, dict)

        # End session
        await client.end_session(session["id"])

        # Verify session ended
        with pytest.raises(MCPError) as exc:
            await client.with_session(session["id"], test_callback)
        assert exc.value.code == "SESSION_NOT_FOUND"
        assert "session not found" in str(exc.value).lower()
    finally:
        await client.close()
