"""
Provider management tools for the MCP server.
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from mcp.server.fastmcp import FastMCP
from ..db.connection import get_db
from ..db.models.providers import Provider
from ..utils.errors import DatabaseError, ValidationError

def register_tools(mcp: FastMCP) -> None:
    """Register provider management tools with the MCP server."""

    @mcp.tool()
    def register_provider(
        name: str,
        provider_type: str,
        version: str,
        metadata: Dict[str, Any] = None,
        db: Session = next(get_db())
    ) -> Dict[str, Any]:
        """Register a new infrastructure provider."""
        try:
            if not name or not name.strip():
                raise ValidationError("Provider name cannot be empty")
                
            provider = Provider(
                name=name.strip(),
                type=provider_type.lower(),
                version=version,
                metadata=metadata or {}
            )
            db.add(provider)
            db.commit()
            db.refresh(provider)
            
            return {
                "id": provider.id,
                "name": provider.name,
                "type": provider.type,
                "version": provider.version
            }
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"Failed to register provider: {str(e)}")
