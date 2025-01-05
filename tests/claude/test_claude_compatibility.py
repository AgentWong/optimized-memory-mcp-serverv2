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
from src.utils.errors import MCPError


@pytest.mark.asyncio
async def test_server_info_endpoint(client):
    """Test server info matches Claude Desktop requirements"""
    # Initialize will have already been called in the fixture
    result = await client.initialize()

    # Verify required fields from initialize result
    assert result.serverInfo.name, "Server info missing 'name' field"
    assert result.serverInfo.version, "Server info missing 'version' field"
    assert result.capabilities, "Server info missing 'capabilities' field"


@pytest.mark.asyncio
async def test_resource_protocol(client):
    """Test resource URL protocol handling"""
    # Test valid resource with parameters
    resources = await client.list_resources()
    assert len(resources.resources) > 0, "No resources found"

    # Test reading a valid resource
    first_resource = resources.resources[0]
    result = await client.read_resource(first_resource.uri)
    assert result.contents, "Resource read returned no content"

    # Test invalid resource
    with pytest.raises(Exception) as exc:
        await client.read_resource("invalid://test")
    assert "invalid resource" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_tool_execution(client):
    """Test tool execution protocol"""
    # List available tools
    tools = await client.list_tools()
    assert len(tools.tools) > 0, "No tools found"

    # Test tool invocation with create_entity tool
    result = await client.call_tool(
        "create_entity",
        {
            "name": "test-entity",
            "entity_type": "test",
            "observations": ["Initial observation"]
        }
    )
    assert not result.isError, "Tool execution failed"
    assert result.content, "Tool returned no content"

    # Test invalid tool
    with pytest.raises(Exception) as exc:
        await client.call_tool("invalid-tool", {"param": "test"})
    assert "tool not found" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_error_response_format(client):
    """Test error responses match Claude Desktop expectations"""
    # Test with invalid resource path
    with pytest.raises(Exception) as exc:
        await client.read_resource("nonexistent://resource")
    
    error = exc.value
    assert str(error), "Error missing message"


@pytest.mark.asyncio
async def test_progress_notification(client):
    """Test progress notification handling"""
    # Send a progress notification
    await client.send_progress_notification("test-progress", 50, 100)

    # No assertion needed - just verifying it doesn't raise an exception


@pytest.mark.asyncio
async def test_ping(client):
    """Test ping functionality"""
    result = await client.send_ping()
    assert result is not None
