from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.db.models.ansible import AnsibleCollection
from src.db.models.parameters import ModuleParameter
from src.utils.errors import DatabaseError, ValidationError

router = APIRouter(
    prefix="/ansible",
    tags=["ansible"]
)

@router.get("/collections")
async def list_collections(
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    List all registered Ansible collections.
    """
    try:
        collections = db.query(AnsibleCollection).all()
        return [collection.to_dict() for collection in collections]
    except Exception as e:
        raise DatabaseError(f"Failed to list collections: {str(e)}")

@router.get("/collections/{collection_id}")
async def get_collection(
    collection_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get details for a specific Ansible collection by ID.
    """
    try:
        collection = db.query(AnsibleCollection).filter(
            AnsibleCollection.id == collection_id
        ).first()
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")
        return collection.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to get collection {collection_id}: {str(e)}")

@router.post("/collections")
async def create_collection(
    collection_data: dict,
    db: Session = Depends(get_db)
) -> dict:
    """
    Register a new Ansible collection.
    """
    try:
        collection = AnsibleCollection(**collection_data)
        db.add(collection)
        db.commit()
        db.refresh(collection)
        return collection.to_dict()
    except ValueError as e:
        raise ValidationError(f"Invalid collection data: {str(e)}")
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Failed to create collection: {str(e)}")

@router.get("/parameters/{module_name}")
async def get_module_parameters(
    module_name: str,
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Get parameters for a specific Ansible module.
    """
    try:
        parameters = db.query(ModuleParameter).filter(
            ModuleParameter.module_name == module_name
        ).all()
        if not parameters:
            raise HTTPException(
                status_code=404,
                detail=f"No parameters found for module {module_name}"
            )
        return [param.to_dict() for param in parameters]
    except HTTPException:
        raise
    except Exception as e:
        raise DatabaseError(
            f"Failed to get parameters for module {module_name}: {str(e)}"
        )

@router.post("/parameters/{module_name}")
async def create_module_parameter(
    module_name: str,
    parameter_data: dict,
    db: Session = Depends(get_db)
) -> dict:
    """
    Create a new parameter for an Ansible module.
    """
    try:
        parameter_data["module_name"] = module_name
        parameter = ModuleParameter(**parameter_data)
        db.add(parameter)
        db.commit()
        db.refresh(parameter)
        return parameter.to_dict()
    except ValueError as e:
        raise ValidationError(f"Invalid parameter data: {str(e)}")
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Failed to create parameter: {str(e)}")
