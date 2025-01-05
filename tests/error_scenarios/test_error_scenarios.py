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
    session = get_db()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def test_database_constraint_violations(mcp_server, db_session: Session):
    """Test database constraint violation handling"""
    # Test duplicate entity name
    result = mcp_server.call_tool(
        "create_entity", {"name": "unique_entity", "entity_type": "test"}
    )
    assert result is not None
    assert "id" in result, "Result missing entity ID"
    assert result["name"] == "unique_entity"

    # Attempt duplicate
    with pytest.raises(ValidationError) as exc:
        mcp_server.call_tool(
            "create_entity", arguments={"name": "unique_entity", "entity_type": "test"}
        )
    assert exc.value.code == "VALIDATION_ERROR"
    assert "already exists" in str(exc.value).lower()
    assert "name" in exc.value.details, "Error details should specify field"


def test_invalid_relationship_creation(mcp_server, db_session: Session):
    """Test invalid relationship handling"""
    # Create test entity
    result = mcp_server.call_tool(
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


def test_invalid_observation_data(mcp_server, db_session: Session):
    """Test invalid observation data handling"""
    # Create test entity
    result = mcp_server.call_tool(
        "create_entity", arguments={"name": "obs_test_entity", "entity_type": "test"}
    )
    entity_id = result["id"]

    # Test invalid observation data
    with pytest.raises(ValidationError) as exc:
        mcp_server.call_tool(
            "add_observation",
            arguments={
                "entity_id": entity_id,
                "observation_type": "test",
                "data": None,  # Invalid data
            },
        )
    assert "invalid data" in str(exc.value).lower()


def test_concurrent_modification_conflicts(mcp_server, db_session: Session):
    """Test concurrent modification handling"""
    # Create test entity
    result = mcp_server.call_tool(
        "create_entity", arguments={"name": "concurrent_test", "entity_type": "test"}
    )
    entity_id = result["id"]

    # Simulate concurrent modifications
    session2 = get_db()
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


def test_invalid_tool_requests(mcp_server):
    """Test invalid tool request handling"""
    # Test invalid tool name
    with pytest.raises(MCPError) as exc:
        mcp_server.call_tool("nonexistent_tool", {})
    assert exc.value.code == "TOOL_NOT_FOUND"
    assert "tool not found" in str(exc.value).lower()

    # Test missing required arguments
    with pytest.raises(MCPError) as exc:
        mcp_server.call_tool("create_entity", {"invalid": "data"})
    assert exc.value.code == "INVALID_ARGUMENTS"
    assert "missing required argument" in str(exc.value).lower()

    # Test malformed arguments
    with pytest.raises(MCPError) as exc:
        mcp_server.call_tool(
            "create_entity", "not_a_dict"  # Invalid argument type
        )
    assert exc.value.code == "INVALID_ARGUMENTS"
    assert "invalid argument type" in str(exc.value).lower()

    # Test invalid argument values
    with pytest.raises(MCPError) as exc:
        mcp_server.call_tool(
            "create_entity", {"name": "", "entity_type": "test"}  # Empty name
        )
    assert exc.value.code == "VALIDATION_ERROR"
    assert "invalid name" in str(exc.value).lower()

    # Test argument type validation
    with pytest.raises(MCPError) as exc:
        mcp_server.call_tool(
            "create_entity",
            {"name": 123, "entity_type": "test"},  # Name should be string
        )
    assert exc.value.code == "VALIDATION_ERROR"
    assert "invalid argument type" in str(exc.value).lower()


def test_resource_not_found_handling(mcp_server):
    """Test resource not found error handling"""
    if not hasattr(mcp_server, "read_resource"):
        pytest.skip("Server does not implement read_resource")

    with pytest.raises(MCPError) as exc:
        mcp_server.read_resource("nonexistent://resource")
    assert "not found" in str(exc.value).lower()


def test_transaction_rollback(mcp_server, db_session):
    """Test transaction rollback on errors"""
    # Create initial entity
    result = mcp_server.call_tool(
        "create_entity", {"name": "rollback_test", "entity_type": "test"}
    )
    entity_id = result["id"]

    # Attempt invalid operation that should trigger rollback
    try:
        mcp_server.call_tool(
            "add_observation",
            {
                "entity_id": entity_id,
                "type": "test",
                "value": {"data": "x" * 1000000},  # Too large
            }
        )
    except ValidationError:
        pass

    # Verify database state rolled back
    from src.db.models.observations import Observation

    observations = db_session.query(Observation).filter_by(entity_id=entity_id).all()
    assert len(observations) == 0, "Transaction should have rolled back"
