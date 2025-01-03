"""
Observation-related resources for the MCP server.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from mcp.server.fastmcp import FastMCP
from ..db.connection import get_db
from ..db.models.observations import Observation
from ..utils.errors import DatabaseError

def register_resources(mcp: FastMCP) -> None:
    """Register observation-related resources with the MCP server."""
    
    @mcp.resource("observations://list")
    def list_observations(
        entity_id: Optional[int] = None,
        observation_type: Optional[str] = None,
        db: Session = next(get_db())
    ) -> List[Dict[str, Any]]:
        """List observations, optionally filtered."""
        try:
            query = db.query(Observation)
            
            if entity_id:
                query = query.filter(Observation.entity_id == entity_id)
            if observation_type:
                query = query.filter(Observation.type == observation_type)
                
            observations = query.all()
            return [
                {
                    "id": o.id,
                    "entity_id": o.entity_id,
                    "type": o.type,
                    "value": o.value,
                    "metadata": o.metadata
                }
                for o in observations
            ]
        except Exception as e:
            raise DatabaseError(f"Failed to list observations: {str(e)}")

    @mcp.resource("observations://{observation_id}")
    def get_observation(
        observation_id: int,
        db: Session = next(get_db())
    ) -> Dict[str, Any]:
        """Get details for a specific observation."""
        try:
            observation = db.query(Observation).filter(
                Observation.id == observation_id
            ).first()
            
            if not observation:
                raise DatabaseError(f"Observation {observation_id} not found")
                
            return {
                "id": observation.id,
                "entity_id": observation.entity_id,
                "type": observation.type,
                "value": observation.value,
                "metadata": observation.metadata,
                "created_at": observation.created_at.isoformat(),
                "updated_at": observation.updated_at.isoformat()
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get observation {observation_id}: {str(e)}")
