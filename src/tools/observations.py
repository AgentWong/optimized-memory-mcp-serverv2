"""
Observation management tools for the MCP server.
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from mcp.server.fastmcp import FastMCP
from ..db.connection import get_db
from ..db.models.observations import Observation
from ..db.models.entities import Entity
from ..utils.errors import DatabaseError, ValidationError

def register_tools(mcp: FastMCP) -> None:
    """Register observation management tools with the MCP server."""

    @mcp.tool()
    def create_observation(
        entity_id: int,
        observation_type: str,
        value: Dict[str, Any],
        metadata: Dict[str, Any] = None,
        db: Session = next(get_db())
    ) -> Dict[str, Any]:
        """Create a new observation for an entity."""
        try:
            # Verify entity exists
            entity = db.query(Entity).filter(Entity.id == entity_id).first()
            if not entity:
                raise ValidationError("Entity not found")
                
            observation = Observation(
                entity_id=entity_id,
                type=observation_type.lower(),
                value=value,
                metadata=metadata or {}
            )
            db.add(observation)
            db.commit()
            db.refresh(observation)
            
            return {
                "id": observation.id,
                "entity_id": observation.entity_id,
                "type": observation.type,
                "value": observation.value
            }
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"Failed to create observation: {str(e)}")

    @mcp.tool()
    def update_observation(
        observation_id: int,
        value: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        db: Session = next(get_db())
    ) -> Dict[str, Any]:
        """Update an existing observation."""
        try:
            observation = db.query(Observation).filter(
                Observation.id == observation_id
            ).first()
            
            if not observation:
                raise DatabaseError(f"Observation {observation_id} not found")
                
            if value:
                observation.value = value
            if metadata:
                observation.metadata.update(metadata)
                
            db.commit()
            db.refresh(observation)
            
            return {
                "id": observation.id,
                "entity_id": observation.entity_id,
                "type": observation.type,
                "value": observation.value,
                "metadata": observation.metadata
            }
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"Failed to update observation {observation_id}: {str(e)}")

    @mcp.tool()
    def delete_observation(
        observation_id: int,
        db: Session = next(get_db())
    ) -> Dict[str, str]:
        """Delete an observation."""
        try:
            observation = db.query(Observation).filter(
                Observation.id == observation_id
            ).first()
            
            if not observation:
                raise DatabaseError(f"Observation {observation_id} not found")
                
            db.delete(observation)
            db.commit()
            
            return {"message": f"Observation {observation_id} deleted successfully"}
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"Failed to delete observation {observation_id}: {str(e)}")
