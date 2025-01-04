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
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.main import create_server
from src.db.connection import get_db
from src.db.models.entities import Entity
from src.db.models.relationships import Relationship
from src.db.models.observations import Observation
from src.utils.errors import MCPError, ValidationError, DatabaseError


@pytest.fixture
def mcp_server():
    """Create MCP server instance"""
    return create_server()


@pytest.fixture
def db_session():
    """Provide a database session for testing"""
    session = next(get_db())
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.mark.asyncio
async def test_database_constraint_violations(mcp_server, db_session: Session):
    """Test database constraint violation handling"""
    # Test duplicate entity name
    result = await mcp_server.call_tool(
        "create_entity", arguments={"name": "unique_entity", "entity_type": "test"}
    )
    assert result is not None

    # Attempt duplicate
    with pytest.raises(ValidationError) as exc:
        await mcp_server.call_tool(
            "create_entity", arguments={"name": "unique_entity", "entity_type": "test"}
        )
    assert "already exists" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_invalid_relationship_creation(mcp_server, db_session: Session):
    """Test invalid relationship handling"""
    # Create test entity
    result = await mcp_server.call_tool(
        "create_entity", arguments={"name": "test_entity", "entity_type": "test"}
    )
    entity_id = result["id"]

    # Test self-referential relationship
    with pytest.raises(ValidationError) as exc:
        mcp_server.call_tool(
            "create_relationship",
            arguments={
                "source_id": entity_id,
                "target_id": entity_id,
                "relationship_type": "self_ref",
            },
        )
    assert "self-referential" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_invalid_observation_data(mcp_server, db_session: Session):
    """Test invalid observation data handling"""
    # Create test entity
    result = await mcp_server.call_tool(
        "create_entity", arguments={"name": "obs_test_entity", "entity_type": "test"}
    )
    entity_id = result["id"]

    # Test invalid observation data
    with pytest.raises(ValidationError) as exc:
        await mcp_server.call_tool(
            "add_observation",
            arguments={
                "entity_id": entity_id,
                "observation_type": "test",
                "data": None,  # Invalid data
            },
        )
    assert "invalid data" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_concurrent_modification_conflicts(mcp_server, db_session: Session):
    """Test concurrent modification handling"""
    # Create test entity
    result = await mcp_server.call_tool(
        "create_entity", arguments={"name": "concurrent_test", "entity_type": "test"}
    )
    entity_id = result["id"]

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
        with pytest.raises(DatabaseError) as exc:
            session2.commit()
        assert "concurrent modification" in str(exc.value).lower()
    finally:
        session2.rollback()
        session2.close()


@pytest.mark.asyncio
async def test_invalid_tool_requests(mcp_server):
    """Test invalid tool request handling"""
    # Test invalid arguments
    with pytest.raises(ValidationError) as exc:
        await mcp_server.call_tool(
            "create_entity",
            arguments={"invalid": "data"}
        )
    assert "invalid arguments" in str(exc.value).lower()

    # Test missing required fields
    with pytest.raises(ValidationError) as exc:
        await mcp_server.call_tool(
            "create_entity",
            arguments={"name": "test"}  # Missing entity_type
        )
    assert "required field" in str(exc.value).lower()


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
        "/entities/", json={"name": "test", "entity_type": "invalid_type"}
    )
    assert response.status_code == 400
    assert "invalid type" in response.json()["message"].lower()

    # Test invalid relationship type
    response = client.post(
        "/relationships/",
        json={"source_id": 1, "target_id": 2, "relationship_type": "invalid_type"},
    )
    assert response.status_code == 400
    assert "invalid type" in response.json()["message"].lower()


def test_transaction_rollback(client, db_session: Session):
    """Test transaction rollback on errors"""
    # Create test entity
    entity_response = client.post(
        "/entities/", json={"name": "rollback_test", "entity_type": "test"}
    )
    entity_id = entity_response.json()["id"]

    # Attempt invalid operation that should trigger rollback
    try:
        # Start transaction
        entity = db_session.query(Entity).get(entity_id)
        entity.name = "updated_name"

        # Perform invalid operation
        invalid_obs = Observation(
            entity_id=99999, observation_type="test", data={}  # Non-existent entity
        )
        db_session.add(invalid_obs)
        db_session.commit()
    except:
        db_session.rollback()

    # Verify original state maintained
    entity = db_session.query(Entity).get(entity_id)
    assert entity.name == "rollback_test"
