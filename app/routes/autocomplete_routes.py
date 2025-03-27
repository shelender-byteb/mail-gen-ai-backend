from fastapi import APIRouter, Query, HTTPException, status
import logging

from app.schemas.request.autocomplete import (
    AutocompleteRequest,
    AutocompleteResponse,
    ServiceType
)
from app.services.auto_completion import get_autocomplete_suggestions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/v1/autocomplete",
    tags=["Autocomplete"],
    responses={404: {"description": "Not found"}},
)
@router.post("/generate", response_model=AutocompleteResponse)
async def autocomplete(
    data: AutocompleteRequest
):
    """
    Generate autocomplete completion for partial user input.
    
    - service_type: 0=splash page, 1=email, 2=banner
    - style_type: Only used for splash pages (professional/casual)
    """
    try:
        # Validate service type
        if data.service_type not in [0, 1, 2]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid service type. Use 0 for splash page, 1 for email, or 2 for banner."
            )
        
        # Convert to enum
        service_enum = ServiceType(data.service_type)
        
        logger.info(f"Autocomplete request: service={service_enum}, query='{data.query[:20]}...'")
        
        completion = await get_autocomplete_suggestions(
            query=data.query,
            service_type=service_enum,
            style_type=data.style_type
        )
        
        return AutocompleteResponse(completion=completion)
    
    except Exception as e:
        logger.error(f"Autocomplete error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Autocomplete failed: {str(e)}"
        )