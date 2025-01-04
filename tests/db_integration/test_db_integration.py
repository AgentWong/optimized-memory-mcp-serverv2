"""
Integration tests for database operations.

Tests the core database integration patterns required by MCP:
- Entity relationship cascade behavior
- Observation foreign key constraints
- Provider version management
- Ansible collection relationships
- Concurrent transaction handling

Each test verifies proper database integration and data integrity
across the MCP server implementation.
"""

import pytest
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.db.models.entities import Entity
from src.db.models.relationships import Relationship
from src.db.models.observations import Observation
from src.db.models.providers import Provider
from src.db.models.ansible import AnsibleCollection
from src.main import create_server


@pytest.fixture
def db_session():
    """Provide a database session for testing"""
    session = next(get_db())
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def mcp_server():
    """Create MCP server instance"""
    return create_server()


def test_entity_relationships_cascade(db_session: Session):
    """Test entity deletion cascades relationships properly"""
    # Create test entities
    entity1 = Entity(name="test_entity_1", type="test")
    entity2 = Entity(name="test_entity_2", type="test")
    db_session.add_all([entity1, entity2])
    db_session.commit()

    # Create relationship
    rel = Relationship(
        source_id=entity1.id, target_id=entity2.id, relationship_type="test_rel"
    )
    db_session.add(rel)
    db_session.commit()

    # Delete entity and verify cascade
    db_session.delete(entity1)
    db_session.commit()

    # Check relationship was deleted
    assert (
        db_session.query(Relationship).filter_by(source_id=entity1.id).first() is None
    )


def test_observation_entity_integrity(db_session: Session):
    """Test observation foreign key constraints"""
    # Create entity
    entity = Entity(name="test_entity", entity_type="test")
    db_session.add(entity)
    db_session.commit()

    # Create observation
    obs = Observation(
        entity_id=entity.id, observation_type="test_obs", data={"test": "data"}
    )
    db_session.add(obs)
    db_session.commit()

    # Verify constraint
    with pytest.raises(Exception):
        invalid_obs = Observation(
            entity_id=99999, observation_type="test", data={}  # Non-existent entity
        )
        db_session.add(invalid_obs)
        db_session.commit()


def test_provider_version_tracking(db_session: Session):
    """Test provider version management"""
    # Create provider
    provider = Provider(
        name="test_provider", namespace="test", type="test_type", version="1.0.0"
    )
    db_session.add(provider)
    db_session.commit()

    # Update version
    provider.version = "1.0.1"
    db_session.commit()

    # Verify version history
    updated = db_session.query(Provider).filter_by(id=provider.id).first()
    assert updated.version == "1.0.1"


def test_ansible_collection_relationships(db_session: Session):
    """Test ansible collection relationship handling"""
    # Create collection
    collection = AnsibleCollection(namespace="test", name="test.collection", version="1.0.0")
    db_session.add(collection)
    db_session.commit()

    # Create related entity
    entity = Entity(name="test_module", entity_type="ansible_module")
    db_session.add(entity)
    db_session.commit()

    # Create relationship
    rel = Relationship(
        source_id=collection.id,
        target_id=entity.id,
        relationship_type="contains_module",
    )
    db_session.add(rel)
    db_session.commit()

    # Verify relationship
    assert (
        db_session.query(Relationship)
        .filter_by(source_id=collection.id, target_id=entity.id)
        .first()
        is not None
    )


def test_concurrent_transactions(db_session: Session):
    """Test concurrent database operations"""
    # Create initial entity
    entity = Entity(name="concurrent_test", entity_type="test")
    db_session.add(entity)
    db_session.commit()

    # Start another session
    session2 = next(get_db())
    try:
        # Modify in first session
        entity.name = "modified_in_session1"

        # Try to modify in second session
        entity2 = session2.query(Entity).filter_by(id=entity.id).first()
        entity2.name = "modified_in_session2"

        # Commit first session
        db_session.commit()

        # Second session should fail
        with pytest.raises(Exception):
            session2.commit()
    finally:
        session2.rollback()
        session2.close()


def test_database_cleanup(db_session: Session):
    """Verify database cleanup between tests"""
    # Create test data
    entity = Entity(name="cleanup_test", entity_type="test")
    db_session.add(entity)
    db_session.commit()

    # Get entity ID
    entity_id = entity.id

    # Close session
    db_session.close()

    # Create new session
    new_session = next(get_db())
    try:
        # Verify entity doesn't exist in new session
        assert new_session.query(Entity).filter_by(id=entity_id).first() is None
    finally:
        new_session.close()
