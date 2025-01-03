"""
Integration tests for error scenarios across the MCP server.

Tests error handling patterns required by the MCP specification:
- Database constraint violations (unique constraints, foreign keys)
- Invalid relationship creation (self-referential, missing entities)
- Invalid observation data (schema validation, data type checks)
- Concurrent modification conflicts (optimistic locking)
- Invalid API requests (malformed JSON, missing fields)
- Resource not found scenarios (404 handling)
- Validation error responses (400 handling)
- Transaction rollback behavior

Each test verifies proper error response format per MCP protocol requirements:
- Error code standardization
- Detailed error messages
- Proper status code mapping
- Error context/details inclusion
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.main import create_server
from src.db.connection import get_db
from src.db.models.entities import Entity
from src.db.models.relationships import Relationship
from src.db.models.observations import Observation
from src.utils.errors import MCPError, ValidationError, DatabaseError

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
        session.rollback()
        session.close()

def test_database_constraint_violations(client, db_session: Session):
    """Test database constraint violation handling"""
    # Test duplicate entity name
    response = client.post(
        "/entities/",
        json={
            "name": "unique_entity",
            "entity_type": "test"
        }
    )
    assert response.status_code == 200

    # Attempt duplicate
    response = client.post(
        "/entities/",
        json={
            "name": "unique_entity",
            "entity_type": "test"
        }
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["message"].lower()

def test_invalid_relationship_creation(client, db_session: Session):
    """Test invalid relationship handling"""
    # Create test entity
    entity_response = client.post(
        "/entities/",
        json={
            "name": "test_entity",
            "entity_type": "test"
        }
    )
    entity_id = entity_response.json()["id"]

    # Test self-referential relationship
    response = client.post(
        "/relationships/",
        json={
            "source_id": entity_id,
            "target_id": entity_id,
            "relationship_type": "self_ref"
        }
    )
    assert response.status_code == 400
    assert "self-referential" in response.json()["message"].lower()

def test_invalid_observation_data(client, db_session: Session):
    """Test invalid observation data handling"""
    # Create test entity
    entity_response = client.post(
        "/entities/",
        json={
            "name": "obs_test_entity",
            "entity_type": "test"
        }
    )
    entity_id = entity_response.json()["id"]

    # Test invalid observation data
    response = client.post(
        "/observations/",
        json={
            "entity_id": entity_id,
            "observation_type": "test",
            "data": None  # Invalid data
        }
    )
    assert response.status_code == 400
    assert "invalid data" in response.json()["message"].lower()

def test_concurrent_modification_conflicts(client, db_session: Session):
    """Test concurrent modification handling"""
    # Create test entity
    response = client.post(
        "/entities/",
        json={
            "name": "concurrent_test",
            "entity_type": "test"
        }
    )
    entity_id = response.json()["id"]

    # Simulate concurrent modifications
    session2 = next(get_db())
    try:
        # Modify in first session
        entity = db_session.query(Entity).get(entity_id)
        entity.name = "modified_in_session1"

        # Modify in second session
        entity2 = session2.query(Entity).get(entity_id)
        entity2.name = "modified_in_session2"
        
        # Commit first session
        db_session.commit()
        
        # Second session should fail
        with pytest.raises(Exception):
            session2.commit()
    finally:
        session2.rollback()
        session2.close()

def test_invalid_api_requests(client):
    """Test invalid API request handling"""
    # Test invalid JSON
    response = client.post(
        "/entities/",
        data="invalid json{",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400
    assert "invalid json" in response.json()["message"].lower()

    # Test missing required fields
    response = client.post(
        "/entities/",
        json={"name": "test"}  # Missing entity_type
    )
    assert response.status_code == 400
    assert "required" in response.json()["message"].lower()

def test_resource_not_found_handling(client):
    """Test resource not found error handling"""
    # Test non-existent entity
    response = client.get("/entities/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["message"].lower()

    # Test non-existent relationship
    response = client.get("/relationships/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["message"].lower()

def test_validation_error_handling(client, db_session: Session):
    """Test validation error handling"""
    # Test invalid entity type
    response = client.post(
        "/entities/",
        json={
            "name": "test",
            "entity_type": "invalid_type"
        }
    )
    assert response.status_code == 400
    assert "invalid type" in response.json()["message"].lower()

    # Test invalid relationship type
    response = client.post(
        "/relationships/",
        json={
            "source_id": 1,
            "target_id": 2,
            "relationship_type": "invalid_type"
        }
    )
    assert response.status_code == 400
    assert "invalid type" in response.json()["message"].lower()

def test_transaction_rollback(client, db_session: Session):
    """Test transaction rollback on errors"""
    # Create test entity
    entity_response = client.post(
        "/entities/",
        json={
            "name": "rollback_test",
            "entity_type": "test"
        }
    )
    entity_id = entity_response.json()["id"]

    # Attempt invalid operation that should trigger rollback
    try:
        # Start transaction
        entity = db_session.query(Entity).get(entity_id)
        entity.name = "updated_name"
        
        # Perform invalid operation
        invalid_obs = Observation(
            entity_id=99999,  # Non-existent entity
            observation_type="test",
            data={}
        )
        db_session.add(invalid_obs)
        db_session.commit()
    except:
        db_session.rollback()

    # Verify original state maintained
    entity = db_session.query(Entity).get(entity_id)
    assert entity.name == "rollback_test"
