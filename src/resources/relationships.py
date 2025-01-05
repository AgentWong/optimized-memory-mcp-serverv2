"""
Relationship-related resources for the MCP server.

Implements core MCP resource patterns for relationship management:

relationships://list
- Lists all relationships in the system
- Optional filtering by source_id, target_id, and type
- Returns relationship objects with core metadata
- Read-only access to relationship definitions

relationships://{relationship_id}
- Gets detailed information for a specific relationship
- Includes full metadata and timestamps
- Returns complete relationship object
- Read-only access to relationship details

Each resource follows MCP protocol for:
- URL pattern matching
- Query parameter handling
- Response formatting
- Error handling with proper MCP error types
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from mcp.server.fastmcp import FastMCP, Context
from ..db.connection import get_db
from ..db.models.relationships import Relationship
from ..utils.errors import DatabaseError


def register_resources(mcp: FastMCP) -> None:
    """Register relationship-related resources with the MCP server."""

    @mcp.resource(
        "relationships://list?source_id={source_id}&target_id={target_id}&relationship_type={relationship_type}&ctx={ctx}"
    )
    async def list_relationships(
        ctx: Context,
        source_id: str = "null",
        target_id: str = "null",
        relationship_type: str = "null",
    ) -> List[Dict[str, Any]]:
        """List relationships, optionally filtered."""
        try:
            db = next(get_db())
            query = db.query(Relationship)

            if source_id != "null":
                query = query.filter(Relationship.source_id == int(source_id))
            if target_id != "null":
                query = query.filter(Relationship.target_id == int(target_id))
            if relationship_type != "null":
                query = query.filter(Relationship.type == relationship_type)

            relationships = query.all()
            ctx.info(f"Listed {len(relationships)} relationships")
            return [
                {
                    "id": r.id,
                    "source_id": r.source_id,
                    "target_id": r.target_id,
                    "type": r.type,
                    "metadata": r.metadata,
                }
                for r in relationships
            ]
        except Exception as e:
            raise DatabaseError(f"Failed to list relationships: {str(e)}")

    @mcp.resource("relationships://{relationship_id}")
    def get_relationship(relationship_id: int) -> Dict[str, Any]:
        db = next(get_db())
        """Get details for a specific relationship."""
        try:
            relationship = (
                db.query(Relationship)
                .filter(Relationship.id == relationship_id)
                .first()
            )

            if not relationship:
                raise DatabaseError(f"Relationship {relationship_id} not found")

            return {
                "id": relationship.id,
                "source_id": relationship.source_id,
                "target_id": relationship.target_id,
                "type": relationship.type,
                "metadata": relationship.metadata,
                "created_at": relationship.created_at.isoformat(),
                "updated_at": relationship.updated_at.isoformat(),
            }
        except Exception as e:
            raise DatabaseError(
                f"Failed to get relationship {relationship_id}: {str(e)}"
            )
