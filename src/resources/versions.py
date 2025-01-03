"""
Version-related resources for the MCP server.
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from mcp.server.fastmcp import FastMCP
from ..db.connection import get_db
from ..db.models.ansible import AnsibleCollection
from ..utils.errors import DatabaseError

def register_resources(mcp: FastMCP) -> None:
    """Register version-related resources with the MCP server."""
    
    @mcp.resource("collections://{collection_name}/versions")
    def list_collection_versions(
        collection_name: str,
        db: Session = next(get_db())
    ) -> List[Dict[str, Any]]:
        """List all versions for a specific collection."""
        try:
            versions = db.query(AnsibleCollection).filter(
                AnsibleCollection.name == collection_name
            ).order_by(AnsibleCollection.version.desc()).all()
            
            if not versions:
                raise DatabaseError(f"Collection {collection_name} not found")
                
            return [
                {
                    "id": v.id,
                    "namespace": v.namespace,
                    "name": v.name,
                    "version": v.version,
                    "metadata": v.metadata
                }
                for v in versions
            ]
        except Exception as e:
            raise DatabaseError(f"Failed to list versions for collection {collection_name}: {str(e)}")
