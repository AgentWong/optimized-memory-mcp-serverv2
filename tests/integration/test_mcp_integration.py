"""
End-to-end integration tests for MCP functionality.

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
from sqlalchemy.orm import Session

from src.main import create_server
from src.db.connection import get_db
from src.db.models.entities import Entity
from src.db.models.relationships import Relationship
from src.db.models.observations import Observation


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
        session.close()


def test_full_entity_workflow(mcp_server, db_session: Session):
    """Test complete entity lifecycle including relationships and observations"""
    # Create initial entity
    entity1_result = mcp_server.call_tool(
        "create_entity", arguments={"name": "test_entity_1", "entity_type": "test_type"}
    )
    assert entity1_result is not None
    entity1_id = entity1_result["id"]

    # Create related entity
    entity2_result = mcp_server.call_tool(
        "create_entity", arguments={"name": "test_entity_2", "entity_type": "test_type"}
    )
    assert entity2_result is not None
    entity2_id = entity2_result["id"]

    # Create relationship between entities
    rel_result = mcp_server.call_tool(
        "create_relationship",
        arguments={
            "source_id": entity1_id,
            "target_id": entity2_id,
            "relationship_type": "test_relationship",
        },
    )
    assert rel_result is not None

    # Add observation to first entity
    obs_result = mcp_server.call_tool(
        "add_observation",
        arguments={
            "entity_id": entity1_id,
            "observation_type": "test_observation",
            "data": {"test": "data"},
        },
    )
    assert obs_result is not None

    # Get related entities
    related_result = mcp_server.read_resource(
        f"entities://{entity1_id}/related?max_depth=1"
    )
    assert related_result is not None
    assert any(e["id"] == entity2_id for e in related_result)


def test_search_and_analysis_workflow(mcp_server, db_session: Session):
    """Test search functionality with analysis tools"""
    # Create test entity
    entity_result = mcp_server.call_tool(
        "create_entity",
        arguments={"name": "searchable_entity", "entity_type": "test_type"},
    )
    assert entity_result is not None

    # Search for entity
    search_result = mcp_server.call_tool(
        "search_entities", arguments={"query": "searchable"}
    )
    assert search_result is not None
    assert len(search_result) > 0
    assert any(e["name"] == "searchable_entity" for e in search_result)


def test_error_handling(mcp_server):
    """Test MCP error handling"""
    # Test invalid entity ID
    with pytest.raises(Exception):
        mcp_server.read_resource("entities://99999")

    # Test invalid relationship creation
    with pytest.raises(Exception):
        mcp_server.call_tool(
            "create_relationship",
            arguments={
                "source_id": 99999,
                "target_id": 99999,
                "relationship_type": "test",
            },
        )

    # Test invalid observation creation
    with pytest.raises(Exception):
        mcp_server.call_tool(
            "add_observation",
            arguments={"entity_id": 99999, "observation_type": "test", "data": {}},
        )
