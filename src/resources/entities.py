"""Entity-related MCP resources."""
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP, Context
from ..db.connection import get_db
from ..db.models.entities import Entity
from ..utils.errors import DatabaseError

def register_resources(mcp: FastMCP) -> None:
    """Register entity-related MCP resources."""

    @mcp.resource("entities://list")
    async def list_entities(ctx: Context) -> List[Dict[str, Any]]:
        """List all entities in the system.
        
        Args:
            ctx: MCP context object
            
        Returns:
            List of dictionaries containing entity details
            
        Raises:
            DatabaseError: If database query fails
        """
        db = next(get_db())
        try:
            entities = db.query(Entity).all()
            return [entity.to_dict() for entity in entities]
        except Exception as e:
            raise DatabaseError(f"Failed to list entities: {str(e)}")

    @mcp.resource("entities://{entity_id}")
    async def get_entity(ctx: Context, entity_id: str) -> Dict[str, Any]:
        """Get details for a specific entity.
        
        Args:
            ctx: MCP context object
            entity_id: Unique identifier of the entity
            
        Returns:
            Dict containing entity details
            
        Raises:
            DatabaseError: If entity not found or database error occurs
            ValidationError: If entity_id format is invalid
        """
        from ..utils.errors import ValidationError
        
        # Validate entity_id format
        try:
            entity_id_int = int(entity_id)
            if entity_id_int < 1:
                raise ValueError("Entity ID must be positive")
        except ValueError as e:
            raise ValidationError(f"Invalid entity ID format: {str(e)}")

        # Get database session from context
        db = next(get_db())
        
        try:
            # Query entity with relationships and observations
            entity = (
                db.query(Entity)
                .filter(Entity.id == entity_id_int)
                .first()
            )
            
            if not entity:
                raise DatabaseError(
                    f"Entity {entity_id} not found",
                    details={"entity_id": entity_id}
                )

            # Convert to dict with related data
            result = entity.to_dict()
            
            # Log access via MCP context
            await ctx.info(f"Retrieved entity {entity_id}")
            
            return result

        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(
                f"Failed to get entity {entity_id}",
                details={"error": str(e)}
            )
