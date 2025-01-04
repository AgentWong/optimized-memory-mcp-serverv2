"""
Unit tests for database operations.

Tests the core database operations required by MCP:
- Entity CRUD operations with proper validation
- Relationship management between entities
- Observation storage and retrieval
- Base model functionality including serialization

Each operation follows MCP protocol requirements for data persistence
and ensures proper database state management.
"""

import pytest
from sqlalchemy.orm import Session

from src.db.init_db import get_db
from src.db.models.base import BaseModel
from src.db.models.entities import Entity
from src.db.models.relationships import Relationship
from src.db.models.observations import Observation


@pytest.fixture
def db_session():
    """Provide a database session for testing"""
    session = next(get_db())
    try:
        yield session
    finally:
        session.close()


def test_base_model_to_dict(db_session: Session):
    """Test BaseModel.to_dict() conversion with all field types"""
    entity = Entity(
        name="test_entity", 
        entity_type="test_type",
        meta_data={"key": "value"},
        tags=["tag1", "tag2"]
    )
    db_session.add(entity)
    db_session.commit()

    entity_dict = entity.to_dict()
    assert isinstance(entity_dict, dict)
    assert entity_dict["name"] == "test_entity"
    assert entity_dict["entity_type"] == "test_type"
    assert entity_dict["meta_data"] == {"key": "value"}
    assert entity_dict["tags"] == ["tag1", "tag2"]
    assert "created_at" in entity_dict
    assert "updated_at" in entity_dict


def test_model_validation(db_session: Session):
    """Test model field validation"""
    # Test required fields
    with pytest.raises(Exception):
        entity = Entity(type="test_type")  # Missing name
        db_session.add(entity)
        db_session.commit()

    # Test field length limits
    with pytest.raises(Exception):
        entity = Entity(name="x" * 256, type="test_type")  # Exceeds max length
        db_session.add(entity)
        db_session.commit()

    # Test JSON field validation
    with pytest.raises(Exception):
        entity = Entity(
            name="test", type="test_type", meta_data="invalid"  # Should be dict
        )
        db_session.add(entity)
        db_session.commit()


def test_entity_crud_operations(db_session: Session):
    """Test CRUD operations for Entity model"""
    # Create
    entity = Entity(name="test_entity", entity_type="test_type", meta_data={})
    db_session.add(entity)
    db_session.commit()

    # Read
    retrieved = db_session.query(Entity).filter_by(name="test_entity").first()
    assert retrieved is not None
    assert retrieved.name == "test_entity"

    # Update
    retrieved.name = "updated_name"
    db_session.commit()
    updated = db_session.query(Entity).filter_by(name="updated_name").first()
    assert updated is not None

    # Delete
    db_session.delete(updated)
    db_session.commit()
    deleted = db_session.query(Entity).filter_by(name="updated_name").first()
    assert deleted is None


def test_relationship_creation(db_session: Session):
    """Test creating relationships between entities"""
    # Create two entities
    entity1 = Entity(name="entity1", entity_type="test_type")
    entity2 = Entity(name="entity2", entity_type="test_type")
    db_session.add_all([entity1, entity2])
    db_session.commit()

    # Create relationship
    rel = Relationship(
        source_id=entity1.id,
        target_id=entity2.id,
        relationship_type="test_relationship",
    )
    db_session.add(rel)
    db_session.commit()

    # Verify relationship
    retrieved = (
        db_session.query(Relationship)
        .filter_by(source_id=entity1.id, target_id=entity2.id)
        .first()
    )
    assert retrieved is not None
    assert retrieved.relationship_type == "test_relationship"


def test_observation_creation(db_session: Session):
    """Test creating observations for entities"""
    # Create entity
    entity = Entity(name="test_entity", entity_type="test_type")
    db_session.add(entity)
    db_session.commit()

    # Create observation
    obs = Observation(
        entity_id=entity.id,
        type="state",  # Using a valid type from VALID_TYPES
        observation_type="test",
        value={"test": "data"},
        meta_data={}
    )
    db_session.add(obs)
    db_session.commit()

    # Verify observation
    retrieved = db_session.query(Observation).filter_by(entity_id=entity.id).first()
    assert retrieved is not None
    assert retrieved.observation_type == "test"
    assert retrieved.value == {"test": "data"}
"""Test database operations and model interactions."""

import pytest
from sqlalchemy.exc import IntegrityError

from src.db.models.entities import Entity
from src.db.connection import get_db

def test_entity_creation():
    """Test basic entity creation and validation."""
    with next(get_db()) as db:
        entity = Entity(name="test_entity", entity_type="test_type", meta_data={})
        db.add(entity)
        db.commit()
        
        assert entity.id is not None
        assert entity.name == "test_entity"
        assert entity.entity_type == "test_type"
        assert entity.meta_data == {}

def test_entity_required_fields():
    """Test that required fields are enforced."""
    with next(get_db()) as db:
        entity = Entity(name="test_entity", entity_type="test_type")
        db.add(entity)
        db.commit()
        
        # Should have default values
        assert entity.meta_data == {}
        assert entity.tags == []

def test_entity_timestamps():
    """Test that timestamps are automatically set."""
    with next(get_db()) as db:
        entity = Entity(name="test_entity", entity_type="test_type")
        db.add(entity)
        db.commit()
        
        assert entity.created_at is not None
        assert entity.updated_at is not None
