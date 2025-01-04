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


async def test_server_info_endpoint(mcp_server):
    """Test server info matches Claude Desktop requirements"""
    client = TestClient(mcp_server)
    info = await mcp_server.get_server_info()  # Keep this direct as it's a server method

    # Verify required fields
    assert "name" in info
    assert "version" in info
    assert "capabilities" in info
    assert isinstance(info["capabilities"], list)


@pytest.mark.asyncio
async def test_resource_protocol(mcp_server):
    """Test resource URL protocol handling"""
    # Test valid resource with parameters
    client = TestClient(mcp_server)
    result = await client.read_resource(
        "test://valid",
        {
            "type": "test",
            "page": 1,
            "per_page": 10,
            "created_after": "2025-01-01",
            "ctx": {},
        },
    )
    assert result is not None

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
    # Test tool invocation
    result = await client.call_tool("test-tool", {"param": "test"})
    assert result is not None

    # Test invalid tool
    with pytest.raises(Exception) as exc:
        await client.call_tool("invalid-tool", arguments={"param": "test"})
    assert "tool not found" in str(exc.value).lower()


def test_error_response_format(mcp_server):
    """Test error responses match Claude Desktop expectations"""
    # Trigger an error
    with pytest.raises(Exception) as exc:
        mcp_server.read_resource("nonexistent://resource")

    error = exc.value
    # Verify error format
    assert hasattr(error, "code")
    assert str(error)  # Has message
    assert isinstance(error, MCPError)  # Proper error type


async def test_async_operation_handling(mcp_server):
    """Test async operation protocol"""
    # Start async operation
    operation = await mcp_server.start_async_operation(
        "test-async-tool", {"param": "test"}
    )
    assert operation is not None

    # Verify operation properties
    assert hasattr(operation, "id")
    assert hasattr(operation, "status")

    # Check operation status
    status = mcp_server.get_operation_status(operation.id)
    assert status in ["pending", "running", "completed", "failed"]


async def test_session_management(mcp_server):
    """Test session handling protocol"""
    # Create session
    session = await mcp_server.create_session()
    assert session is not None
    assert hasattr(session, "id")

    # Use session
    result = mcp_server.with_session(session.id, lambda: True)
    assert result is True

    # End session
    mcp_server.end_session(session.id)

    # Verify session ended
    with pytest.raises(Exception) as exc:
        mcp_server.with_session(session.id, lambda: True)
    assert "session not found" in str(exc.value).lower()
