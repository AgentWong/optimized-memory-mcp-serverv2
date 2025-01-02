"""
Deprecation warning endpoints for the MCP API.
Handles tracking and reporting of deprecated features across resources.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.db.models.providers import Provider
from src.db.models.ansible import AnsibleCollection
from src.utils.errors import ValidationError

router = APIRouter(tags=["deprecation"])

@router.get("/providers/{provider_id}/deprecations")
async def get_provider_deprecations(
    provider_id: int,
    version: Optional[str] = None,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get deprecation warnings for a specific provider version.
    
    Args:
        provider_id: ID of the provider to check
        version: Optional specific version to check, defaults to latest
        
    Returns:
        Dict containing active deprecation warnings
    """
    try:
        provider = db.query(Provider).filter(Provider.id == provider_id).first()
        if not provider:
            raise ValidationError("Provider not found", {"provider_id": provider_id})
            
        warnings = {
            "active_deprecations": [],
            "upcoming_deprecations": [],
            "removed_features": []
        }
        
        # Add deprecation checking logic here
        # For now returning empty warnings structure
        
        return warnings
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/ansible/{collection_name}/deprecations")
async def get_collection_deprecations(
    collection_name: str,
    version: Optional[str] = None,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get deprecation warnings for an Ansible collection version.
    
    Args:
        collection_name: Name of the collection to check
        version: Optional specific version to check, defaults to latest
        
    Returns:
        Dict containing active deprecation warnings
    """
    try:
        collection = db.query(AnsibleCollection).filter(
            AnsibleCollection.name == collection_name
        ).first()
        
        if not collection:
            raise ValidationError(
                "Collection not found",
                {"collection_name": collection_name}
            )
            
        warnings = {
            "active_deprecations": [],
            "upcoming_deprecations": [],
            "removed_features": []
        }
        
        # Add deprecation checking logic here
        # For now returning empty warnings structure
        
        return warnings
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/batch-deprecations")
async def get_batch_deprecations(
    provider_versions: Optional[List[dict]] = None,
    ansible_versions: Optional[List[dict]] = None,
    db: Session = Depends(get_db)
) -> dict:
    """
    Batch check deprecation warnings for multiple providers and collections.
    
    Args:
        provider_versions: List of provider IDs and optional versions to check
        ansible_versions: List of collection names and optional versions to check
        
    Returns:
        Dict containing deprecation warnings for all checked items
    """
    results = {
        "providers": {},
        "ansible": {},
        "summary": {
            "total_active_deprecations": 0,
            "total_upcoming_deprecations": 0
        }
    }
    
    try:
        if provider_versions:
            for pv in provider_versions:
                provider_result = await get_provider_deprecations(
                    pv["id"],
                    pv.get("version"),
                    db
                )
                results["providers"][pv["id"]] = provider_result
                
        if ansible_versions:
            for av in ansible_versions:
                ansible_result = await get_collection_deprecations(
                    av["name"],
                    av.get("version"),
                    db
                )
                results["ansible"][av["name"]] = ansible_result
                
        return results
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
