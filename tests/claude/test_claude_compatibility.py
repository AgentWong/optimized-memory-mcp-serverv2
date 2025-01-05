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
    assert isinstance(result, dict), "Result should be dictionary"
    assert result["name"] == "Infrastructure Memory Server", "Wrong server name"
    assert result["version"] is not None, "Missing version"
    assert isinstance(result["capabilities"], dict), "Capabilities should be dictionary"
    assert "resources" in result["capabilities"], "Missing resources capability"
    assert "tools" in result["capabilities"], "Missing tools capability"

def test_resource_protocol(client, db_session):
    """Test resource URL protocol handling"""
    # Test resource listing
    resources = client.list_resources()
    assert len(resources) > 0, "No resources found"
    assert isinstance(resources, list), "Resources should be list"
    
    # Validate resource structure
    first_resource = resources[0]
    assert isinstance(first_resource, dict), "Resource should be dictionary"
    assert "uri" in first_resource, "Resource missing URI"
    assert "name" in first_resource, "Resource missing name"
    assert "type" in first_resource, "Resource missing type"
    
    # Test resource reading
    content = client.read_resource(first_resource["uri"])
    assert content is not None, "Resource read returned no content"
    assert isinstance(content, (str, dict)), "Content should be string or dict"
    if isinstance(content, dict):
        assert "data" in content, "Content missing data field"
        assert "type" in content, "Content missing type field"
    
    # Test error handling
    with pytest.raises(MCPError) as exc:
        client.read_resource("invalid://test")
    error = exc.value
    assert error.code == "INVALID_RESOURCE", "Wrong error code"
    assert "invalid resource" in str(error).lower(), "Wrong error message"
    assert error.details is not None, "Error missing details"

def test_tool_execution(client, db_session):
    """Test tool execution protocol"""
    tools = client.list_tools()
    assert len(tools) > 0, "No tools found"

    result = client.call_tool(
        "create_entity",
        {
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

def test_error_response_format(client):
    """Test error responses match Claude Desktop expectations"""
    with pytest.raises(MCPError) as exc:
        client.read_resource("nonexistent://resource")
    
    error = exc.value
    assert error.message, "Error missing message"
    assert error.code == "RESOURCE_NOT_FOUND"

def test_progress_notification(client):
    """Test progress notification handling"""
    result = client.send_progress_notification("test-progress", 50, 100)
    assert result is None, "Progress notification should return None"

def test_ping(client):
    """Test ping functionality"""
    result = client.send_ping()
    assert result is not None
