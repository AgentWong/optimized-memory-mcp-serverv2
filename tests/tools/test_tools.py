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
from tests.conftest import TestClient


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
        session.close()


@pytest.mark.asyncio
async def test_create_entity_tool(mcp_server):
    """Test create_entity tool"""
    client = TestClient(mcp_server)
    result = await client.call_tool(
        "create_entity",
        arguments={
            "name": "test_entity",
            "entity_type": "test",
            "observations": ["Initial observation"],
        },
    )
    assert result["name"] == "test_entity"
    assert isinstance(result["id"], str)
    await client.close()


@pytest.mark.asyncio
async def test_add_observation_tool(mcp_server):
    """Test add_observation tool"""
    client = TestClient(mcp_server)
    try:
        # Create entity first
        entity_result = await client.call_tool(
            "create_entity", arguments={"name": "obs_test_entity", "entity_type": "test"}
        )
        entity_id = entity_result["id"]

        # Test add_observation
        result = await client.call_tool(
            "add_observation",
            arguments={"entity_id": entity_id, "content": "Test observation"},
        )
        assert result is True
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_register_provider_tool(mcp_server):
    """Test register_provider_resource tool"""
    client = TestClient(mcp_server)
    try:
        result = await client.call_tool(
            "register_provider_resource",
            arguments={
                "provider": "test_provider",
                "resource_type": "test_resource", 
                "schema_version": "1.0",
                "doc_url": "https://example.com/docs",
            },
        )
        assert isinstance(result, str)  # Returns resource_id
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_register_ansible_module_tool(mcp_server):
    """Test register_ansible_module tool"""
    client = TestClient(mcp_server)
    try:
        result = await client.call_tool(
            "register_ansible_module",
            arguments={
                "collection": "test.collection",
                "module": "test_module",
                "version": "1.0.0",
                "doc_url": "https://example.com/docs",
            },
        )
        assert isinstance(result, str)  # Returns module_id
    finally:
        await client.close()
