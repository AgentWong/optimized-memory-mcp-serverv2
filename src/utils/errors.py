"""Error handling utilities for MCP server."""

from datetime import datetime
from typing import Any

# Standard MCP error codes
RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
TOOL_NOT_FOUND = "TOOL_NOT_FOUND" 
INVALID_RESOURCE = "INVALID_RESOURCE"
ENTITY_CREATE_ERROR = "ENTITY_CREATE_ERROR"
DB_CONSTRAINT_ERROR = "DB_CONSTRAINT_ERROR"
DB_TIMEOUT_ERROR = "DB_TIMEOUT_ERROR"
VALIDATION_ERROR = "VALIDATION_ERROR"
CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
INTERNAL_ERROR = "INTERNAL_ERROR"

class MCPError(Exception):
    """Base exception for MCP server errors."""
    def __init__(self, message: str, code: str = INTERNAL_ERROR, details: dict[str, Any] | None = None):
        self.message = message
        self.code = code
        self.details = details or {
            "error": message,
            "context": {
                "timestamp": datetime.utcnow().isoformat()
            }
        }
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
