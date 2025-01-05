"""Error handling utilities for MCP server."""

from datetime import datetime
from typing import Any, Dict, Optional


class MCPError(Exception):
    """Base exception for MCP server errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the base error.

        Args:
            message: Error message
            code: Error code (standardized MCP error codes)
            details: Additional error details
        """
        self.message = message
        self.code = code
        self.details = details or {
            "context": {
                "timestamp": datetime.utcnow().isoformat(),
                "error_type": self.__class__.__name__
            }
        }
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format."""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details
        }


class ConfigurationError(MCPError):
    """Raised when there is a configuration error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize configuration error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message, "CONFIGURATION_ERROR", details)


class ResourceError(MCPError):
    """Raised when there is a resource access error."""

    def __init__(
        self,
        message: str,
        resource_path: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize resource error.

        Args:
            message: Error message
            resource_path: Path of resource that caused error
            details: Additional error details
        """
        error_details = details or {}
        if resource_path:
            error_details["resource_path"] = resource_path
        super().__init__(
            message=message,
            code="RESOURCE_ERROR",
            details=error_details
        )


class ValidationError(MCPError):
    """Raised when there is a validation error."""

    def __init__(
        self, 
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize validation error.

        Args:
            message: Error message
            field: Name of field that failed validation
            details: Additional error details
        """
        error_details = details or {}
        if field:
            error_details["field"] = field
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details=error_details
        )


class DatabaseError(MCPError):
    """Raised when there is a database error."""

    def __init__(
        self, 
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize database error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            details=details
        )
