"""
Unit tests for API endpoints
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

def test_create_entity(client, db_session: Session):
    """Test entity creation endpoint"""
    response = client.post(
        "/entities/",
        json={
            "name": "test_entity",
            "entity_type": "test_type"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_entity"
    assert data["entity_type"] == "test_type"

    # Verify in database
    entity = db_session.query(Entity).filter_by(name="test_entity").first()
    assert entity is not None

def test_create_relationship(client, db_session: Session):
    """Test relationship creation endpoint"""
    # Create two entities first
    entity1 = Entity(name="entity1", entity_type="test_type")
    entity2 = Entity(name="entity2", entity_type="test_type")
    db_session.add_all([entity1, entity2])
    db_session.commit()

    response = client.post(
        "/relationships/",
        json={
            "source_id": entity1.id,
            "target_id": entity2.id,
            "relationship_type": "test_relationship"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["source_id"] == entity1.id
    assert data["target_id"] == entity2.id

def test_create_observation(client, db_session: Session):
    """Test observation creation endpoint"""
    # Create entity first
    entity = Entity(name="test_entity", entity_type="test_type")
    db_session.add(entity)
    db_session.commit()

    response = client.post(
        "/observations/",
        json={
            "entity_id": entity.id,
            "observation_type": "test_observation",
            "data": {"test": "data"}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["entity_id"] == entity.id
    assert data["observation_type"] == "test_observation"

def test_get_entity(client, db_session: Session):
    """Test entity retrieval endpoint"""
    entity = Entity(name="test_entity", entity_type="test_type")
    db_session.add(entity)
    db_session.commit()

    response = client.get(f"/entities/{entity.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_entity"
    assert data["entity_type"] == "test_type"

def test_get_related_entities(client, db_session: Session):
    """Test related entities endpoint"""
    # Create entities and relationship
    entity1 = Entity(name="entity1", entity_type="test_type")
    entity2 = Entity(name="entity2", entity_type="test_type")
    db_session.add_all([entity1, entity2])
    db_session.commit()

    rel = Relationship(
        source_id=entity1.id,
        target_id=entity2.id,
        relationship_type="test_relationship"
    )
    db_session.add(rel)
    db_session.commit()

    response = client.get(
        f"/context/related/{entity1.id}",
        params={"max_depth": 1}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(e["id"] == entity2.id for e in data)
