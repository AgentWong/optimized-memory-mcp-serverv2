"""
Ansible-related resources for the MCP server.
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from mcp.server.fastmcp import FastMCP
from ..db.connection import get_db
from ..db.models.ansible import AnsibleCollection
from ..utils.errors import DatabaseError

def register_resources(mcp: FastMCP) -> None:
    """Register Ansible-related resources with the MCP server."""
    
    @mcp.resource("ansible://collections")
    def list_collections(
        db: Session = next(get_db())
    ) -> List[Dict[str, Any]]:
        """List all registered Ansible collections."""
        try:
            collections = db.query(AnsibleCollection).all()
            return [
                {
                    "id": c.id,
                    "namespace": c.namespace,
                    "name": c.name,
                    "version": c.version,
                    "metadata": c.metadata
                }
                for c in collections
            ]
        except Exception as e:
            raise DatabaseError(f"Failed to list Ansible collections: {str(e)}")
