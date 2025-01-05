"""Error handling utilities for MCP server."""

class MCPError(Exception):
    """Base exception for MCP server errors."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class ConfigurationError(MCPError):
    """Raised when there is a configuration error."""
    def __init__(self, message: str):
        super().__init__(message, "CONFIGURATION_ERROR")


class ResourceError(MCPError):
    """Raised when there is a resource access error."""
    def __init__(self, message: str):
        super().__init__(message, "RESOURCE_ERROR")


class ValidationError(MCPError):
    """Raised when there is a validation error."""
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class DatabaseError(MCPError):
    """Raised when there is a database error."""
    def __init__(self, message: str):
        super().__init__(message, "DATABASE_ERROR")
