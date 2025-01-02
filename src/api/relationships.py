"""
Relationship management endpoints for the MCP server.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from ..utils.rate_limit import default_limiter
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, constr, validator
from sqlalchemy.orm import Session

from ..db.connection import get_db, cache_query
from ..db.models.relationships import Relationship
from ..db.models.entities import Entity
from ..utils.errors import DatabaseError

router = APIRouter(
    prefix="/relationships",
    tags=["relationships"],
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

class RelationshipCreate(BaseModel):
    source_id: int
    target_id: int
    relationship_type: constr(min_length=1, max_length=50)
    description: Optional[constr(max_length=1000)] = None
    
    @validator('relationship_type')
    def validate_type(cls, v):
        if not v.strip():
            raise ValueError('type cannot be empty or whitespace')
        allowed_types = {'depends_on', 'contains', 'references', 'implements', 'extends'}
        if v.lower() not in allowed_types:
            raise ValueError(f'type must be one of: {allowed_types}')
        return v.lower()
    
    @validator('description')
    def validate_description(cls, v):
        if v is not None and not v.strip():
            raise ValueError('description cannot be empty or whitespace')
        return v.strip() if v else None

class RelationshipUpdate(BaseModel):
    relationship_type: Optional[constr(min_length=1, max_length=50)] = None
    description: Optional[constr(max_length=1000)] = None
    
    @validator('relationship_type')
    def validate_type(cls, v):
        if v is not None and not v.strip():
            raise ValueError('type cannot be empty or whitespace')
        allowed_types = {'depends_on', 'contains', 'references', 'implements', 'extends'}
        if v is not None and v.lower() not in allowed_types:
            raise ValueError(f'type must be one of: {allowed_types}')
        return v.lower() if v else None
    
    @validator('description')
    def validate_description(cls, v):
        if v is not None and not v.strip():
            raise ValueError('description cannot be empty or whitespace')
        return v.strip() if v else None

@router.post("/", dependencies=[Depends(default_limiter)])
async def create_relationship(
    request: Request,
    relationship: RelationshipCreate,
    db: Session = Depends(get_db)
) -> dict:
    """Create a new relationship between entities."""
    try:
        # Verify both entities exist
        source = db.query(Entity).filter(Entity.id == relationship.source_id).first()
        target = db.query(Entity).filter(Entity.id == relationship.target_id).first()
        
        if not source or not target:
            raise HTTPException(
                status_code=404,
                detail="Source or target entity not found"
            )
        
        relationship_obj = Relationship(
            source_id=relationship.source_id,
            target_id=relationship.target_id,
            relationship_type=relationship.relationship_type,
            description=relationship.description
        )
        db.add(relationship_obj)
        db.commit()
        db.refresh(relationship_obj)
        return {
            "id": relationship_obj.id,
            "source_id": relationship_obj.source_id,
            "target_id": relationship_obj.target_id,
            "type": relationship_obj.relationship_type
        }
    except HTTPException:
        raise
    except Exception as e:
        raise DatabaseError("Failed to create relationship due to database error")

@router.get("/{relationship_id}")
async def get_relationship(
    relationship_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """Get a relationship by ID."""
    relationship = db.query(Relationship).filter(
        Relationship.id == relationship_id
    ).first()
    
    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")
        
    return {
        "id": relationship.id,
        "source_id": relationship.source_id,
        "target_id": relationship.target_id,
        "type": relationship.relationship_type,
        "description": relationship.description
    }

@router.get("/")
async def list_relationships(
    source_id: Optional[int] = None,
    target_id: Optional[int] = None,
    relationship_type: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[dict]:
    """List relationships, optionally filtered."""
    @cache_query(ttl_seconds=300)
    def get_relationships(db_session, source_id, target_id, relationship_type):
        query = db_session.query(Relationship).select_from(Relationship)
        
        if source_id:
            query = query.filter(Relationship.source_id == source_id)\
                        .with_hint(Relationship, 'USE INDEX (ix_relationships_source)')
        if target_id:
            query = query.filter(Relationship.target_id == target_id)\
                        .with_hint(Relationship, 'USE INDEX (ix_relationships_target)')
        if relationship_type:
            query = query.filter(Relationship.relationship_type == relationship_type)\
                        .with_hint(Relationship, 'USE INDEX (ix_relationships_type)')
            
        # Use yield_per for memory efficient iteration of large result sets  
        return [r for r in query.yield_per(100)]
    
    relationships = get_relationships(db, source_id, target_id, relationship_type)
    return [
        {
            "id": r.id,
            "source_id": r.source_id,
            "target_id": r.target_id,
            "type": r.relationship_type,
            "description": r.description
        }
        for r in relationships
    ]

@router.put("/{relationship_id}")
async def update_relationship(
    relationship_id: int,
    relationship_update: RelationshipUpdate,
    db: Session = Depends(get_db)
) -> dict:
    """Update a relationship."""
    relationship = db.query(Relationship).filter(
        Relationship.id == relationship_id
    ).first()
    
    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")
    
    if relationship_update.relationship_type:
        relationship.relationship_type = relationship_update.relationship_type
    if relationship_update.description:
        relationship.description = relationship_update.description
        
    try:
        db.commit()
        db.refresh(relationship)
        return {
            "id": relationship.id,
            "source_id": relationship.source_id,
            "target_id": relationship.target_id,
            "type": relationship.relationship_type,
            "description": relationship.description
        }
    except Exception as e:
        raise DatabaseError("Failed to update relationship due to database error")

@router.delete("/{relationship_id}")
async def delete_relationship(
    relationship_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """Delete a relationship."""
    relationship = db.query(Relationship).filter(
        Relationship.id == relationship_id
    ).first()
    
    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")
    
    try:
        db.delete(relationship)
        db.commit()
        return {"message": f"Relationship {relationship_id} deleted"}
    except Exception as e:
        raise DatabaseError("Failed to delete relationship due to database error")
