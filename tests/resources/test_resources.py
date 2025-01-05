"""
Unit tests for MCP resources.

from src.utils.errors import MCPError

Tests the core MCP resource patterns:
- entities://list - Lists all entities in the system
- entities://{id} - Gets details for a specific entity
- providers://{provider}/resources - Lists resources for a provider
- ansible://collections - Lists registered Ansible collections

Each resource follows the MCP protocol for read-only data access.
"""

import pytest

from src.main import create_server
from src.db.connection import get_db
from src.db.models.base import Base


@pytest.fixture
def client():
    """Create test client"""
    server = create_server()
    return server


@pytest.fixture
def db_session():
    """Provide a database session for testing"""
    session = next(get_db())
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(bind=session.bind)
        Base.metadata.create_all(bind=session.bind)


@pytest.mark.asyncio
async def test_entities_list_resource(mcp_server):
    """Test entities://list resource"""
    if not hasattr(mcp_server, 'read_resource'):
        pytest.skip("Server does not implement read_resource")
        
    result = await mcp_server.read_resource(
        "entities://list",
        {
            "page": 1,
            "per_page": 10,
            "type": None,
            "created_after": None,
            "ctx": {}
        }
    )
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "data" in result, "Result missing 'data' field"
    assert isinstance(result["data"], list), "Data should be a list"
    assert "resource_path" in result, "Result missing 'resource_path'"
    assert "timestamp" in result, "Result missing 'timestamp'"


@pytest.mark.asyncio
async def test_entity_detail_resource(mcp_server, db_session):
    """Test entities://{id} resource"""
    if not hasattr(mcp_server, 'start_async_operation'):
        pytest.skip("Server does not implement start_async_operation")
    if not hasattr(mcp_server, 'read_resource'):
        pytest.skip("Server does not implement read_resource")
        
    # Create test entity first
    operation = await mcp_server.start_async_operation(
        "create_entity", 
        {"name": "test_entity", "entity_type": "test"}
    )
    assert operation["status"] == "completed", "Entity creation failed"
    entity_id = operation["result"]["id"]
    assert entity_id, "No entity ID returned"

    # Test resource
    result = await mcp_server.read_resource(f"entities://{entity_id}")
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "data" in result, "Result missing 'data' field"
    assert result["data"]["name"] == "test_entity", "Entity name mismatch"
    assert result["data"]["id"] == entity_id, "Entity ID mismatch"


@pytest.mark.asyncio
async def test_providers_resource(mcp_server):
    """Test providers://{provider}/resources resource"""
    if not hasattr(mcp_server, 'read_resource'):
        pytest.skip("Server does not implement read_resource")
        
    result = await mcp_server.read_resource(
        "providers://test/resources",
        {"version": "latest"}
    )
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "data" in result, "Result missing 'data' field"
    assert isinstance(result["data"], list), "Provider resources should be a list"


@pytest.mark.asyncio
async def test_ansible_collections_resource(mcp_server):
    """Test ansible://collections resource"""
    if not hasattr(mcp_server, 'read_resource'):
        pytest.skip("Server does not implement read_resource")
        
    result = await mcp_server.read_resource("ansible://collections")
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "data" in result, "Result missing 'data' field"
    assert isinstance(result["data"], list), "Collections should be a list"
@pytest.mark.asyncio
async def test_resource_error_handling(mcp_server):
    """Test resource error handling"""
    if not hasattr(mcp_server, 'read_resource'):
        pytest.skip("Server does not implement read_resource")
        
    # Test invalid resource path
    with pytest.raises(MCPError) as exc:
        await mcp_server.read_resource("invalid://resource")
    assert "not found" in str(exc.value).lower()
    assert hasattr(exc.value, "code")
    assert exc.value.code in ["RESOURCE_NOT_FOUND", "INVALID_RESOURCE"]

    # Test invalid parameters
    with pytest.raises(MCPError) as exc:
        await mcp_server.read_resource(
            "entities://list",
            {"invalid_param": "value"}
        )
    assert "invalid" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_resource_pagination(mcp_server):
    """Test resource pagination"""
    if not hasattr(mcp_server, 'read_resource'):
        pytest.skip("Server does not implement read_resource")
        
    # Create multiple test entities
    if hasattr(mcp_server, 'start_async_operation'):
        for i in range(5):
            await mcp_server.start_async_operation(
                "create_entity",
                {"name": f"test_entity_{i}", "entity_type": "test"}
            )
    
    # Test first page
    result = await mcp_server.read_resource(
        "entities://list",
        {"page": 1, "per_page": 2}
    )
    assert isinstance(result["data"], list)
    assert len(result["data"]) <= 2, "Page size exceeded"
    assert "total" in result, "Missing total count"
    assert "pages" in result, "Missing total pages"
    
    # Verify next page
    if len(result["data"]) == 2:
        next_page = await mcp_server.read_resource(
            "entities://list",
            {"page": 2, "per_page": 2}
        )
        assert isinstance(next_page["data"], list)
        assert next_page["data"] != result["data"], "Pages should be different"
        assert len(next_page["data"]) <= 2, "Page size exceeded"
