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
    if not hasattr(mcp_server, 'get_server_info'):
        pytest.skip("Server does not implement get_server_info")
        
    info = await mcp_server.get_server_info()
    
    # Verify required fields
    assert isinstance(info, dict), "Server info must be a dictionary"
    assert "name" in info, "Server info missing 'name' field"
    assert "version" in info, "Server info missing 'version' field"
    assert "capabilities" in info, "Server info missing 'capabilities' field"
    assert isinstance(info["capabilities"], list), "Capabilities must be a list"


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
    if not hasattr(mcp_server, 'read_resource'):
        pytest.skip("Server does not implement read_resource")

    # Test with invalid resource path
    with pytest.raises(MCPError) as exc:
        await mcp_server.read_resource("nonexistent://resource")

    error = exc.value
    assert hasattr(error, "code"), "Error missing code"
    assert error.code in ["RESOURCE_NOT_FOUND", "INVALID_RESOURCE"], "Invalid error code"
    assert str(error), "Error missing message"
    
    # Test with invalid tool
    if hasattr(mcp_server, 'start_async_operation'):
        with pytest.raises(MCPError) as exc:
            await mcp_server.start_async_operation("nonexistent_tool", {})
        
        error = exc.value
        assert hasattr(error, "code"), "Error missing code"
        assert error.code == "TOOL_NOT_FOUND", "Invalid error code"
        assert str(error), "Error missing message"


@pytest.mark.asyncio
async def test_async_operation_handling(mcp_server):
    """Test async operation protocol"""
    if not hasattr(mcp_server, 'start_async_operation'):
        pytest.skip("Server does not implement start_async_operation")
    if not hasattr(mcp_server, 'get_operation_status'):
        pytest.skip("Server does not implement get_operation_status")

    # Start async operation
    operation = await mcp_server.start_async_operation(
        "create_entity", 
        {"name": "test-entity", "entity_type": "test"}
    )
    
    assert operation is not None, "Operation should not be None"
    assert "id" in operation, "Operation missing ID"
    assert "status" in operation, "Operation missing status"
    assert operation["status"] in ["pending", "running", "completed", "failed"]

    # Check operation status
    status = await mcp_server.get_operation_status(operation["id"])
    assert status["id"] == operation["id"], "Operation ID mismatch"
    assert status["status"] in ["pending", "running", "completed", "failed"]
    assert "tool" in status, "Operation status missing tool name"
    assert "arguments" in status, "Operation status missing arguments"


@pytest.mark.asyncio
async def test_session_management(mcp_server):
    """Test session handling protocol"""
    if not hasattr(mcp_server, 'create_session'):
        pytest.skip("Server does not implement create_session")
    if not hasattr(mcp_server, 'end_session'):
        pytest.skip("Server does not implement end_session")

    # Create session
    session = await mcp_server.create_session()
    assert session is not None, "Session should not be None"
    assert "id" in session, "Session missing ID"
    session_id = session["id"]

    # Use session for an operation
    if hasattr(mcp_server, 'read_resource'):
        result = await mcp_server.read_resource(
            "entities://list",
            {"session_id": session_id}
        )
        assert isinstance(result, dict), "Resource read failed"

    # End session
    await mcp_server.end_session(session_id)

    # Verify session ended - should raise error
    with pytest.raises(MCPError) as exc:
        await mcp_server.read_resource(
            "entities://list",
            {"session_id": session_id}
        )
    assert "session not found" in str(exc.value).lower()
