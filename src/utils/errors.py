"""Error handling utilities for MCP server."""

from datetime import datetime
from typing import Any

class MCPError(Exception):
    """Base exception for MCP server errors."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", details: dict[str, Any] | None = None):
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
        super().__init__(message, "RESOURCE_NOT_FOUND", details)


class ValidationError(MCPError):
    """Raised when there is a validation error."""
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class DatabaseError(MCPError):
    """Raised when there is a database error."""
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, "DATABASE_ERROR", details)


class ToolError(MCPError):
    """Raised when there is a tool execution error."""
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, "TOOL_NOT_FOUND", details)
