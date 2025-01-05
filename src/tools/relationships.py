"""
Relationship management tools for the MCP server.

This module implements MCP tools for managing relationships between infrastructure entities.
Tools provide capabilities for:
- Creating new relationships between entities with typed connections
- Updating relationship metadata and properties
- Removing relationships between entities
- Managing relationship lifecycle

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
from ..db.models.relationships import Relationship
from ..db.models.entities import Entity
from ..utils.errors import DatabaseError, ValidationError


def register_tools(mcp: FastMCP) -> list:
    """Register relationship management tools with the MCP server.

    This function registers all relationship-related tools with the MCP server instance.
    Tools include:
    - create_relationship: Create new relationships between entities
    - update_relationship: Modify existing relationship properties
    - delete_relationship: Remove relationships from the system

    Each tool is registered with proper type hints, error handling, and database integration.
    Tools follow MCP protocol patterns for consistent behavior and error reporting.
    """

    @mcp.tool()
    def create_relationship(
        source_id: int,
        target_id: int,
        relationship_type: str,
        metadata: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Create a new relationship between entities.

        Args:
            source_id: ID of the source entity
            target_id: ID of the target entity
            relationship_type: Type of relationship (e.g. 'depends_on', 'contains')
            metadata: Optional metadata dictionary
            db: Database session

        Returns:
            Dict containing relationship id and entity references

        Raises:
            ValidationError: If entities not found
            DatabaseError: If database operation fails

        Example:
            >>> result = create_relationship(
            ...     source_id=1,
            ...     target_id=2,
            ...     relationship_type="depends_on",
            ...     metadata={"priority": "high"}
            ... )
            >>> print(result)
            {
                "id": 1,
                "source_id": 1,
                "target_id": 2,
                "type": "depends_on"
            }
        """
        try:
            # Verify both entities exist
            source = db.query(Entity).filter(Entity.id == source_id).first()
            target = db.query(Entity).filter(Entity.id == target_id).first()

            if not source or not target:
                raise ValidationError("Source or target entity not found")

            relationship = Relationship(
                source_id=source_id,
                target_id=target_id,
                type=relationship_type.lower(),
                metadata=metadata or {},
            )
            db.add(relationship)
            db.commit()
            db.refresh(relationship)

            return {
                "id": relationship.id,
                "source_id": relationship.source_id,
                "target_id": relationship.target_id,
                "type": relationship.type,
            }
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"Failed to create relationship: {str(e)}")

    @mcp.tool()
    def update_relationship(
        relationship_id: int,
        relationship_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update an existing relationship.

        Args:
            relationship_id: ID of relationship to update
            relationship_type: Optional new relationship type
            metadata: Optional metadata to merge with existing
            db: Database session

        Returns:
            Dict containing updated relationship details

        Raises:
            ValidationError: If relationship not found
            DatabaseError: If update fails

        Example:
            >>> result = update_relationship(
            ...     relationship_id=1,
            ...     relationship_type="contains",
            ...     metadata={"updated_by": "user123"}
            ... )
            >>> print(result)
            {
                "id": 1,
                "source_id": 1,
                "target_id": 2,
                "type": "contains",
                "metadata": {
                    "priority": "high",
                    "updated_by": "user123"
                }
            }
        """
        try:
            relationship = (
                db.query(Relationship)
                .filter(Relationship.id == relationship_id)
                .first()
            )

            if not relationship:
                raise DatabaseError(f"Relationship {relationship_id} not found")

            if relationship_type:
                relationship.type = relationship_type.lower()
            if metadata:
                relationship.metadata.update(metadata)

            db.commit()
            db.refresh(relationship)

            return {
                "id": relationship.id,
                "source_id": relationship.source_id,
                "target_id": relationship.target_id,
                "type": relationship.type,
                "metadata": relationship.metadata,
            }
        except Exception as e:
            db.rollback()
            raise DatabaseError(
                f"Failed to update relationship {relationship_id}: {str(e)}"
            )

    @mcp.tool()
    def delete_relationship(relationship_id: int) -> Dict[str, str]:
        """Delete a relationship between entities.

        Args:
            relationship_id: ID of relationship to delete
            db: Database session

        Returns:
            Dict containing success message

        Raises:
            ValidationError: If relationship not found
            DatabaseError: If deletion fails

        Example:
            >>> result = delete_relationship(relationship_id=1)
            >>> print(result)
            {
                "message": "Relationship 1 deleted successfully"
            }
        """
        try:
            relationship = (
                db.query(Relationship)
                .filter(Relationship.id == relationship_id)
                .first()
            )

            if not relationship:
                raise DatabaseError(f"Relationship {relationship_id} not found")

            db.delete(relationship)
            db.commit()

            return {"message": f"Relationship {relationship_id} deleted successfully"}
        except Exception as e:
            db.rollback()
            raise DatabaseError(
                f"Failed to delete relationship {relationship_id}: {str(e)}"
            )
