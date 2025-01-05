"""
Ansible management tools for the MCP server.

This module implements MCP tools for managing Ansible collections and their versions.
Tools provide capabilities for:
- Registering new Ansible collections with namespace and version
- Adding new versions to existing collections
- Managing collection metadata

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
from ..db.models.ansible import AnsibleCollection
from ..utils.errors import DatabaseError, ValidationError


async def register_tools(mcp: FastMCP) -> list:
    """Register Ansible management tools with the MCP server.

    This function registers all Ansible-related tools with the MCP server instance.
    Tools include:
    - register_collection: Register new Ansible collections
    - add_version: Add new versions to existing collections
    - update_metadata: Update collection metadata

    Each tool is registered with proper type hints, error handling, and database integration.
    Tools follow MCP protocol patterns for consistent behavior and error reporting.

    Ansible tools handle:
    - Collection registration and versioning
    - Module documentation and schemas
    - Role definitions and requirements
    - Playbook validation patterns
    - Galaxy integration support

    Tool capabilities include:
    - Collection lifecycle management
    - Version compatibility tracking
    - Dependency resolution
    - Documentation generation
    - Schema validation
    """

    @mcp.tool()
    @mcp.tool()
    def register_collection(
        namespace: str,
        name: str,
        version: str,
        metadata: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Register a new Ansible collection.

        Args:
            namespace: Collection namespace (e.g. 'community', 'ansible')
            name: Collection name
            version: Semantic version string
            metadata: Optional metadata dictionary
            db: Database session

        Returns:
            Dict containing collection id, namespace, name and version

        Raises:
            ValidationError: If collection name is empty
            DatabaseError: If database operation fails
        """
        try:
            if not name or not name.strip():
                raise ValidationError("Collection name cannot be empty")

            collection = AnsibleCollection(
                namespace=namespace.strip(),
                name=name.strip(),
                version=version,
                metadata=metadata or {},
            )
            with get_db() as db:
                db.add(collection)
                db.commit()
                db.refresh(collection)

            return {
                "id": collection.id,
                "namespace": collection.namespace,
                "name": collection.name,
                "version": collection.version,
            }
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"Failed to register collection: {str(e)}")

    @mcp.tool()
    @mcp.tool()
    def add_version(
        collection_name: str,
        version: str,
        metadata: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Add a new version for an existing Ansible collection.

        Args:
            collection_name: Name of existing collection
            version: New semantic version string
            metadata: Optional metadata dictionary
            db: Database session

        Returns:
            Dict containing collection id, namespace, name and version

        Raises:
            ValidationError: If collection does not exist
            DatabaseError: If database operation fails
        """
        try:
            # Get existing collection to copy namespace
            existing = (
                db.query(AnsibleCollection)
                .filter(AnsibleCollection.name == collection_name)
                .first()
            )

            if not existing:
                raise ValidationError(f"Collection {collection_name} not found")

            collection = AnsibleCollection(
                namespace=existing.namespace,
                name=collection_name,
                version=version,
                metadata=metadata or {},
            )
            db.add(collection)
            db.commit()
            db.refresh(collection)

            return {
                "id": collection.id,
                "namespace": collection.namespace,
                "name": collection.name,
                "version": collection.version,
            }
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"Failed to add version: {str(e)}")
