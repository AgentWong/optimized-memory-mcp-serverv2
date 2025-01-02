"""
Observation management endpoints for the MCP server.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request
from ..utils.rate_limit import default_limiter
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, constr, validator
from sqlalchemy.orm import Session

from ..db.connection import get_db, cache_query
from ..db.models.observations import Observation
from ..db.models.entities import Entity
from ..utils.errors import DatabaseError

router = APIRouter(
    prefix="/observations",
    tags=["observations"],
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

class ObservationCreate(BaseModel):
    entity_id: int
    observation_type: constr(min_length=1, max_length=50)
    content: constr(min_length=1, max_length=10000)
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('observation_type')
    def validate_type(cls, v):
        if not v.strip():
            raise ValueError('type cannot be empty or whitespace')
        allowed_types = {'change', 'deprecation', 'security', 'compatibility'}
        if v.lower() not in allowed_types:
            raise ValueError(f'type must be one of: {allowed_types}')
        return v.lower()
    
    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('content cannot be empty or whitespace')
        return v.strip()

class ObservationUpdate(BaseModel):
    content: Optional[constr(min_length=1, max_length=10000)] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('content')
    def validate_content(cls, v):
        if v is not None and not v.strip():
            raise ValueError('content cannot be empty or whitespace')
        return v.strip() if v else None

@router.post("/", dependencies=[Depends(default_limiter)])
async def create_observation(
    request: Request,
    observation: ObservationCreate,
    db: Session = Depends(get_db)
) -> dict:
    """Create a new observation for an entity."""
    try:
        # Verify entity exists
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if not entity:
            raise HTTPException(
                status_code=404,
                detail="Entity not found"
            )
        
        observation = Observation(
            entity_id=observation.entity_id,
            observation_type=observation.observation_type,
            content=observation.content,
            metadata=observation.metadata
        )
        db.add(observation)
        db.commit()
        db.refresh(observation)
        return {
            "id": observation.id,
            "entity_id": observation.entity_id,
            "type": observation.observation_type,
            "content": observation.content
        }
    except HTTPException:
        raise
    except Exception as e:
        raise DatabaseError("Failed to create observation due to database error")

@router.get("/{observation_id}")
async def get_observation(
    observation_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """Get an observation by ID."""
    observation = db.query(Observation).filter(
        Observation.id == observation_id
    ).first()
    
    if not observation:
        raise HTTPException(status_code=404, detail="Observation not found")
        
    return {
        "id": observation.id,
        "entity_id": observation.entity_id,
        "type": observation.observation_type,
        "content": observation.content,
        "metadata": observation.metadata,
        "created_at": observation.created_at,
        "updated_at": observation.updated_at
    }

@router.get("/")
async def list_observations(
    entity_id: Optional[int] = None,
    observation_type: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[dict]:
    """List observations, optionally filtered by entity and type."""
    @cache_query(ttl_seconds=300)
    def get_observations(db_session, entity_id, observation_type):
        query = db_session.query(Observation).select_from(Observation)
        
        if entity_id:
            query = query.filter(Observation.entity_id == entity_id)\
                        .with_hint(Observation, 'USE INDEX (ix_observations_entity_id)')
        if observation_type:
            query = query.filter(Observation.observation_type == observation_type)\
                        .with_hint(Observation, 'USE INDEX (ix_observations_type)')
            
        # Use yield_per for memory efficient iteration of large result sets
        return [o for o in query.yield_per(100)]
    
    observations = get_observations(db, entity_id, observation_type)
    return [
        {
            "id": o.id,
            "entity_id": o.entity_id,
            "type": o.observation_type,
            "content": o.content,
            "metadata": o.metadata,
            "created_at": o.created_at,
            "updated_at": o.updated_at
        }
        for o in observations
    ]

@router.put("/{observation_id}")
async def update_observation(
    observation_id: int,
    observation_update: ObservationUpdate,
    db: Session = Depends(get_db)
) -> dict:
    """Update an observation."""
    observation = db.query(Observation).filter(
        Observation.id == observation_id
    ).first()
    
    if not observation:
        raise HTTPException(status_code=404, detail="Observation not found")
    
    if observation_update.content:
        observation.content = observation_update.content
    if observation_update.metadata:
        observation.metadata = observation_update.metadata
        
    try:
        db.commit()
        db.refresh(observation)
        return {
            "id": observation.id,
            "entity_id": observation.entity_id,
            "type": observation.observation_type,
            "content": observation.content,
            "metadata": observation.metadata,
            "created_at": observation.created_at,
            "updated_at": observation.updated_at
        }
    except Exception as e:
        raise DatabaseError("Failed to update observation due to database error")

@router.delete("/{observation_id}")
async def delete_observation(
    observation_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """Delete an observation."""
    observation = db.query(Observation).filter(
        Observation.id == observation_id
    ).first()
    
    if not observation:
        raise HTTPException(status_code=404, detail="Observation not found")
    
    try:
        db.delete(observation)
        db.commit()
        return {"message": f"Observation {observation_id} deleted"}
    except Exception as e:
        raise DatabaseError("Failed to delete observation due to database error")
