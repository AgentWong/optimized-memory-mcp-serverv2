"""
Provider-related resources for the MCP server.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from mcp.server.fastmcp import FastMCP
from ..db.connection import get_db
from ..db.models.providers import Provider
from ..utils.errors import DatabaseError

def register_resources(mcp: FastMCP) -> None:
    """Register provider-related resources with the MCP server."""
    
    @mcp.resource("providers://{provider}/resources")
    def list_provider_resources(
        provider: str,
        db: Session = next(get_db())
    ) -> List[Dict[str, Any]]:
        """List all resources for a specific provider."""
        try:
            provider_obj = db.query(Provider).filter(
                Provider.name == provider
            ).first()
            
            if not provider_obj:
                raise DatabaseError(f"Provider {provider} not found")
                
            return [
                {
                    "id": r.id,
                    "name": r.name,
                    "type": r.resource_type,
                    "schema": r.schema,
                    "metadata": r.metadata
                }
                for r in provider_obj.resources
            ]
        except Exception as e:
            raise DatabaseError(f"Failed to list resources for provider {provider}: {str(e)}")
