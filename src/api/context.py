"""
Context retrieval endpoints for the MCP server.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from ..db.connection import get_db
from ..db.models.entities import Entity
from ..db.models.relationships import Relationship
from ..db.models.observations import Observation
from ..utils.errors import DatabaseError

router = APIRouter(prefix="/context", tags=["context"])

@router.get("/entity/{entity_id}")
async def get_entity_context(
    entity_id: int,
    include_relationships: bool = True,
    include_observations: bool = True,
    relationship_types: Optional[List[str]] = None,
    observation_types: Optional[List[str]] = None,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get full context for an entity, including relationships and observations.
    Optionally filter by relationship and observation types.
    """
    try:
        # Get entity
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
            
        context = {
            "entity": {
                "id": entity.id,
                "name": entity.name,
                "type": entity.entity_type,
                "description": entity.description
            }
        }
        
        # Get relationships if requested
        if include_relationships:
            relationships_query = db.query(Relationship).filter(
                (Relationship.source_id == entity_id) |
                (Relationship.target_id == entity_id)
            )
            
            if relationship_types:
                relationships_query = relationships_query.filter(
                    Relationship.relationship_type.in_(relationship_types)
                )
                
            relationships = relationships_query.all()
            context["relationships"] = [
                {
                    "id": r.id,
                    "type": r.relationship_type,
                    "source_id": r.source_id,
                    "target_id": r.target_id,
                    "description": r.description,
                    "direction": "outgoing" if r.source_id == entity_id else "incoming"
                }
                for r in relationships
            ]
            
        # Get observations if requested
        if include_observations:
            observations_query = db.query(Observation).filter(
                Observation.entity_id == entity_id
            )
            
            if observation_types:
                observations_query = observations_query.filter(
                    Observation.observation_type.in_(observation_types)
                )
                
            observations = observations_query.all()
            context["observations"] = [
                {
                    "id": o.id,
                    "type": o.observation_type,
                    "content": o.content,
                    "metadata": o.metadata,
                    "created_at": o.created_at,
                    "updated_at": o.updated_at
                }
                for o in observations
            ]
            
        return context
        
    except HTTPException:
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to retrieve entity context: {str(e)}")

@router.get("/related/{entity_id}")
async def get_related_entities(
    entity_id: int,
    relationship_types: Optional[List[str]] = None,
    include_observations: bool = False,
    max_depth: int = 1,
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Get related entities up to a specified depth, optionally filtered by relationship types.
    Can include observations for the related entities.
    """
    try:
        def get_entities_at_depth(current_id: int, current_depth: int, visited: set) -> List[dict]:
            if current_depth > max_depth or current_id in visited:
                return []
                
            visited.add(current_id)
            
            # Get relationships for current entity
            relationships_query = db.query(Relationship).filter(
                (Relationship.source_id == current_id) |
                (Relationship.target_id == current_id)
            )
            
            if relationship_types:
                relationships_query = relationships_query.filter(
                    Relationship.relationship_type.in_(relationship_types)
                )
                
            relationships = relationships_query.all()
            
            related_entities = []
            for r in relationships:
                related_id = r.target_id if r.source_id == current_id else r.source_id
                
                if related_id not in visited:
                    related_entity = db.query(Entity).filter(Entity.id == related_id).first()
                    if related_entity:
                        entity_data = {
                            "id": related_entity.id,
                            "name": related_entity.name,
                            "type": related_entity.entity_type,
                            "description": related_entity.description,
                            "relationship": {
                                "type": r.relationship_type,
                                "direction": "outgoing" if r.source_id == current_id else "incoming"
                            }
                        }
                        
                        if include_observations:
                            observations = db.query(Observation).filter(
                                Observation.entity_id == related_id
                            ).all()
                            entity_data["observations"] = [
                                {
                                    "type": o.observation_type,
                                    "content": o.content,
                                    "metadata": o.metadata
                                }
                                for o in observations
                            ]
                            
                        related_entities.append(entity_data)
                        
                        # Recursively get entities at next depth
                        if current_depth < max_depth:
                            related_entities.extend(
                                get_entities_at_depth(related_id, current_depth + 1, visited)
                            )
                            
            return related_entities
            
        # Verify initial entity exists
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
            
        # Get all related entities up to max_depth
        return get_entities_at_depth(entity_id, 1, set())
        
    except HTTPException:
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to retrieve related entities: {str(e)}")
