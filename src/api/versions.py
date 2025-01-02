from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.db.models.ansible import AnsibleCollection
from src.utils.errors import DatabaseError, ValidationError

router = APIRouter(
    prefix="/versions",
    tags=["versions"]
)

@router.get("/collections/{collection_name}")
async def get_collection_versions(
    collection_name: str,
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Get version history for a specific Ansible collection.
    """
    try:
        versions = db.query(AnsibleCollection).filter(
            AnsibleCollection.name == collection_name
        ).order_by(AnsibleCollection.version.desc()).all()
        
        if not versions:
            raise HTTPException(
                status_code=404,
                detail=f"No versions found for collection {collection_name}"
            )
        return [version.to_dict() for version in versions]
    except HTTPException:
        raise
    except Exception as e:
        raise DatabaseError(
            f"Failed to get versions for collection {collection_name}: {str(e)}"
        )

@router.get("/collections/{collection_name}/latest")
async def get_latest_version(
    collection_name: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get the latest version of a specific Ansible collection.
    """
    try:
        latest = db.query(AnsibleCollection).filter(
            AnsibleCollection.name == collection_name
        ).order_by(AnsibleCollection.version.desc()).first()
        
        if not latest:
            raise HTTPException(
                status_code=404,
                detail=f"No versions found for collection {collection_name}"
            )
        return latest.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise DatabaseError(
            f"Failed to get latest version for collection {collection_name}: {str(e)}"
        )

@router.post("/collections/{collection_name}/versions")
async def add_collection_version(
    collection_name: str,
    version_data: dict,
    db: Session = Depends(get_db)
) -> dict:
    """
    Add a new version for an Ansible collection.
    """
    try:
        version_data["name"] = collection_name
        collection = AnsibleCollection(**version_data)
        db.add(collection)
        db.commit()
        db.refresh(collection)
        return collection.to_dict()
    except ValueError as e:
        raise ValidationError(f"Invalid version data: {str(e)}")
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Failed to add version: {str(e)}")
