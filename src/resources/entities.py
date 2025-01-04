"""Entity-related MCP resources."""
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP, Context
from ..db.connection import get_db
from ..db.models.entities import Entity
from ..utils.errors import DatabaseError

def register_resources(mcp: FastMCP) -> None:
    """Register entity-related MCP resources."""

    @mcp.resource("resource://entities/list")
    async def list_entities(ctx: Context) -> List[Dict[str, Any]]:
        """List all entities."""
        db = next(get_db())
        try:
            entities = db.query(Entity).all()
            return [entity.to_dict() for entity in entities]
        except Exception as e:
            raise DatabaseError(f"Failed to list entities: {str(e)}")

    @mcp.resource("resource://entities/{entity_id}")
    async def get_entity(ctx: Context, entity_id: str) -> Dict[str, Any]:
        """Get details for a specific entity."""
        db = next(get_db())
        try:
            entity = db.query(Entity).filter(Entity.id == int(entity_id)).first()
            if not entity:
                raise DatabaseError(f"Entity {entity_id} not found")
            return entity.to_dict()
        except ValueError:
            raise DatabaseError(f"Invalid entity ID format: {entity_id}")
        except Exception as e:
            raise DatabaseError(f"Failed to get entity {entity_id}: {str(e)}")
