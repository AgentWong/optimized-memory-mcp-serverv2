"""
Entity management endpoints for the MCP server.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from ..db.connection import get_db, cache_query
from ..db.models.entities import Entity
from ..utils.errors import DatabaseError

router = APIRouter(prefix="/entities", tags=["entities"])

@router.post("/")
async def create_entity(
    name: str,
    entity_type: str,
    description: Optional[str] = None,
    db: Session = Depends(get_db)
) -> dict:
    """Create a new entity."""
    try:
        entity = Entity(
            name=name,
            entity_type=entity_type,
            description=description
        )
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return {"id": entity.id, "name": entity.name}
    except Exception as e:
        raise DatabaseError(f"Failed to create entity: {str(e)}")

@router.get("/{entity_id}")
async def get_entity(entity_id: int, db: Session = Depends(get_db)) -> dict:
    """Get an entity by ID."""
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return {
        "id": entity.id,
        "name": entity.name,
        "type": entity.entity_type,
        "description": entity.description
    }

@router.get("/")
async def list_entities(
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[dict]:
    """List all entities, optionally filtered by type."""
    @cache_query(ttl_seconds=300)
    def get_entities(db_session, entity_type):
        query = db_session.query(Entity).select_from(Entity)
        if entity_type:
            query = query.filter(Entity.entity_type == entity_type)\
                        .with_hint(Entity, 'USE INDEX (ix_entities_type)')
        # Use yield_per for memory efficient iteration of large result sets
        return [e for e in query.yield_per(100)]
    
    entities = get_entities(db, entity_type)
    return [
        {
            "id": e.id,
            "name": e.name,
            "type": e.entity_type,
            "description": e.description
        }
        for e in entities
    ]

@router.put("/{entity_id}")
async def update_entity(
    entity_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db)
) -> dict:
    """Update an entity."""
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    if name:
        entity.name = name
    if description:
        entity.description = description
        
    try:
        db.commit()
        db.refresh(entity)
        return {
            "id": entity.id,
            "name": entity.name,
            "type": entity.entity_type,
            "description": entity.description
        }
    except Exception as e:
        raise DatabaseError(f"Failed to update entity: {str(e)}")

@router.delete("/{entity_id}")
async def delete_entity(entity_id: int, db: Session = Depends(get_db)) -> dict:
    """Delete an entity."""
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    try:
        db.delete(entity)
        db.commit()
        return {"message": f"Entity {entity_id} deleted"}
    except Exception as e:
        raise DatabaseError(f"Failed to delete entity: {str(e)}")
