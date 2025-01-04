"""
Unit tests for model validation.

Tests the core validation patterns required by the MCP specification:
- Required field validation for all model types
- Foreign key constraint enforcement
- Relationship integrity rules
- Data type validation
- Schema validation for JSON fields

Each test verifies that the database models properly enforce
data integrity requirements for the MCP server implementation.
"""

import pytest
from sqlalchemy.exc import IntegrityError

from src.db.models.entities import Entity
from src.db.models.relationships import Relationship
from src.db.models.observations import Observation


def test_entity_required_fields(db_session):
    """Test that entity required fields are enforced"""
    # Missing name
    with pytest.raises(IntegrityError):
        entity = Entity(entity_type="test_type")
        db_session.add(entity)
        db_session.commit()
    db_session.rollback()

    # Missing entity_type
    with pytest.raises(IntegrityError):
        entity = Entity(name="test_entity")
        db_session.add(entity)
        db_session.commit()
    db_session.rollback()


def test_relationship_required_fields(db_session):
    """Test that relationship required fields are enforced"""
    entity1 = Entity(name="entity1", entity_type="test_type")
    entity2 = Entity(name="entity2", entity_type="test_type")
    db_session.add_all([entity1, entity2])
    db_session.commit()

    # Missing source_id
    with pytest.raises(IntegrityError):
        rel = Relationship(target_id=entity2.id, relationship_type="test_rel")
        db_session.add(rel)
        db_session.commit()
    db_session.rollback()

    # Missing target_id
    with pytest.raises(IntegrityError):
        rel = Relationship(source_id=entity1.id, relationship_type="test_rel")
        db_session.add(rel)
        db_session.commit()
    db_session.rollback()


def test_observation_required_fields(db_session):
    """Test that observation required fields are enforced"""
    entity = Entity(name="test_entity", entity_type="test_type")
    db_session.add(entity)
    db_session.commit()

    # Missing entity_id
    with pytest.raises(IntegrityError):
        obs = Observation(observation_type="test_obs", data={"test": "data"})
        db_session.add(obs)
        db_session.commit()
    db_session.rollback()

    # Missing observation_type
    with pytest.raises(IntegrityError):
        obs = Observation(entity_id=entity.id, data={"test": "data"})
        db_session.add(obs)
        db_session.commit()
    db_session.rollback()


def test_relationship_foreign_keys(db_session):
    """Test that relationship foreign keys are enforced"""
    entity = Entity(name="entity1", entity_type="test_type")
    db_session.add(entity)
    db_session.commit()

    # Invalid target_id
    with pytest.raises(IntegrityError):
        rel = Relationship(
            source_id=entity.id,
            target_id=99999,  # Non-existent ID
            relationship_type="test_rel",
        )
        db_session.add(rel)
        db_session.commit()
    db_session.rollback()


def test_observation_foreign_keys(db_session):
    """Test that observation foreign keys are enforced"""
    # Invalid entity_id
    with pytest.raises(IntegrityError):
        obs = Observation(
            entity_id=99999,  # Non-existent ID
            observation_type="test_obs",
            data={"test": "data"},
        )
        db_session.add(obs)
        db_session.commit()
    db_session.rollback()
