"""
Observation-related resources for the MCP server.

Implements core MCP resource patterns for observation access:

observations://list
- Lists all observations in the system
- Optional filtering by entity_id and observation_type
- Returns list of observation objects with core fields
- Read-only access to observation data

observations://{observation_id}
- Gets detailed information for a specific observation
- Includes metadata, timestamps and full observation value
- Returns single observation object with complete details
- Read-only access to observation details

Each resource follows MCP protocol for:
- URL pattern matching
- Query parameter handling 
- Response formatting
- Error handling with proper MCP error types
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from mcp.server.fastmcp import FastMCP
from ..db.connection import get_db
from ..db.models.observations import Observation
from ..utils.errors import DatabaseError


def register_resources(mcp: FastMCP) -> None:
    """Register observation-related resources with the MCP server."""

    @mcp.resource(
        "observations://list?entity_id={entity_id}&observation_type={observation_type}"
    )
    def list_observations(
        entity_id: str = "null", observation_type: str = "null"
    ) -> List[Dict[str, Any]]:
        """List observations, optionally filtered."""
        try:
            db = next(get_db())
            query = db.query(Observation)

            if entity_id != "null":
                query = query.filter(Observation.entity_id == int(entity_id))
            if observation_type != "null":
                query = query.filter(Observation.type == observation_type)

            observations = query.all()
            return [
                {
                    "id": o.id,
                    "entity_id": o.entity_id,
                    "type": o.type,
                    "value": o.value,
                    "metadata": o.metadata,
                }
                for o in observations
            ]
        except Exception as e:
            raise DatabaseError(f"Failed to list observations: {str(e)}")

    @mcp.resource("observations://{observation_id}")
    def get_observation(observation_id: int) -> Dict[str, Any]:
        """Get details for a specific observation."""
        db = next(get_db())
        try:
            observation = (
                db.query(Observation).filter(Observation.id == observation_id).first()
            )

            if not observation:
                raise DatabaseError(f"Observation {observation_id} not found")

            return {
                "id": observation.id,
                "entity_id": observation.entity_id,
                "type": observation.type,
                "value": observation.value,
                "metadata": observation.metadata,
                "created_at": observation.created_at.isoformat(),
                "updated_at": observation.updated_at.isoformat(),
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get observation {observation_id}: {str(e)}")
