from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.schemas.request.blurb_requests import PowerBlurbGenerationRequest, PowerBlurbGenerationResponse
from app.services.blurb_generator import generate_power_blurb
import logging

router = APIRouter(
    prefix="/v1/powerblurb",
    tags=["PowerBlurbs"],
    responses={404: {"description": "Not found"}},
)

@router.post("/generate", status_code=status.HTTP_200_OK, response_model=PowerBlurbGenerationResponse)
async def generate_power_blurb_endpoint(
    data: PowerBlurbGenerationRequest,
):
    """
    Generate or refine a PowerBlurb advertisement by scraping a website and using AI.
    """
    logging.info(f"PowerBlurb generation request received: {data.prompt[:50]}...")
    
    try:
        blurb_content = await generate_power_blurb(
            prompt=data.prompt,
            website_url=data.website_url,
            operation=data.operation,
            previous_blurb=data.previous_blurb
        )

        logging.info(f"PowerBlurb generation successful:\n\n\n")

        return PowerBlurbGenerationResponse(html=blurb_content)
        
        # return JSONResponse(
        #     content={"html": blurb_content},
        #     headers={"Content-Type": "application/json; charset=utf-8"}
        # )
        
    except Exception as e:
        logging.error(f"PowerBlurb generation API error: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"PowerBlurb generation failed: {str(e)}"
            )
