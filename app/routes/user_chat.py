import uuid
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, status, Request
from fastapi import BackgroundTasks, HTTPException

from app.schemas.response.user_chat import ChatbotResponse, GetMessagesResponse
from app.schemas.request.user_chat import UserChat, GenerationRequest
# from app.common import database_config
from app.services import user_chat
from app.common.env_config import get_envs_setting



settings = get_envs_setting()

router = APIRouter(
    prefix="/v1/chat",
    tags=["Chat"],
    responses={404: {"description": "Not found"}},
)


@router.post("/splash-generate", status_code=status.HTTP_200_OK)
async def generate_html_page(
    data: GenerationRequest,
    background_tasks: BackgroundTasks,
    # session: Session = Depends(database_config.get_async_db)
):
    """
    Generate a splash page HTML based on description and style type.
    """

    print(f"Route hit...")

    query = data.query
    style_type = data.style_type

    if style_type not in ["professional", "casual"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid style type. Use 'professional' or 'casual'"
        )

    try:
        html_content = await user_chat.generate_splash_page(query, style_type)
        return JSONResponse(
            content={"html": html_content},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )

    except Exception as e:
        print(f"API Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )



