from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from app.schemas.request.banner import BannerGenerationRequest
from app.services.banner_generator import generate_banner

import logging

router = APIRouter(
    prefix="/v1/banner",
    tags=["Banner Generation"],
    responses={404: {"description": "Not found"}},
)

@router.post("/generate", status_code=status.HTTP_200_OK)
async def generate_banner_endpoint(data: BannerGenerationRequest):
    """
    Generate or refine an AI banner.
    """
    try:
        banner_html = await generate_banner(
            prompt=data.user_prompt,
            operation=data.operation,
            website_url=data.website_url,
            previous_banner=data.previous_banner
        )
    
        logging.info(f"Banner generation successful:\n{banner_html}\n\n")
        
        return JSONResponse(
            content={"html": banner_html},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
    except Exception as e:
        logging.error(f"Banner generation API error: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Email generation failed: {str(e)}"
            )
    