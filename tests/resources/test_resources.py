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


def test_entities_list_resource(client):
    """Test entities://list resource"""
    response = client.get("/resource/entities://list")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_entity_detail_resource(client, db_session):
    """Test entities://{id} resource"""
    # Create test entity first
    response = client.post(
        "/tools/create_entity", json={"name": "test_entity", "entity_type": "test"}
    )
    entity_id = response.json()["id"]

    # Test resource
    response = client.get(f"/resource/entities://{entity_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_entity"


def test_providers_resource(client):
    """Test providers://{provider}/resources resource"""
    response = client.get("/resource/providers://test/resources")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_ansible_collections_resource(client):
    """Test ansible://collections resource"""
    response = client.get("/resource/ansible://collections")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
