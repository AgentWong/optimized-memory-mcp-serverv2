"""
Unit tests for MCP tools.

Tests the core MCP tool patterns:
- create_entity - Creates new entities with initial observations
- add_observation - Adds observations to existing entities
- register_provider_resource - Registers new provider resource types
- register_ansible_module - Registers new Ansible modules

Each tool follows the MCP protocol for performing actions and side effects.
"""

import pytest
from src.main import create_server
from src.db.connection import get_db
from src.utils.errors import MCPError


@pytest.fixture
def db_session():
    """Provide a database session for testing"""
    session = next(get_db())
    try:
        yield session
    finally:
        session.close()


def test_create_entity_tool(mcp_server):
    """Test create_entity tool"""
    
    result = mcp_server._tool_manager.call_tool(
        "create_entity",
        {
            "name": "test_entity",
            "entity_type": "test",
            "observations": ["Initial observation"],
        }
    )
    if isinstance(result, type(lambda: None)):
        result = result()
    
    assert isinstance(result, dict), "Result should be a dictionary"
    assert result["name"] == "test_entity", "Entity name mismatch"
    assert isinstance(result["id"], str), "Entity ID should be string"
    assert "created_at" in result, "Missing creation timestamp"
    assert "meta_data" in result, "Missing metadata"


def test_add_observation_tool(mcp_server):
    """Test add_observation tool"""
    # Create entity first
    entity_result = mcp_server.call_tool(
        "create_entity", {"name": "obs_test_entity", "entity_type": "test"}
    )
    entity_id = entity_result["id"]

    # Test add_observation
    obs_result = mcp_server.call_tool(
        "add_observation",
        {
            "entity_id": entity_id,
            "type": "test",
            "observation_type": "test",
            "value": {"test": "data"},
        },
    )
    assert isinstance(obs_result, dict), "Result should be a dictionary"
    assert "id" in obs_result, "Result missing observation ID"
    assert "entity_id" in obs_result, "Result missing entity ID"
    assert "created_at" in obs_result, "Missing creation timestamp"


def test_register_provider_tool(mcp_server):
    """Test register_provider_resource tool"""
    result = mcp_server.call_tool(
        "register_provider_resource",
        {
            "provider": "test_provider",
            "resource_type": "test_resource",
            "schema_version": "1.0",
            "doc_url": "https://example.com/docs",
        },
    )

    assert isinstance(result, dict), "Result should be a dictionary"
    assert "id" in result, "Result missing provider ID"
    assert "provider" in result, "Result missing provider name"
    assert "resource_type" in result, "Result missing resource type"
    assert "schema_version" in result, "Result missing schema version"


def test_register_ansible_module_tool(mcp_server):
    """Test register_ansible_module tool"""
    result = mcp_server.call_tool(
        "register_ansible_module",
        {
            "collection": "test.collection",
            "module": "test_module",
            "version": "1.0.0",
            "doc_url": "https://example.com/docs",
        },
    )

    assert isinstance(result, dict), "Result should be a dictionary"
    assert "id" in result, "Result missing module ID"
    assert "collection" in result, "Result missing collection name"
    assert "module" in result, "Result missing module name"
    assert "version" in result, "Result missing version"


def test_tool_error_handling(mcp_server):
    """Test tool error handling"""
    # Test invalid tool
    with pytest.raises(MCPError) as exc:
        mcp_server.call_tool("invalid_tool", {})
    assert exc.value.code == "TOOL_NOT_FOUND"
    assert "tool not found" in str(exc.value).lower()
    assert exc.value.details is not None

    # Test missing required arguments - comprehensive validation
    with pytest.raises(MCPError) as exc:
        mcp_server.call_tool(
            "create_entity", {"invalid_arg": "value"}  # Missing required args
        )
    error = exc.value
    # Validate error code and message
    assert error.code == "INVALID_ARGUMENTS", "Incorrect error code"
    assert "invalid arguments" in str(error).lower(), "Wrong error message"

    # Validate error details structure
    assert error.details is not None, "Error should include details"
    assert isinstance(error.details, dict), "Details should be a dictionary"

    # Validate missing fields
    assert "missing_fields" in error.details, "Should list missing fields"
    missing_fields = error.details["missing_fields"]
    assert isinstance(missing_fields, list), "Missing fields should be a list"
    assert "name" in missing_fields, "Should specify missing name field"
    assert "entity_type" in missing_fields, "Should specify missing entity_type field"

    # Validate error context
    assert "context" in error.details, "Should include error context"
    assert "timestamp" in error.details["context"], "Should include error timestamp"
    assert "tool" in error.details["context"], "Should specify tool name"
    assert "provided_args" in error.details["context"], "Should list provided arguments"

    # Validate error details structure
    assert error.details is not None, "Error should include details"
    assert isinstance(error.details, dict), "Details should be a dictionary"

    # Validate error reason
    assert "reason" in error.details, "Should specify error reason"
    assert isinstance(error.details["reason"], str), "Reason should be string"
    assert "missing" in error.details["reason"].lower(), "Should indicate missing args"

    # Validate required fields
    assert "required_fields" in error.details, "Should list required fields"
    required_fields = error.details["required_fields"]
    assert isinstance(required_fields, list), "Required fields should be a list"
    assert "name" in required_fields, "Should specify missing name field"
    assert "entity_type" in required_fields, "Should specify missing entity_type field"
    assert len(required_fields) == 2, "Should list exactly required fields"

    # Validate field-specific details
    assert "fields" in error.details, "Should include field-specific details"
    fields = error.details["fields"]
    assert isinstance(fields, dict), "Fields should be a dictionary"
    assert "name" in fields, "Should include name field details"
    assert "entity_type" in fields, "Should include entity_type field details"
    assert fields["name"]["error"] == "missing", "Should specify field is missing"
    assert (
        fields["entity_type"]["error"] == "missing"
    ), "Should specify field is missing"

    # Test validation error - comprehensive field validation
    with pytest.raises(MCPError) as exc:
        mcp_server.call_tool(
            "create_entity", {"name": "a" * 256, "entity_type": "test"}  # Name too long
        )
    error = exc.value
    # Validate error code and message
    assert error.code == "VALIDATION_ERROR", "Incorrect error code"
    assert "validation" in str(error).lower(), "Incorrect error message"

    # Validate error details structure
    assert error.details is not None, "Error should include details"
    assert isinstance(error.details, dict), "Details should be a dictionary"

    # Validate field-specific details
    assert "name" in error.details, "Should specify invalid field"
    field_error = error.details["name"]
    assert isinstance(field_error, dict), "Field error should be a dictionary"

    # Validate length constraints
    assert "length" in field_error, "Should specify validation reason"
    assert "max_length" in field_error, "Should specify length limit"
    assert field_error["max_length"] == 255, "Should specify correct length limit"
    assert "current_length" in field_error, "Should specify current length"
    assert field_error["current_length"] == 256, "Should specify correct current length"

    # Validate error context
    assert "context" in error.details, "Should include error context"
    assert "timestamp" in error.details["context"], "Should include error timestamp"
    assert "field" in error.details["context"], "Should specify affected field"
    assert error.details["context"]["field"] == "name", "Should identify correct field"
    assert (
        "constraint" in error.details["context"]
    ), "Should specify violated constraint"
    assert (
        error.details["context"]["constraint"] == "length"
    ), "Should identify correct constraint"


def test_tool_operation_status(mcp_server):
    """Test operation status handling"""
    # Execute tool
    result = mcp_server.call_tool(
        "create_entity",
        arguments={"name": "status_test", "entity_type": "test"}
    )

    # Verify result structure
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "id" in result, "Result missing ID"
    assert "name" in result, "Result missing name"
    assert "entity_type" in result, "Result missing entity type"
    assert "created_at" in result, "Result missing creation timestamp"
    assert "meta_data" in result, "Result missing metadata"

    # Verify status tracking
    assert "status" in result, "Result missing status"
    assert "started_at" in result, "Result missing start timestamp"
    assert "completed_at" in result, "Result missing completion timestamp"
    assert "operation_id" in result, "Result missing operation ID"
    assert result["status"] == "completed", "Operation should be completed"
    assert result["started_at"] < result["completed_at"], "Invalid operation timing"

    # Verify operation metadata
    assert "tool_name" in result, "Result missing tool name"
    assert result["tool_name"] == "create_entity", "Incorrect tool name"
    assert "arguments" in result, "Result missing arguments"
    assert result["arguments"]["name"] == "status_test", "Arguments not preserved"
    assert "duration_ms" in result, "Result missing duration"
    assert isinstance(result["duration_ms"], (int, float)), "Invalid duration type"
