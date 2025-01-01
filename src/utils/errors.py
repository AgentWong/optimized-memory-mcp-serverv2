"""
Error handling utilities for MCP server.
"""
from typing import Any, Dict, Optional

class MCPError(Exception):
    """Base exception for MCP server errors."""
    
    def __init__(
        self,
        message: str,
        code: str = 'INTERNAL_ERROR',
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

class ConfigurationError(MCPError):
    """Raised when there is a configuration error."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, 'CONFIGURATION_ERROR', details)

class DatabaseError(MCPError):
    """Raised when there is a database error."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, 'DATABASE_ERROR', details)

class ValidationError(MCPError):
    """Raised when there is a validation error."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, 'VALIDATION_ERROR', details)
