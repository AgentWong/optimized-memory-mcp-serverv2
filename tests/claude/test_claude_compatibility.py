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
from src.utils.errors import MCPError, ValidationError
from src.db.connection import get_db


def test_server_info_endpoint(client):
    """Test server info matches Claude Desktop requirements"""
    result = client.get_server_info()
    assert result["name"] == "Infrastructure Memory Server"
    assert result["version"] is not None
    assert result["capabilities"] is not None

def test_resource_protocol(client, db_session):
    """Test resource URL protocol handling"""
    resources = client.list_resources()
    assert len(resources) > 0, "No resources found"

    first_resource = resources[0]
    content = await client.read_resource(first_resource.uri)
    assert content, "Resource read returned no content"

    with pytest.raises(MCPError) as exc:
        client.read_resource("invalid://test")
    assert "invalid resource" in str(exc.value).lower()

@pytest.mark.asyncio
async def test_tool_execution(client, db_session):
    """Test tool execution protocol"""
    tools = await client.list_tools()
    assert len(tools) > 0, "No tools found"

    result = client.call_tool(
        "create_entity",
        arguments={
            "name": "test-entity",
            "entity_type": "test", 
            "observations": ["Initial observation"]
        }
    )
    assert isinstance(result, dict), "Result should be a dictionary"
    assert result.get("name") == "test-entity", "Entity name mismatch"

    with pytest.raises(MCPError) as exc:
        client.call_tool("invalid-tool", {"param": "test"})
    assert "unknown tool" in str(exc.value).lower()

@pytest.mark.asyncio
async def test_error_response_format(client):
    """Test error responses match Claude Desktop expectations"""
    with pytest.raises(MCPError) as exc:
        await client.read_resource("nonexistent://resource")
    
    error = exc.value
    assert error.message, "Error missing message"
    assert error.code == "RESOURCE_NOT_FOUND"

@pytest.mark.asyncio
async def test_progress_notification(client):
    """Test progress notification handling"""
    await client.send_progress_notification("test-progress", 50, 100)

@pytest.mark.asyncio
async def test_ping(client):
    """Test ping functionality"""
    result = await client.send_ping()
    assert result is not None
