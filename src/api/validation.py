from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.db.models.parameters import ModuleParameter
from src.utils.errors import DatabaseError, ValidationError

router = APIRouter(
    prefix="/validation",
    tags=["validation"]
)

@router.post("/parameters/validate")
async def validate_module_parameters(
    module_name: str,
    parameters: dict,
    db: Session = Depends(get_db)
) -> dict:
    """
    Validate parameters against module schema.
    """
    try:
        # Get module parameter definitions
        param_defs = db.query(ModuleParameter).filter(
            ModuleParameter.module_name == module_name
        ).all()
        
        if not param_defs:
            raise HTTPException(
                status_code=404,
                detail=f"No parameter definitions found for module {module_name}"
            )
            
        validation_errors = []
        
        # Validate required parameters
        for param in param_defs:
            if param.required and param.name not in parameters:
                validation_errors.append(
                    f"Missing required parameter: {param.name}"
                )
                
        # Validate parameter types and values
        for name, value in parameters.items():
            param_def = next(
                (p for p in param_defs if p.name == name),
                None
            )
            
            if not param_def:
                validation_errors.append(f"Unknown parameter: {name}")
                continue
                
            # Type validation could be expanded based on parameter types
            if not isinstance(value, eval(param_def.type)):
                validation_errors.append(
                    f"Invalid type for {name}: expected {param_def.type}"
                )
                
        if validation_errors:
            return {
                "valid": False,
                "errors": validation_errors
            }
            
        return {
            "valid": True,
            "errors": []
        }
    except HTTPException:
        raise
    except Exception as e:
        raise DatabaseError(
            f"Failed to validate parameters for module {module_name}: {str(e)}"
        )

@router.get("/schema/{module_name}")
async def get_module_schema(
    module_name: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get the parameter schema for a module.
    """
    try:
        parameters = db.query(ModuleParameter).filter(
            ModuleParameter.module_name == module_name
        ).all()
        
        if not parameters:
            raise HTTPException(
                status_code=404,
                detail=f"No schema found for module {module_name}"
            )
            
        return {
            "module": module_name,
            "parameters": [param.to_dict() for param in parameters]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise DatabaseError(
            f"Failed to get schema for module {module_name}: {str(e)}"
        )
