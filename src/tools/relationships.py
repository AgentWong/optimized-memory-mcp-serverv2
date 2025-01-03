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

def register_tools(mcp: FastMCP) -> None:
    """Register relationship management tools with the MCP server."""

    @mcp.tool()
    def create_relationship(
        source_id: int,
        target_id: int,
        relationship_type: str,
        metadata: Dict[str, Any] = None,
        db: Session = next(get_db())
    ) -> Dict[str, Any]:
        """Create a new relationship between entities."""
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
                metadata=metadata or {}
            )
            db.add(relationship)
            db.commit()
            db.refresh(relationship)
            
            return {
                "id": relationship.id,
                "source_id": relationship.source_id,
                "target_id": relationship.target_id,
                "type": relationship.type
            }
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"Failed to create relationship: {str(e)}")

    @mcp.tool()
    def update_relationship(
        relationship_id: int,
        relationship_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        db: Session = next(get_db())
    ) -> Dict[str, Any]:
        """Update an existing relationship."""
        try:
            relationship = db.query(Relationship).filter(
                Relationship.id == relationship_id
            ).first()
            
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
                "metadata": relationship.metadata
            }
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"Failed to update relationship {relationship_id}: {str(e)}")

    @mcp.tool()
    def delete_relationship(
        relationship_id: int,
        db: Session = next(get_db())
    ) -> Dict[str, str]:
        """Delete a relationship."""
        try:
            relationship = db.query(Relationship).filter(
                Relationship.id == relationship_id
            ).first()
            
            if not relationship:
                raise DatabaseError(f"Relationship {relationship_id} not found")
                
            db.delete(relationship)
            db.commit()
            
            return {"message": f"Relationship {relationship_id} deleted successfully"}
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"Failed to delete relationship {relationship_id}: {str(e)}")
