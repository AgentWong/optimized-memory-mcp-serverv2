"""
Search-related resources for the MCP server.

Implements core MCP resource patterns for entity search:

search://{query}
- Searches entities by name, type, or metadata
- Optional filtering by entity_type
- Configurable result limit
- Returns matching entity objects

Each resource follows MCP protocol for:
- URL pattern matching with query parameter
- Query parameter handling for filters
- Response formatting with pagination
- Error handling with proper MCP error types
"""

from typing import List, Dict, Any
from sqlalchemy import or_
from sqlalchemy.orm import Session

from mcp.server.fastmcp import FastMCP
from ..db.connection import get_db
from ..db.models.entities import Entity
from ..utils.errors import DatabaseError


def register_resources(mcp: FastMCP) -> None:
    """Register search-related resources with the MCP server."""

    @mcp.resource("search://{query}")
    def search_entities(
        query: str,
        entity_type: str = None,
        limit: int = 10,
        db: Session = next(get_db()),
    ) -> List[Dict[str, Any]]:
        """Search entities by name, type, or metadata."""
        try:
            base_query = db.query(Entity)

            # Apply search filters
            search_filter = or_(
                Entity.name.ilike(f"%{query}%"),
                Entity.type.ilike(f"%{query}%"),
                Entity.metadata.cast(str).ilike(f"%{query}%"),
            )
            base_query = base_query.filter(search_filter)

            # Filter by type if specified
            if entity_type:
                base_query = base_query.filter(Entity.type == entity_type)

            results = base_query.limit(limit).all()
            return [
                {"id": e.id, "name": e.name, "type": e.type, "metadata": e.metadata}
                for e in results
            ]
        except Exception as e:
            raise DatabaseError(f"Search failed: {str(e)}")
