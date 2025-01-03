"""
End-to-end integration tests for API endpoints.

Tests complete workflow patterns required by MCP:
- Full entity lifecycle management
- Relationship creation and validation
- Observation handling and storage
- Search and analysis operations
- Error handling scenarios

Each test verifies end-to-end functionality across multiple
MCP components working together.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.main import create_server
from src.db.connection import get_db
from src.db.models.entities import Entity
from src.db.models.relationships import Relationship
from src.db.models.observations import Observation

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

def test_full_entity_workflow(client, db_session: Session):
    """Test complete entity lifecycle including relationships and observations"""
    # Create initial entity
    entity1_response = client.post(
        "/entities/",
        json={
            "name": "test_entity_1",
            "entity_type": "test_type"
        }
    )
    assert entity1_response.status_code == 200
    entity1_data = entity1_response.json()
    entity1_id = entity1_data["id"]

    # Create related entity
    entity2_response = client.post(
        "/entities/",
        json={
            "name": "test_entity_2",
            "entity_type": "test_type"
        }
    )
    assert entity2_response.status_code == 200
    entity2_data = entity2_response.json()
    entity2_id = entity2_data["id"]

    # Create relationship between entities
    rel_response = client.post(
        "/relationships/",
        json={
            "source_id": entity1_id,
            "target_id": entity2_id,
            "relationship_type": "test_relationship"
        }
    )
    assert rel_response.status_code == 200

    # Add observation to first entity
    obs_response = client.post(
        "/observations/",
        json={
            "entity_id": entity1_id,
            "observation_type": "test_observation",
            "data": {"test": "data"}
        }
    )
    assert obs_response.status_code == 200

    # Get related entities
    related_response = client.get(
        f"/context/related/{entity1_id}",
        params={"max_depth": 1}
    )
    assert related_response.status_code == 200
    related_data = related_response.json()
    assert len(related_data) > 0
    assert any(e["id"] == entity2_id for e in related_data)

def test_search_and_analysis_workflow(client, db_session: Session):
    """Test search functionality with analysis endpoints"""
    # Create test entities
    entity_response = client.post(
        "/entities/",
        json={
            "name": "searchable_entity",
            "entity_type": "test_type"
        }
    )
    assert entity_response.status_code == 200

    # Search for entity
    search_response = client.get(
        "/search/",
        params={"q": "searchable"}
    )
    assert search_response.status_code == 200
    search_data = search_response.json()
    assert len(search_data) > 0
    assert any(e["name"] == "searchable_entity" for e in search_data)

def test_error_handling(client):
    """Test API error handling"""
    # Test invalid entity ID
    response = client.get("/entities/99999")
    assert response.status_code == 404

    # Test invalid relationship creation
    response = client.post(
        "/relationships/",
        json={
            "source_id": 99999,
            "target_id": 99999,
            "relationship_type": "test"
        }
    )
    assert response.status_code in (404, 400)

    # Test invalid observation creation
    response = client.post(
        "/observations/",
        json={
            "entity_id": 99999,
            "observation_type": "test",
            "data": {}
        }
    )
    assert response.status_code in (404, 400)
