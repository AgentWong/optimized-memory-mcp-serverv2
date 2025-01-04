"""
Provider management tools for the MCP server.

This module implements MCP tools for managing infrastructure providers.
Tools provide capabilities for:
- Registering new infrastructure providers with version info
- Managing provider metadata and configuration
- Tracking provider versions and capabilities
- Handling provider-specific settings

Each tool follows standard patterns:
- Database integration through SQLAlchemy sessions
- Proper error handling with ValidationError and DatabaseError
- Consistent return structures with typed dictionaries
- Clean transaction management with commits and rollbacks
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from mcp.server.fastmcp import FastMCP
from ..db.connection import get_db
from ..db.models.providers import Provider
from ..utils.errors import DatabaseError, ValidationError


def register_tools(mcp: FastMCP) -> None:
    """Register provider management tools with the MCP server.

    This function registers all provider-related tools with the MCP server instance.
    Tools include:
    - register_provider: Register new infrastructure providers
    - update_provider: Update existing provider configurations
    - delete_provider: Remove providers from the system

    Each tool is registered with proper type hints, error handling, and database integration.
    Tools follow MCP protocol patterns for consistent behavior and error reporting.

    Provider tools handle:
    - Cloud providers (AWS, Azure, GCP)
    - Container platforms (Kubernetes, Docker)
    - Network infrastructure providers
    - Storage providers
    - Custom provider implementations

    Tool capabilities include:
    - Provider registration with version tracking
    - Configuration management
    - Feature flag control
    - Regional settings
    - Authentication handling
    - Resource quotas and limits
    """

    @mcp.tool()
    def register_provider(
        name: str,
        provider_type: str,
        version: str,
        metadata: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Register a new infrastructure provider.

        Registers a new infrastructure provider with version and configuration details.
        Provider types can include cloud providers (AWS, Azure, GCP), container platforms
        (Kubernetes, Docker), network providers, etc.

        The provider registration includes:
        - Basic provider information (name, type)
        - Version details for compatibility tracking
        - Optional metadata for provider-specific configuration
        - Automatic validation of provider information

        Args:
            name: Provider name (e.g. 'aws', 'azure', 'gcp', 'kubernetes')
            provider_type: Type of provider:
                - 'cloud': Cloud infrastructure providers (AWS, Azure, GCP)
                - 'container': Container orchestration (Kubernetes, Docker)
                - 'network': Network infrastructure providers
                - 'storage': Storage providers (local, S3, etc)
            version: Semantic version string (e.g. '4.0.0')
            metadata: Optional metadata dictionary for provider-specific config:
                     {
                         "region": "us-west-2",          # Provider region
                         "credentials": "path/to/creds", # Auth credentials path
                         "features": ["vpc", "lambda"],  # Enabled features
                         "timeout": 30,                  # Operation timeout
                         "retries": 3                    # Retry attempts
                     }
            db: Database session for persistence

        Returns:
            Dict containing provider details:
            {
                "id": <int>,          # Unique provider ID
                "name": <str>,        # Provider name (e.g. "aws")
                "type": <str>,        # Provider type (e.g. "cloud")
                "version": <str>      # Provider version (e.g. "4.0.0")
            }

        Raises:
            ValidationError: If provider name is empty or invalid
            DatabaseError: If database operation fails

        Example:
            >>> # Register AWS provider with region config
            >>> result = register_provider(
            ...     name="aws",
            ...     provider_type="cloud",
            ...     version="4.0.0",
            ...     metadata={
            ...         "region": "us-west-2",
            ...         "profile": "production",
            ...         "features": ["vpc", "lambda", "rds"]
            ...     }
            ... )
            >>> print(result)
            {
                "id": 1,
                "name": "aws",
                "type": "cloud",
                "version": "4.0.0"
            }

            >>> # Register Kubernetes provider
            >>> result = register_provider(
            ...     name="kubernetes",
            ...     provider_type="container",
            ...     version="1.24",
            ...     metadata={
            ...         "context": "prod-cluster",
            ...         "namespace": "default"
            ...     }
            ... )
        """
        try:
            if not name or not name.strip():
                raise ValidationError("Provider name cannot be empty")

            provider = Provider(
                name=name.strip(),
                type=provider_type.lower(),
                version=version,
                metadata=metadata or {},
            )
            db.add(provider)
            db.commit()
            db.refresh(provider)

            return {
                "id": provider.id,
                "name": provider.name,
                "type": provider.type,
                "version": provider.version,
            }
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"Failed to register provider: {str(e)}")
