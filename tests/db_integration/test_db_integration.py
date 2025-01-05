"""
Integration tests for database operations.

from sqlalchemy.exc import IntegrityError, SQLAlchemyError, InvalidRequestError

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
    entity1 = Entity(name="test_entity_1", entity_type="test")
    entity2 = Entity(name="test_entity_2", entity_type="test")
    db_session.add_all([entity1, entity2])
    db_session.commit()

    # Create relationship
    rel = Relationship(
        source_id=entity1.id,
        target_id=entity2.id,
        type="depends_on",
        relationship_type="test_rel",
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


def test_observation_entity_integrity(db_session):
    """Test observation foreign key constraints"""
    from src.db.models.entities import Entity
    from src.db.models.observations import Observation
    
    # Create entity
    entity = Entity(name="test_entity", entity_type="test")
    db_session.add(entity)
    db_session.commit()

    # Create valid observation
    obs = Observation(
        entity_id=entity.id,
        type="test",
        observation_type="test_obs",
        value={"test": "data"},
        meta_data={}
    )
    db_session.add(obs)
    db_session.commit()

    # Verify constraint with invalid entity_id
    with pytest.raises(IntegrityError):
        invalid_obs = Observation(
            entity_id=99999,  # Non-existent entity
            type="test",
            observation_type="test",
            value={},
            meta_data={}
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
    collection = AnsibleCollection(
        namespace="test", name="test.collection", version="1.0.0"
    )
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


@pytest.mark.asyncio
async def test_concurrent_transactions(mcp_server):
    """Test concurrent database operations"""
    if not hasattr(mcp_server, 'start_async_operation'):
        pytest.skip("Server does not implement start_async_operation")
        
    # Create initial entity through first operation
    operation1 = await mcp_server.start_async_operation(
        "create_entity",
        {"name": "concurrent_test", "entity_type": "test"}
    )
    assert operation1["status"] == "completed", "First operation failed"
    entity_id = operation1["result"]["id"]
    
    # Try concurrent modifications
    operations = []
    for i in range(3):  # Try multiple concurrent updates
        operations.append(
            await mcp_server.start_async_operation(
                "update_entity",
                {"id": entity_id, "name": f"modified_concurrent_{i}"}
            )
        )
    
    # At least one operation should fail with a concurrent modification error
    failed_ops = [op for op in operations if op["status"] == "failed"]
    assert len(failed_ops) > 0, "Expected at least one operation to fail due to concurrency"
    
    # Verify error contains concurrency information
    failed_op = failed_ops[0]
    assert "concurrent modification" in str(failed_op.get("error", "")).lower()


@pytest.mark.asyncio
async def test_database_cleanup(mcp_server, db_session):
    """Verify database cleanup between tests"""
    if not hasattr(mcp_server, 'start_async_operation'):
        pytest.skip("Server does not implement start_async_operation")
        
    # Create test entity
    operation = await mcp_server.start_async_operation(
        "create_entity",
        {"name": "cleanup_test", "entity_type": "test"}
    )
    assert operation["status"] == "completed", "Entity creation failed"
    entity_id = operation["result"]["id"]
    
    # Verify entity exists
    from src.db.models.entities import Entity
    entity = db_session.query(Entity).filter_by(id=entity_id).first()
    assert entity is not None, "Entity should exist"
    
    # Close session and create new one
    db_session.close()
    new_session = next(get_db())
    
    try:
        # Verify entity persists in new session
        entity = new_session.query(Entity).filter_by(id=entity_id).first()
        assert entity is not None, "Entity should persist across sessions"
        
        # Clean up
        if hasattr(mcp_server, 'cleanup'):
            await mcp_server.cleanup()
            
        # Verify cleanup worked
        entity = new_session.query(Entity).filter_by(id=entity_id).first()
        assert entity is None, "Entity should be cleaned up"
    finally:
        new_session.close()
