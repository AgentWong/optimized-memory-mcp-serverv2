"""
Unit tests for error handling utilities.

Tests the core error handling patterns required by MCP:
- Base MCPError functionality and inheritance
- Configuration error handling
- Database error handling 
- Validation error handling
- Error message formatting and details

Each test verifies proper error construction and handling
per MCP protocol requirements.
"""
import pytest
from src.utils.errors import MCPError, ConfigurationError, DatabaseError, ValidationError

def test_base_error():
    """Test base MCPError functionality"""
    error = MCPError("test message", "TEST_CODE", {"detail": "test"})
    assert error.message == "test message"
    assert error.code == "TEST_CODE"
    assert error.details == {"detail": "test"}
    
    # Test default values
    error = MCPError("test message")
    assert error.code == "INTERNAL_ERROR"
    assert error.details == {}

def test_configuration_error():
    """Test ConfigurationError class"""
    error = ConfigurationError("config error", {"param": "invalid"})
    assert error.message == "config error"
    assert error.code == "CONFIGURATION_ERROR"
    assert error.details == {"param": "invalid"}
    
    # Test without details
    error = ConfigurationError("config error")
    assert error.details == {}

def test_database_error():
    """Test DatabaseError class"""
    error = DatabaseError("db error", {"table": "users"})
    assert error.message == "db error"
    assert error.code == "DATABASE_ERROR"
    assert error.details == {"table": "users"}
    
    # Test without details
    error = DatabaseError("db error")
    assert error.details == {}

def test_validation_error():
    """Test ValidationError class"""
    error = ValidationError("invalid input", {"field": "name"})
    assert error.message == "invalid input"
    assert error.code == "VALIDATION_ERROR"
    assert error.details == {"field": "name"}
    
    # Test without details
    error = ValidationError("invalid input")
    assert error.details == {}

def test_error_inheritance():
    """Test error class inheritance"""
    config_error = ConfigurationError("test")
    db_error = DatabaseError("test")
    validation_error = ValidationError("test")
    
    assert isinstance(config_error, MCPError)
    assert isinstance(db_error, MCPError)
    assert isinstance(validation_error, MCPError)

def test_error_str_representation():
    """Test string representation of errors"""
    error = MCPError("test message")
    assert str(error) == "test message"
