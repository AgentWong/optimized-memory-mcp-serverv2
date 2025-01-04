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


async def test_create_entity_tool(mcp_server):
    """Test create_entity tool"""
    result = await mcp_server.call_tool(
        "create_entity",
        arguments={
            "name": "test_entity",
            "entity_type": "test",
            "observations": ["Initial observation"],
        },
    )
    assert result["name"] == "test_entity"
    assert isinstance(result["id"], str)


def test_add_observation_tool(mcp_server):
    """Test add_observation tool"""
    # Create entity first
    entity_result = mcp_server.call_tool(
        "create_entity", arguments={"name": "obs_test_entity", "entity_type": "test"}
    )
    entity_id = entity_result["id"]

    # Test add_observation
    result = mcp_server.call_tool(
        "add_observation",
        arguments={"entity_id": entity_id, "content": "Test observation"},
    )
    assert result is True


def test_register_provider_tool(mcp_server):
    """Test register_provider_resource tool"""
    result = mcp_server.call_tool(
        "register_provider_resource",
        arguments={
            "provider": "test_provider",
            "resource_type": "test_resource",
            "schema_version": "1.0",
            "doc_url": "https://example.com/docs",
        },
    )
    assert isinstance(result, str)  # Returns resource_id


def test_register_ansible_module_tool(mcp_server):
    """Test register_ansible_module tool"""
    result = mcp_server.call_tool(
        "register_ansible_module",
        arguments={
            "collection": "test.collection",
            "module": "test_module",
            "version": "1.0.0",
            "doc_url": "https://example.com/docs",
        },
    )
    assert isinstance(result, str)  # Returns module_id
