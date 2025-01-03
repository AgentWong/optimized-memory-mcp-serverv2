"""
Entity management tools for the MCP server.
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from mcp.server.fastmcp import FastMCP
from ..db.connection import get_db
from ..db.models.entities import Entity
from ..utils.errors import DatabaseError, ValidationError

def register_tools(mcp: FastMCP) -> None:
    """Register entity management tools with the MCP server."""

    @mcp.tool()
    def create_entity(
        name: str,
        entity_type: str,
        metadata: Dict[str, Any] = None,
        db: Session = next(get_db())
    ) -> Dict[str, Any]:
        """Create a new entity."""
        try:
            if not name or not name.strip():
                raise ValidationError("Entity name cannot be empty")
                
            entity = Entity(
                name=name.strip(),
                type=entity_type.lower(),
                metadata=metadata or {}
            )
            db.add(entity)
            db.commit()
            db.refresh(entity)
            
            return {
                "id": entity.id,
                "name": entity.name,
                "type": entity.type
            }
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"Failed to create entity: {str(e)}")

    @mcp.tool()
    def update_entity(
        entity_id: int,
        name: str = None,
        metadata: Dict[str, Any] = None,
        db: Session = next(get_db())
    ) -> Dict[str, Any]:
        """Update an existing entity."""
        try:
            entity = db.query(Entity).filter(Entity.id == entity_id).first()
            if not entity:
                raise DatabaseError(f"Entity {entity_id} not found")
                
            if name:
                entity.name = name.strip()
            if metadata:
                entity.metadata.update(metadata)
                
            db.commit()
            db.refresh(entity)
            
            return {
                "id": entity.id,
                "name": entity.name,
                "type": entity.type,
                "metadata": entity.metadata
            }
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"Failed to update entity {entity_id}: {str(e)}")

    @mcp.tool()
    def delete_entity(
        entity_id: int,
        db: Session = next(get_db())
    ) -> Dict[str, str]:
        """Delete an entity."""
        try:
            entity = db.query(Entity).filter(Entity.id == entity_id).first()
            if not entity:
                raise DatabaseError(f"Entity {entity_id} not found")
                
            db.delete(entity)
            db.commit()
            
            return {"message": f"Entity {entity_id} deleted successfully"}
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"Failed to delete entity {entity_id}: {str(e)}")
