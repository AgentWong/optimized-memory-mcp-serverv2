from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.db.models.providers import Provider
from src.utils.errors import DatabaseError, ValidationError

router = APIRouter(
    prefix="/providers",
    tags=["providers"]
)

@router.get("/")
async def list_providers(
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    List all registered infrastructure providers.
    """
    try:
        providers = db.query(Provider).all()
        return [provider.to_dict() for provider in providers]
    except Exception as e:
        raise DatabaseError(f"Failed to list providers: {str(e)}")

@router.get("/{provider_id}")
async def get_provider(
    provider_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get details for a specific provider by ID.
    """
    try:
        provider = db.query(Provider).filter(Provider.id == provider_id).first()
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        return provider.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to get provider {provider_id}: {str(e)}")

@router.post("/")
async def create_provider(
    provider_data: dict,
    db: Session = Depends(get_db)
) -> dict:
    """
    Register a new infrastructure provider.
    """
    try:
        provider = Provider(**provider_data)
        db.add(provider)
        db.commit()
        db.refresh(provider)
        return provider.to_dict()
    except ValueError as e:
        raise ValidationError(f"Invalid provider data: {str(e)}")
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Failed to create provider: {str(e)}")

@router.put("/{provider_id}")
async def update_provider(
    provider_id: int,
    provider_data: dict,
    db: Session = Depends(get_db)
) -> dict:
    """
    Update an existing provider's details.
    """
    try:
        provider = db.query(Provider).filter(Provider.id == provider_id).first()
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
            
        for key, value in provider_data.items():
            setattr(provider, key, value)
            
        db.commit()
        db.refresh(provider)
        return provider.to_dict()
    except HTTPException:
        raise
    except ValueError as e:
        raise ValidationError(f"Invalid provider data: {str(e)}")
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Failed to update provider {provider_id}: {str(e)}")

@router.delete("/{provider_id}")
async def delete_provider(
    provider_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete a provider registration.
    """
    try:
        provider = db.query(Provider).filter(Provider.id == provider_id).first()
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
            
        db.delete(provider)
        db.commit()
        return {"message": f"Provider {provider_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Failed to delete provider {provider_id}: {str(e)}")
