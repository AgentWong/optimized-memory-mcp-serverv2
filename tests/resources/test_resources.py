"""
Unit tests for MCP resources.

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
    result = await mcp_server.read_resource(
        "entities://list",
        {
            "page": "1",
            "per_page": "10",
            "type": "null",
            "created_after": "null",
            "ctx": {}
        }
    )
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_entity_detail_resource(mcp_server, db_session):
    """Test entities://{id} resource"""
    # Create test entity first
    result = await mcp_server.call_tool(
        "create_entity", arguments={"name": "test_entity", "entity_type": "test"}
    )
    entity_id = result["id"]

    # Test resource
    entity = await mcp_server.read_resource(f"entities://{entity_id}")
    assert entity["name"] == "test_entity"


@pytest.mark.asyncio
async def test_providers_resource(mcp_server):
    """Test providers://{provider}/resources resource"""
    result = await mcp_server.read_resource("providers://test/resources")
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_ansible_collections_resource(mcp_server):
    """Test ansible://collections resource"""
    result = await mcp_server.read_resource("ansible://collections")
    assert isinstance(result, list)
