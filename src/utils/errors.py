"""Error handling utilities for MCP server."""

from datetime import datetime
from typing import Any

# Standard MCP error codes
RESOURCE_NOT_FOUND = "resource_not_found"
TOOL_NOT_FOUND = "tool_not_found"
INVALID_RESOURCE = "invalid_resource" 
INVALID_ARGUMENTS = "invalid_arguments"
ENTITY_CREATE_ERROR = "entity_create_error"
DB_CONSTRAINT_ERROR = "db_constraint_error"
DB_TIMEOUT_ERROR = "db_timeout_error"
VALIDATION_ERROR = "validation_error"
CONFIGURATION_ERROR = "configuration_error"
INTERNAL_ERROR = "internal_error"
CONCURRENT_MODIFICATION = "concurrent_modification"

class MCPError(Exception):
    """Base exception for MCP server errors."""
    def __init__(self, message: str, code: str = INTERNAL_ERROR, details: dict[str, Any] | None = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

class ResourceError(MCPError):
    """Raised when there is a resource access error."""
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, RESOURCE_NOT_FOUND, details)

class ValidationError(MCPError):
    """Raised when there is a validation error."""
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, VALIDATION_ERROR, details)

class DatabaseError(MCPError):
    """Raised when there is a database error."""
    def __init__(self, message: str, code: str = DB_CONSTRAINT_ERROR, details: dict[str, Any] | None = None):
        super().__init__(message, code, details)

class ToolError(MCPError):
    """Raised when there is a tool execution error."""
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, TOOL_NOT_FOUND, details)

class ConfigurationError(MCPError):
    """Raised when there is a configuration error."""
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, CONFIGURATION_ERROR, details)

class InvalidResourceError(MCPError):
    """Raised when a resource request is invalid."""
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, INVALID_RESOURCE, details)

class EntityError(MCPError):
    """Raised when there is an entity creation/update error."""
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, ENTITY_CREATE_ERROR, details)
