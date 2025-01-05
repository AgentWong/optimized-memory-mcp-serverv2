"""
Observation management tools for the MCP server.

This module implements MCP tools for managing entity observations and their metadata.
Tools provide capabilities for:
- Recording new observations about infrastructure entities
- Updating observation data and metadata
- Managing observation lifecycle
- Tracking observation history

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
from ..db.models.observations import Observation
from ..db.models.entities import Entity
from ..utils.errors import DatabaseError, ValidationError


async def register_tools(mcp: FastMCP) -> list:
    """Register observation management tools with the MCP server.

    This function registers all observation-related tools with the MCP server instance.
    Tools include:
    - create_observation: Record new observations about entities
    - update_observation: Modify existing observation data
    - delete_observation: Remove observations from the system

    Each tool is registered with proper type hints, error handling, and database integration.
    Tools follow MCP protocol patterns for consistent behavior and error reporting.

    Observation tools handle:
    - Status updates and health checks
    - Performance metrics and statistics
    - Configuration changes and updates
    - Security events and alerts
    - Compliance validation results

    Tool capabilities include:
    - Structured observation recording
    - Historical data tracking
    - Metadata management
    - Observation categorization
    - Data validation rules
    """

    @mcp.tool()
    async def create_observation(
        entity_id: int,
        observation_type: str,
        value: Dict[str, Any],
        metadata: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Create a new observation for an entity.

        Args:
            entity_id: ID of the entity to observe
            observation_type: Type of observation (e.g. 'status', 'metric', 'event')
            value: Dictionary containing observation data
            metadata: Optional metadata dictionary
            db: Database session

        Returns:
            Dict containing observation id and details

        Raises:
            ValidationError: If entity not found
            DatabaseError: If database operation fails

        Example:
            >>> result = create_observation(
            ...     entity_id=1,
            ...     observation_type="status",
            ...     value={"state": "running", "uptime": "24h"},
            ...     metadata={"source": "monitoring"}
            ... )
            >>> print(result)
            {
                "id": 1,
                "entity_id": 1,
                "type": "status",
                "value": {
                    "state": "running",
                    "uptime": "24h"
                }
            }
        """
        try:
            # Verify entity exists
            entity = db.query(Entity).filter(Entity.id == entity_id).first()
            if not entity:
                raise ValidationError("Entity not found")

            observation = Observation(
                entity_id=entity_id,
                type=observation_type.lower(),
                value=value,
                metadata=metadata or {},
            )
            db.add(observation)
            db.commit()
            db.refresh(observation)

            return {
                "id": observation.id,
                "entity_id": observation.entity_id,
                "type": observation.type,
                "value": observation.value,
            }
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"Failed to create observation: {str(e)}")

    @mcp.tool()
    async def update_observation(
        observation_id: int,
        value: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update an existing observation.

        Args:
            observation_id: ID of observation to update
            value: Optional new observation value dictionary
            metadata: Optional metadata to merge with existing
            db: Database session

        Returns:
            Dict containing updated observation details

        Raises:
            ValidationError: If observation not found
            DatabaseError: If update fails

        Example:
            >>> result = update_observation(
            ...     observation_id=1,
            ...     value={"state": "stopped", "downtime": "10m"},
            ...     metadata={"updated_by": "system"}
            ... )
            >>> print(result)
            {
                "id": 1,
                "entity_id": 1,
                "type": "status",
                "value": {
                    "state": "stopped",
                    "downtime": "10m"
                },
                "metadata": {
                    "source": "monitoring",
                    "updated_by": "system"
                }
            }
        """
        try:
            observation = (
                db.query(Observation).filter(Observation.id == observation_id).first()
            )

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
                "metadata": observation.metadata,
            }
        except Exception as e:
            db.rollback()
            raise DatabaseError(
                f"Failed to update observation {observation_id}: {str(e)}"
            )

    @mcp.tool()
    async def delete_observation(observation_id: int) -> Dict[str, str]:
        """Delete an observation.

        Args:
            observation_id: ID of observation to delete
            db: Database session

        Returns:
            Dict containing success message

        Raises:
            ValidationError: If observation not found
            DatabaseError: If deletion fails

        Example:
            >>> result = delete_observation(observation_id=1)
            >>> print(result)
            {
                "message": "Observation 1 deleted successfully"
            }
        """
        try:
            observation = (
                db.query(Observation).filter(Observation.id == observation_id).first()
            )

            if not observation:
                raise DatabaseError(f"Observation {observation_id} not found")

            db.delete(observation)
            db.commit()

            return {"message": f"Observation {observation_id} deleted successfully"}
        except Exception as e:
            db.rollback()
            raise DatabaseError(
                f"Failed to delete observation {observation_id}: {str(e)}"
            )
