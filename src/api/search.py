from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.db.connection import get_db
from src.db.models.entities import Entity
from src.db.models.ansible import AnsibleCollection
from src.db.models.providers import Provider
from src.utils.errors import DatabaseError, ValidationError

router = APIRouter(
    prefix="/search",
    tags=["search"]
)

@router.get("/entities")
async def search_entities(
    query: str,
    entity_type: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Search entities by name, type, or attributes.
    """
    try:
        base_query = db.query(Entity)
        
        # Apply search filters
        search_filter = or_(
            Entity.name.ilike(f"%{query}%"),
            Entity.description.ilike(f"%{query}%"),
            Entity.attributes.cast(str).ilike(f"%{query}%")
        )
        base_query = base_query.filter(search_filter)
        
        # Filter by type if specified
        if entity_type:
            base_query = base_query.filter(Entity.type == entity_type)
            
        results = base_query.limit(limit).all()
        return [entity.to_dict() for entity in results]
    except Exception as e:
        raise DatabaseError(f"Search failed: {str(e)}")

@router.get("/collections")
async def search_collections(
    query: str,
    version: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Search Ansible collections by name or version.
    """
    try:
        base_query = db.query(AnsibleCollection)
        
        # Apply search filters
        search_filter = or_(
            AnsibleCollection.name.ilike(f"%{query}%"),
            AnsibleCollection.description.ilike(f"%{query}%")
        )
        base_query = base_query.filter(search_filter)
        
        # Filter by version if specified
        if version:
            base_query = base_query.filter(AnsibleCollection.version == version)
            
        results = base_query.limit(limit).all()
        return [collection.to_dict() for collection in results]
    except Exception as e:
        raise DatabaseError(f"Collection search failed: {str(e)}")

@router.get("/providers")
async def search_providers(
    query: str,
    provider_type: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Search infrastructure providers by name or type.
    """
    try:
        base_query = db.query(Provider)
        
        # Apply search filters
        search_filter = or_(
            Provider.name.ilike(f"%{query}%"),
            Provider.description.ilike(f"%{query}%")
        )
        base_query = base_query.filter(search_filter)
        
        # Filter by provider type if specified
        if provider_type:
            base_query = base_query.filter(Provider.type == provider_type)
            
        results = base_query.limit(limit).all()
        return [provider.to_dict() for provider in results]
    except Exception as e:
        raise DatabaseError(f"Provider search failed: {str(e)}")
