"""
Compatibility checking endpoints for the MCP API.
Handles version compatibility checks between different resources.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.db.models.providers import Provider
from src.db.models.ansible import AnsibleCollection
from src.utils.errors import ValidationError

router = APIRouter(tags=["compatibility"])

@router.get("/providers/{provider_id}/compatibility")
async def check_provider_compatibility(
    provider_id: int,
    version: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Check compatibility of a specific provider version against current resources.
    
    Args:
        provider_id: ID of the provider to check
        version: Version string to check compatibility for
        
    Returns:
        Dict containing compatibility status and any warnings
    """
    try:
        provider = db.query(Provider).filter(Provider.id == provider_id).first()
        if not provider:
            raise ValidationError("Provider not found", {"provider_id": provider_id})
            
        # Compare versions and check compatibility
        compatibility = {
            "is_compatible": True,
            "warnings": [],
            "breaking_changes": []
        }
        
        # Add compatibility checks here
        # For now returning basic compatibility
        
        return compatibility
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/ansible/{collection_name}/compatibility") 
async def check_ansible_compatibility(
    collection_name: str,
    version: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Check compatibility of an Ansible collection version.
    
    Args:
        collection_name: Name of the collection to check
        version: Version string to check compatibility for
        
    Returns:
        Dict containing compatibility status and any warnings
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
            
        compatibility = {
            "is_compatible": True,
            "warnings": [],
            "breaking_changes": []
        }
        
        # Add compatibility checks here
        # For now returning basic compatibility
        
        return compatibility
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/batch-compatibility")
async def check_batch_compatibility(
    provider_versions: Optional[List[dict]] = None,
    ansible_versions: Optional[List[dict]] = None,
    db: Session = Depends(get_db)
) -> dict:
    """
    Batch check compatibility for multiple providers and collections.
    
    Args:
        provider_versions: List of provider IDs and versions to check
        ansible_versions: List of collection names and versions to check
        
    Returns:
        Dict containing compatibility results for all checked items
    """
    results = {
        "providers": {},
        "ansible": {},
        "overall_compatible": True
    }
    
    try:
        if provider_versions:
            for pv in provider_versions:
                provider_result = await check_provider_compatibility(
                    pv["id"], 
                    pv["version"],
                    db
                )
                results["providers"][pv["id"]] = provider_result
                
        if ansible_versions:
            for av in ansible_versions:
                ansible_result = await check_ansible_compatibility(
                    av["name"],
                    av["version"], 
                    db
                )
                results["ansible"][av["name"]] = ansible_result
                
        return results
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
