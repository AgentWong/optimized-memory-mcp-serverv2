"""
Unit tests for MCP tools.

Tests the core MCP tool patterns:
- create_entity - Creates new entities with initial observations
- add_observation - Adds observations to existing entities
- register_provider_resource - Registers new provider resource types
- register_ansible_module - Registers new Ansible modules

Each tool follows the MCP protocol for performing actions and side effects.
"""

import pytest
from src.main import create_server
from src.db.connection import get_db
from src.utils.errors import MCPError


@pytest.fixture
def db_session():
    """Provide a database session for testing"""
    session = next(get_db())
    try:
        yield session
    finally:
        session.close()


@pytest.mark.asyncio
async def test_create_entity_tool(mcp_server):
    """Test create_entity tool"""
    if not hasattr(mcp_server, 'start_async_operation'):
        pytest.skip("Server does not implement start_async_operation")
        
    operation = await mcp_server.start_async_operation(
        "create_entity",
        {
            "name": "test_entity",
            "entity_type": "test",
            "observations": ["Initial observation"]
        }
    )
    
    assert operation["status"] == "completed", "Operation failed"
    result = operation["result"]
    assert isinstance(result, dict), "Result should be a dictionary"
    assert result["name"] == "test_entity", "Entity name mismatch"
    assert isinstance(result["id"], str), "Entity ID should be string"


@pytest.mark.asyncio
async def test_add_observation_tool(mcp_server):
    """Test add_observation tool"""
    if not hasattr(mcp_server, 'start_async_operation'):
        pytest.skip("Server does not implement start_async_operation")
        
    # Create entity first
    entity_op = await mcp_server.start_async_operation(
        "create_entity", 
        {"name": "obs_test_entity", "entity_type": "test"}
    )
    assert entity_op["status"] == "completed", "Entity creation failed"
    entity_id = entity_op["result"]["id"]
    
    # Test add_observation
    obs_op = await mcp_server.start_async_operation(
        "add_observation",
        {
            "entity_id": entity_id,
            "type": "test",
            "observation_type": "test",
            "value": {"test": "data"}
        }
    )
    assert obs_op["status"] == "completed", "Observation creation failed"
    assert isinstance(obs_op["result"], dict), "Result should be a dictionary"
    assert "id" in obs_op["result"], "Result missing observation ID"


@pytest.mark.asyncio
async def test_register_provider_tool(mcp_server):
    """Test register_provider_resource tool"""
    if not hasattr(mcp_server, 'start_async_operation'):
        pytest.skip("Server does not implement start_async_operation")
        
    operation = await mcp_server.start_async_operation(
        "register_provider_resource",
        {
            "provider": "test_provider",
            "resource_type": "test_resource", 
            "schema_version": "1.0",
            "doc_url": "https://example.com/docs"
        }
    )
    
    assert operation["status"] == "completed", "Provider registration failed"
    result = operation["result"]
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "id" in result, "Result missing provider ID"


@pytest.mark.asyncio
async def test_register_ansible_module_tool(mcp_server):
    """Test register_ansible_module tool"""
    if not hasattr(mcp_server, 'start_async_operation'):
        pytest.skip("Server does not implement start_async_operation")
        
    operation = await mcp_server.start_async_operation(
        "register_ansible_module",
        {
            "collection": "test.collection",
            "module": "test_module",
            "version": "1.0.0",
            "doc_url": "https://example.com/docs"
        }
    )
    
    assert operation["status"] == "completed", "Module registration failed"
    result = operation["result"]
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "id" in result, "Result missing module ID"


@pytest.mark.asyncio
async def test_tool_error_handling(mcp_server):
    """Test tool error handling"""
    if not hasattr(mcp_server, 'start_async_operation'):
        pytest.skip("Server does not implement start_async_operation")
        
    # Test invalid tool
    with pytest.raises(MCPError) as exc:
        await mcp_server.start_async_operation("invalid_tool", {})
    assert "not found" in str(exc.value).lower()
    assert exc.value.code == "TOOL_NOT_FOUND"

    # Test invalid arguments
    with pytest.raises(MCPError) as exc:
        await mcp_server.start_async_operation(
            "create_entity",
            {"invalid_arg": "value"}  # Missing required args
        )
    assert "invalid" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_tool_operation_status(mcp_server):
    """Test async operation status handling"""
    if not hasattr(mcp_server, 'start_async_operation'):
        pytest.skip("Server does not implement start_async_operation")
    if not hasattr(mcp_server, 'get_operation_status'):
        pytest.skip("Server does not implement get_operation_status")
        
    # Start operation
    operation = await mcp_server.start_async_operation(
        "create_entity",
        {"name": "status_test", "entity_type": "test"}
    )
    
    # Check status fields
    assert "id" in operation, "Operation missing ID"
    assert "status" in operation, "Operation missing status"
    assert "tool" in operation, "Operation missing tool name"
    assert "arguments" in operation, "Operation missing arguments"
    assert "created_at" in operation, "Operation missing creation timestamp"
    
    if operation["status"] == "completed":
        assert "result" in operation, "Completed operation missing result"
        assert "completed_at" in operation, "Completed operation missing completion timestamp"
    elif operation["status"] == "failed":
        assert "error" in operation, "Failed operation missing error message"
