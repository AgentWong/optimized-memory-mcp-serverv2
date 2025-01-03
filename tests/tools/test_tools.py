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
from fastapi.testclient import TestClient

from src.main import create_server
from src.db.connection import get_db

@pytest.fixture
def client():
    """Create test client"""
    server = create_server()
    return TestClient(server.app)

@pytest.fixture
def db_session():
    """Provide a database session for testing"""
    session = next(get_db())
    try:
        yield session
    finally:
        session.close()

def test_create_entity_tool(client):
    """Test create_entity tool"""
    response = client.post(
        "/tools/create_entity",
        json={
            "name": "test_entity",
            "entity_type": "test",
            "observations": ["Initial observation"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_entity"
    assert isinstance(data["id"], str)

def test_add_observation_tool(client):
    """Test add_observation tool"""
    # Create entity first
    entity_response = client.post(
        "/tools/create_entity",
        json={
            "name": "obs_test_entity",
            "entity_type": "test"
        }
    )
    entity_id = entity_response.json()["id"]
    
    # Test add_observation
    response = client.post(
        "/tools/add_observation",
        json={
            "entity_id": entity_id,
            "content": "Test observation"
        }
    )
    assert response.status_code == 200
    assert response.json() is True

def test_register_provider_tool(client):
    """Test register_provider_resource tool"""
    response = client.post(
        "/tools/register_provider_resource",
        json={
            "provider": "test_provider",
            "resource_type": "test_resource",
            "schema_version": "1.0",
            "doc_url": "https://example.com/docs"
        }
    )
    assert response.status_code == 200
    assert isinstance(response.json(), str)  # Returns resource_id

def test_register_ansible_module_tool(client):
    """Test register_ansible_module tool"""
    response = client.post(
        "/tools/register_ansible_module",
        json={
            "collection": "test.collection",
            "module": "test_module",
            "version": "1.0.0",
            "doc_url": "https://example.com/docs"
        }
    )
    assert response.status_code == 200
    assert isinstance(response.json(), str)  # Returns module_id
