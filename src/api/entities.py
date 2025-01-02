"""
Entity management endpoints for the MCP server.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from ..utils.rate_limit import default_limiter
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, constr, validator
from sqlalchemy.orm import Session

from ..db.connection import get_db, cache_query
from ..db.models.entities import Entity
from ..utils.errors import DatabaseError

router = APIRouter(
    prefix="/entities",
    tags=["entities"],
    # Secure defaults for API endpoints
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
        429: {"description": "Too Many Requests"},
        500: {"description": "Internal Server Error"}
    }
)

class EntityCreate(BaseModel):
    name: constr(min_length=1, max_length=200)
    entity_type: constr(min_length=1, max_length=50)
    description: Optional[constr(max_length=1000)] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('name cannot be empty or whitespace')
        return v.strip()
    
    @validator('entity_type')
    def validate_type(cls, v):
        if not v.strip():
            raise ValueError('type cannot be empty or whitespace')
        allowed_types = {'provider', 'module', 'resource', 'collection'}
        if v.lower() not in allowed_types:
            raise ValueError(f'type must be one of: {allowed_types}')
        return v.lower()

class EntityUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=200)] = None
    description: Optional[constr(max_length=1000)] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('name cannot be empty or whitespace')
        return v.strip() if v else None

@router.post("/", dependencies=[Depends(default_limiter)])
async def create_entity(
    request: Request,
    entity: EntityCreate,
    db: Session = Depends(get_db)
) -> dict:
    """Create a new entity."""
    try:
        entity = Entity(
            name=entity.name,
            entity_type=entity.entity_type,
            description=entity.description
        )
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return {"id": entity.id, "name": entity.name}
    except Exception as e:
        raise DatabaseError("Failed to create entity due to database error")

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
    entity_update: EntityUpdate,
    db: Session = Depends(get_db)
) -> dict:
    """Update an entity."""
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    if entity_update.name:
        entity.name = entity_update.name
    if entity_update.description:
        entity.description = entity_update.description
        
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
        raise DatabaseError("Failed to update entity due to database error")

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
        raise DatabaseError("Failed to delete entity due to database error")
