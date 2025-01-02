"""
Observation management endpoints for the MCP server.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from ..db.connection import get_db, cache_query
from ..db.models.observations import Observation
from ..db.models.entities import Entity
from ..utils.errors import DatabaseError

router = APIRouter(prefix="/observations", tags=["observations"])

@router.post("/")
async def create_observation(
    entity_id: int,
    observation_type: str,
    content: str,
    metadata: Optional[dict] = None,
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
            entity_id=entity_id,
            observation_type=observation_type,
            content=content,
            metadata=metadata
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
        raise DatabaseError(f"Failed to create observation: {str(e)}")

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
    content: Optional[str] = None,
    metadata: Optional[dict] = None,
    db: Session = Depends(get_db)
) -> dict:
    """Update an observation."""
    observation = db.query(Observation).filter(
        Observation.id == observation_id
    ).first()
    
    if not observation:
        raise HTTPException(status_code=404, detail="Observation not found")
    
    if content:
        observation.content = content
    if metadata:
        observation.metadata = metadata
        
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
        raise DatabaseError(f"Failed to update observation: {str(e)}")

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
        raise DatabaseError(f"Failed to delete observation: {str(e)}")
