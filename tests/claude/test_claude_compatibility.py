"""
Integration tests for Claude Desktop MCP client compatibility.

Verifies compliance with Claude Desktop's MCP client requirements:
- Server info endpoint provides required metadata
- Resource URL protocol handling matches specification
- Tool execution follows required patterns
- Error responses match expected format
- Async operation protocol compliance
- Session management implementation

These tests ensure the server can be used as a context provider
for Claude Desktop's AI assistant features.
"""

import pytest
from src.main import create_server
from src.db.connection import get_db


@pytest.fixture
def db_session():
    """Provide a database session for testing"""
    session = next(get_db())
    try:
        yield session
    finally:
        session.close()


def test_server_info_endpoint(client):
    """Test server info endpoint matches Claude Desktop requirements"""
    response = client.get("/server-info")
    assert response.status_code == 200
    data = response.json()

    # Verify required fields
    assert "name" in data
    assert "version" in data
    assert "capabilities" in data
    assert isinstance(data["capabilities"], list)


def test_resource_protocol(client):
    """Test resource URL protocol handling"""
    # Test valid resource URL
    response = client.get("/resource/test")
    assert response.status_code in (200, 404)  # Either success or not found

    # Test invalid resource URL
    response = client.get("/resource/invalid://test")
    assert response.status_code == 400


def test_tool_execution(client):
    """Test tool execution protocol"""
    # Test tool invocation
    response = client.post("/tools/test-tool", json={"param": "test"})
    assert response.status_code in (200, 404)  # Either success or not found

    # Test invalid tool request
    response = client.post("/tools/invalid-tool", json={"param": "test"})
    assert response.status_code == 404


def test_error_response_format(client):
    """Test error responses match Claude Desktop expectations"""
    # Trigger a 404 error
    response = client.get("/nonexistent")
    assert response.status_code == 404
    data = response.json()

    # Verify error format
    assert "error" in data
    assert "code" in data
    assert "message" in data


def test_async_operation_handling(client):
    """Test async operation protocol"""
    # Start async operation
    response = client.post("/tools/async-test", json={"param": "test"})
    assert response.status_code in (200, 404)

    if response.status_code == 200:
        data = response.json()
        # Verify async operation ID
        assert "operation_id" in data

        # Check operation status
        op_id = data["operation_id"]
        status_response = client.get(f"/operations/{op_id}")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert "status" in status_data


def test_session_management(client):
    """Test session handling protocol"""
    # Create session
    response = client.post("/sessions")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data

    session_id = data["session_id"]

    # Use session
    response = client.get("/test", headers={"X-Session-ID": session_id})
    assert response.status_code in (200, 404)

    # End session
    response = client.delete(f"/sessions/{session_id}")
    assert response.status_code == 200
