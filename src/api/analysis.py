"""
Version analysis endpoints for the MCP API.
Provides analysis of version compatibility and changes across resources.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.db.models.providers import Provider
from src.db.models.ansible import AnsibleCollection
from src.utils.errors import ValidationError

router = APIRouter(tags=["analysis"])

@router.get("/providers/{provider_id}/analysis")
async def analyze_provider_versions(
    provider_id: int,
    from_version: str,
    to_version: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Analyze changes between two versions of a provider.
    
    Args:
        provider_id: ID of the provider to analyze
        from_version: Starting version for analysis
        to_version: Ending version for analysis
        
    Returns:
        Dict containing analysis of changes between versions
    """
    try:
        provider = db.query(Provider).filter(Provider.id == provider_id).first()
        if not provider:
            raise ValidationError("Provider not found", {"provider_id": provider_id})
            
        analysis = {
            "breaking_changes": [],
            "new_features": [],
            "deprecations": [],
            "security_updates": []
        }
        
        # Add version analysis logic here
        # For now returning empty analysis structure
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/ansible/{collection_name}/analysis")
async def analyze_collection_versions(
    collection_name: str,
    from_version: str,
    to_version: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Analyze changes between two versions of an Ansible collection.
    
    Args:
        collection_name: Name of the collection to analyze
        from_version: Starting version for analysis
        to_version: Ending version for analysis
        
    Returns:
        Dict containing analysis of changes between versions
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
            
        analysis = {
            "breaking_changes": [],
            "new_features": [],
            "deprecations": [],
            "security_updates": []
        }
        
        # Add version analysis logic here
        # For now returning empty analysis structure
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/batch-analysis")
async def analyze_multiple_versions(
    provider_versions: Optional[List[dict]] = None,
    ansible_versions: Optional[List[dict]] = None,
    db: Session = Depends(get_db)
) -> dict:
    """
    Batch analyze version changes for multiple providers and collections.
    
    Args:
        provider_versions: List of provider IDs and version pairs to analyze
        ansible_versions: List of collection names and version pairs to analyze
        
    Returns:
        Dict containing analysis results for all requested items
    """
    results = {
        "providers": {},
        "ansible": {},
        "summary": {
            "total_breaking_changes": 0,
            "total_deprecations": 0
        }
    }
    
    try:
        if provider_versions:
            for pv in provider_versions:
                provider_result = await analyze_provider_versions(
                    pv["id"],
                    pv["from_version"],
                    pv["to_version"],
                    db
                )
                results["providers"][pv["id"]] = provider_result
                
        if ansible_versions:
            for av in ansible_versions:
                ansible_result = await analyze_collection_versions(
                    av["name"],
                    av["from_version"],
                    av["to_version"],
                    db
                )
                results["ansible"][av["name"]] = ansible_result
                
        return results
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
