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


def test_server_info_endpoint(client):
    """Test server info matches Claude Desktop requirements"""
    # Get initialization result which contains server info
    result = client.initialize()
    
    assert result.serverInfo.name == "Infrastructure Memory Server"
    assert result.serverInfo.version is not None
    assert result.capabilities is not None


def test_resource_protocol(client):
    """Test resource URL protocol handling"""
    # List resources using SDK method
    result = client.list_resources()
    assert len(result.resources) > 0, "No resources found"

    # Test reading a valid resource
    first_resource = result.resources[0]
    result = client.read_resource(first_resource.uri)
    assert result.contents, "Resource read returned no content"

    # Test invalid resource
    with pytest.raises(MCPError) as exc:
        client.read_resource("invalid://test")
    assert "invalid resource" in str(exc.value).lower()


def test_tool_execution(client):
    """Test tool execution protocol"""
    # List available tools
    result = client.list_tools()
    assert len(result.tools) > 0, "No tools found"

    # Test tool invocation
    result = client.call_tool(
        "create_entity",
        {
            "name": "test-entity",
            "entity_type": "test", 
            "observations": ["Initial observation"]
        }
    )
    assert result.content, "Tool returned no content"
    assert not result.isError, "Tool execution failed"

    # Test invalid tool
    with pytest.raises(MCPError) as exc:
        client.call_tool("invalid-tool", {"param": "test"})
    assert "unknown tool" in str(exc.value).lower()


def test_error_response_format(client):
    """Test error responses match Claude Desktop expectations"""
    with pytest.raises(MCPError) as exc:
        client.read_resource("nonexistent://resource")
    
    error = exc.value
    assert error.message, "Error missing message"
    assert error.code == "RESOURCE_NOT_FOUND"


def test_progress_notification(client):
    """Test progress notification handling"""
    # Send a progress notification
    client.send_progress_notification("test-progress", 50, 100)
    # No assertion needed - just verifying it doesn't raise an exception


def test_ping(client):
    """Test ping functionality"""
    result = client.send_ping()
    assert result is not None
