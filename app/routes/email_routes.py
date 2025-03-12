# app/routes/email_routes.py
from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from app.schemas.request.user_chat import EmailGenerationRequest
from app.services.email_generator import generate_email_advertisement
import logging

router = APIRouter(
    prefix="/v1/email",
    tags=["Email Generation"],
    responses={404: {"description": "Not found"}},
)

@router.post("/generate", status_code=status.HTTP_200_OK)
async def generate_email(
    data: EmailGenerationRequest,
    background_tasks: BackgroundTasks,
):
    """
    Generate or refine an email advertisement by scraping a website and using AI.
    """
    logging.info(f"Email generation request received: {data.prompt[:50]}...")
    
    try:
        email_content = await generate_email_advertisement(
            prompt=data.prompt,
            website_url=data.website_url,
            operation=data.operation,
            previous_email=data.previous_email
        )
        
        return JSONResponse(
            content={"email": email_content},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
    except Exception as e:
        logging.error(f"Email generation API error: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Email generation failed: {str(e)}"
            )