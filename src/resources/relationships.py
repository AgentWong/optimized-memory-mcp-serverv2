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

from mcp.server.fastmcp import FastMCP
from ..db.connection import get_db
from ..db.models.relationships import Relationship
from ..utils.errors import DatabaseError

def register_resources(mcp: FastMCP) -> None:
    """Register relationship-related resources with the MCP server."""
    
    @mcp.resource("relationships://list")
    def list_relationships(
        source_id: Optional[int] = None,
        target_id: Optional[int] = None,
        relationship_type: Optional[str] = None,
        db: Session = next(get_db())
    ) -> List[Dict[str, Any]]:
        """List relationships, optionally filtered."""
        try:
            query = db.query(Relationship)
            
            if source_id:
                query = query.filter(Relationship.source_id == source_id)
            if target_id:
                query = query.filter(Relationship.target_id == target_id)
            if relationship_type:
                query = query.filter(Relationship.type == relationship_type)
                
            relationships = query.all()
            return [
                {
                    "id": r.id,
                    "source_id": r.source_id,
                    "target_id": r.target_id,
                    "type": r.type,
                    "metadata": r.metadata
                }
                for r in relationships
            ]
        except Exception as e:
            raise DatabaseError(f"Failed to list relationships: {str(e)}")

    @mcp.resource("relationships://{relationship_id}")
    def get_relationship(
        relationship_id: int,
        db: Session = next(get_db())
    ) -> Dict[str, Any]:
        """Get details for a specific relationship."""
        try:
            relationship = db.query(Relationship).filter(
                Relationship.id == relationship_id
            ).first()
            
            if not relationship:
                raise DatabaseError(f"Relationship {relationship_id} not found")
                
            return {
                "id": relationship.id,
                "source_id": relationship.source_id,
                "target_id": relationship.target_id,
                "type": relationship.type,
                "metadata": relationship.metadata,
                "created_at": relationship.created_at.isoformat(),
                "updated_at": relationship.updated_at.isoformat()
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get relationship {relationship_id}: {str(e)}")
