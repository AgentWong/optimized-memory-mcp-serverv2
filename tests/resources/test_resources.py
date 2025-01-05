"""
Unit tests for MCP resources.

from src.utils.errors import MCPError, ValidationError

Tests the core MCP resource patterns:
- entities://list - Lists all entities in the system
- entities://{id} - Gets details for a specific entity
- providers://{provider}/resources - Lists resources for a provider
- ansible://collections - Lists registered Ansible collections

Each resource follows the MCP protocol for read-only data access.
"""

import pytest

from src.main import create_server
from src.db.connection import get_db
from src.db.models.base import Base


@pytest.fixture
def client():
    """Create test client"""
    server = create_server()
    return server


@pytest.fixture
def db_session():
    """Provide a database session for testing"""
    session = next(get_db())
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(bind=session.bind)
        Base.metadata.create_all(bind=session.bind)


def test_entities_list_resource(mcp_server):
    """Test entities://list resource using FastMCP"""
    result = mcp_server.read_resource("entities://list")
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "data" in result, "Result missing 'data' field"
    assert isinstance(result["data"], list), "Data should be a list"
    assert "resource_path" in result, "Result missing 'resource_path'"
    assert "timestamp" in result, "Result missing 'timestamp'"


def test_entity_detail_resource(mcp_server, db_session):
    """Test entities://{id} resource"""
    if not hasattr(mcp_server, "read_resource"):
        pytest.skip("Server does not implement read_resource")

    # Create test entity first
    result = mcp_server.call_tool(
        "create_entity", {"name": "test_entity", "entity_type": "test"}
    )
    entity_id = result["id"]
    assert entity_id, "No entity ID returned"

    # Test resource
    result = mcp_server.read_resource(f"entities://{entity_id}")
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "data" in result, "Result missing 'data' field"
    assert result["data"]["name"] == "test_entity", "Entity name mismatch"
    assert result["data"]["id"] == entity_id, "Entity ID mismatch"


def test_providers_resource(mcp_server):
    """Test providers://{provider}/resources resource"""
    if not hasattr(mcp_server, "read_resource"):
        pytest.skip("Server does not implement read_resource")

    result = mcp_server.get_resource("providers://test/resources", version="latest")
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "data" in result, "Result missing 'data' field"
    assert isinstance(result["data"], list), "Provider resources should be a list"


def test_ansible_collections_resource(mcp_server):
    """Test ansible://collections resource"""
    if not hasattr(mcp_server, "read_resource"):
        pytest.skip("Server does not implement read_resource")

    result = mcp_server.read_resource("ansible://collections")
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "data" in result, "Result missing 'data' field"
    assert isinstance(result["data"], list), "Collections should be a list"


def test_resource_error_handling(mcp_server):
    """Test resource error handling"""
    if not hasattr(mcp_server, "read_resource"):
        pytest.skip("Server does not implement read_resource")

    # Test invalid resource path - comprehensive validation
    with pytest.raises(MCPError) as exc:
        mcp_server.read_resource("invalid://resource")
    error = exc.value

    # Additional validation of error structure
    assert hasattr(error, "code"), "Error should have code attribute"
    assert hasattr(error, "details"), "Error should have details attribute"
    assert isinstance(error.details, dict), "Error details should be dictionary"
    # Validate error code and message
    assert error.code in [
        "RESOURCE_NOT_FOUND",
        "INVALID_RESOURCE",
    ], "Incorrect error code"
    assert "not found" in str(error).lower(), "Wrong error message"

    # Validate error details structure
    assert error.details is not None, "Error should include details"
    assert isinstance(error.details, dict), "Details should be a dictionary"

    # Validate error context
    assert "context" in error.details, "Should include error context"
    assert "timestamp" in error.details["context"], "Should include error timestamp"
    assert "resource_path" in error.details["context"], "Should specify resource path"
    assert "request_id" in error.details["context"], "Should include request ID"

    # Test invalid parameters - comprehensive validation
    with pytest.raises(MCPError) as exc:
        mcp_server.read_resource("entities://list", {"invalid_param": "value"})
    error = exc.value
    # Validate error code and message
    assert error.code == "INVALID_PARAMETERS", "Incorrect error code"
    assert "invalid" in str(error).lower(), "Wrong error message"

    # Validate error details structure
    assert error.details is not None, "Error should include details"
    assert isinstance(error.details, dict), "Details should be a dictionary"

    # Validate invalid parameters
    assert "invalid_parameters" in error.details, "Should list invalid parameters"
    invalid_params = error.details["invalid_parameters"]
    assert isinstance(invalid_params, list), "Invalid parameters should be a list"
    assert "invalid_param" in invalid_params, "Should specify invalid parameter"

    # Validate allowed parameters
    assert "allowed_parameters" in error.details, "Should list allowed parameters"
    assert isinstance(
        error.details["allowed_parameters"], list
    ), "Allowed parameters should be a list"

    # Validate error context
    assert "context" in error.details, "Should include error context"
    assert "timestamp" in error.details["context"], "Should include error timestamp"
    assert "resource_path" in error.details["context"], "Should specify resource path"
    assert (
        "provided_params" in error.details["context"]
    ), "Should list provided parameters"


def test_resource_pagination(mcp_server):
    """Test resource pagination"""
    if not hasattr(mcp_server, "read_resource"):
        pytest.skip("Server does not implement read_resource")

    # Create multiple test entities
    for i in range(5):
        mcp_server.call_tool(
            "create_entity", 
            {"name": f"test_entity_{i}", "entity_type": "test"}
        )

    # Test pagination using query string
    result = mcp_server.read_resource("entities://list?page=1&per_page=2")
    assert isinstance(result, dict)
    assert isinstance(result.get("data"), list)
    assert len(result.get("data", [])) <= 2, "Page size exceeded"
    assert "total" in result, "Missing total count"
    assert "pages" in result, "Missing total pages"

    # Verify next page
    if len(result.get("data", [])) == 2:
        next_page = mcp_server.read_resource("entities://list", params={
            "page": 2,
            "per_page": 2
        })
        assert isinstance(next_page, dict)
        assert isinstance(next_page.get("data"), list)
        assert next_page.get("data") != result.get("data"), "Pages should be different"
        assert len(next_page.get("data", [])) <= 2, "Page size exceeded"
