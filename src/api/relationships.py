"""
Relationship management endpoints for the MCP server.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from ..db.connection import get_db
from ..db.models.relationships import Relationship
from ..db.models.entities import Entity
from ..utils.errors import DatabaseError

router = APIRouter(prefix="/relationships", tags=["relationships"])

@router.post("/")
async def create_relationship(
    source_id: int,
    target_id: int,
    relationship_type: str,
    description: Optional[str] = None,
    db: Session = Depends(get_db)
) -> dict:
    """Create a new relationship between entities."""
    try:
        # Verify both entities exist
        source = db.query(Entity).filter(Entity.id == source_id).first()
        target = db.query(Entity).filter(Entity.id == target_id).first()
        
        if not source or not target:
            raise HTTPException(
                status_code=404,
                detail="Source or target entity not found"
            )
        
        relationship = Relationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            description=description
        )
        db.add(relationship)
        db.commit()
        db.refresh(relationship)
        return {
            "id": relationship.id,
            "source_id": relationship.source_id,
            "target_id": relationship.target_id,
            "type": relationship.relationship_type
        }
    except HTTPException:
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to create relationship: {str(e)}")

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
    query = db.query(Relationship)
    
    if source_id:
        query = query.filter(Relationship.source_id == source_id)
    if target_id:
        query = query.filter(Relationship.target_id == target_id)
    if relationship_type:
        query = query.filter(Relationship.relationship_type == relationship_type)
        
    relationships = query.all()
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
    relationship_type: Optional[str] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db)
) -> dict:
    """Update a relationship."""
    relationship = db.query(Relationship).filter(
        Relationship.id == relationship_id
    ).first()
    
    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")
    
    if relationship_type:
        relationship.relationship_type = relationship_type
    if description:
        relationship.description = description
        
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
        raise DatabaseError(f"Failed to update relationship: {str(e)}")

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
        raise DatabaseError(f"Failed to delete relationship: {str(e)}")
