"""
Ansible management tools for the MCP server.
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from mcp.server.fastmcp import FastMCP
from ..db.connection import get_db
from ..db.models.ansible import AnsibleCollection
from ..utils.errors import DatabaseError, ValidationError

def register_tools(mcp: FastMCP) -> None:
    """Register Ansible management tools with the MCP server."""

    @mcp.tool()
    def register_collection(
        namespace: str,
        name: str,
        version: str,
        metadata: Dict[str, Any] = None,
        db: Session = next(get_db())
    ) -> Dict[str, Any]:
        """Register a new Ansible collection."""
        try:
            if not name or not name.strip():
                raise ValidationError("Collection name cannot be empty")
                
            collection = AnsibleCollection(
                namespace=namespace.strip(),
                name=name.strip(),
                version=version,
                metadata=metadata or {}
            )
            db.add(collection)
            db.commit()
            db.refresh(collection)
            
            return {
                "id": collection.id,
                "namespace": collection.namespace,
                "name": collection.name,
                "version": collection.version
            }
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"Failed to register collection: {str(e)}")

    @mcp.tool()
    def add_version(
        collection_name: str,
        version: str,
        metadata: Dict[str, Any] = None,
        db: Session = next(get_db())
    ) -> Dict[str, Any]:
        """Add a new version for an existing Ansible collection."""
        try:
            # Get existing collection to copy namespace
            existing = db.query(AnsibleCollection).filter(
                AnsibleCollection.name == collection_name
            ).first()
            
            if not existing:
                raise ValidationError(f"Collection {collection_name} not found")
                
            collection = AnsibleCollection(
                namespace=existing.namespace,
                name=collection_name,
                version=version,
                metadata=metadata or {}
            )
            db.add(collection)
            db.commit()
            db.refresh(collection)
            
            return {
                "id": collection.id,
                "namespace": collection.namespace,
                "name": collection.name,
                "version": collection.version
            }
        except Exception as e:
            db.rollback()
            raise DatabaseError(f"Failed to add version: {str(e)}")
