"""
Entity-related resources for the MCP server.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from mcp.server.fastmcp import FastMCP
from ..db.connection import get_db
from ..db.models.entities import Entity
from ..utils.errors import DatabaseError

def register_resources(mcp: FastMCP) -> None:
    """Register entity-related resources with the MCP server."""
    
    @mcp.resource("entities://list")
    def list_entities(
        entity_type: Optional[str] = None,
        db: Session = next(get_db())
    ) -> List[Dict[str, Any]]:
        """List all entities, optionally filtered by type."""
        try:
            query = db.query(Entity)
            if entity_type:
                query = query.filter(Entity.type == entity_type)
            
            entities = query.all()
            return [
                {
                    "id": e.id,
                    "name": e.name,
                    "type": e.type,
                    "metadata": e.metadata
                }
                for e in entities
            ]
        except Exception as e:
            raise DatabaseError(f"Failed to list entities: {str(e)}")

    @mcp.resource("entities://{entity_id}")
    def get_entity(
        entity_id: int,
        db: Session = next(get_db())
    ) -> Dict[str, Any]:
        """Get details for a specific entity."""
        try:
            entity = db.query(Entity).filter(Entity.id == entity_id).first()
            if not entity:
                raise DatabaseError(f"Entity {entity_id} not found")
                
            return {
                "id": entity.id,
                "name": entity.name,
                "type": entity.type,
                "metadata": entity.metadata,
                "created_at": entity.created_at.isoformat(),
                "updated_at": entity.updated_at.isoformat()
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get entity {entity_id}: {str(e)}")
