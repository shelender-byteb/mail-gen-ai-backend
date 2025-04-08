import uuid
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, status, Request
from fastapi import BackgroundTasks, HTTPException
from app.schemas.response.splash_page import SplashPageResponse


from app.schemas.response.splash_page import ChatbotResponse, GetMessagesResponse
from app.schemas.request.splash_page import UserChat, GenerationRequest
from app.common import database_config
from app.services import splash_page_generator
from app.common.env_config import get_envs_setting
from app.models.splash_page import SplashPage
import logging
logging.basicConfig(level=logging.INFO)


settings = get_envs_setting()

router = APIRouter(
    prefix="/v1/splash-page",
    tags=["Splash Page"],
    responses={404: {"description": "Not found"}},
)


@router.post("/generate", status_code=status.HTTP_200_OK)
async def generate_html_page(
    data: GenerationRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(database_config.get_async_db)
):
    """
    Generate a splash page HTML based on description and style type.
    """
    print(f"Route hit...")

    id = data.id
    query = data.query
    style_type = data.style_type
    operation = data.operation
    previous_html = data.previous_html
    button_url = data.button_url

    if style_type not in ["professional", "casual"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid style type. Use 'professional' or 'casual'"
        )
    
    if operation not in ["start_over", "update"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid operation. Use 'start_over' or 'update'"
        )

    if operation == "update" and not previous_html:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Previous HTML required for update operation"
        )
    if operation == "update" and not id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Id required for update operation"
        )

    try:
        html_content = await splash_page_generator.generate_splash_page(
            query, 
            style_type, 
            operation, 
            previous_html,
            button_url
        )
            # Create new splash page record
        if data.operation == "update":
            # Update existing record
            existing_page = await session.get(SplashPage, data.id)
            if not existing_page:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Splash page not found"
                )
                
            existing_page.html_content = html_content
            if data.button_url:  # Only update if provided
                existing_page.button_url = button_url
            page_id = existing_page.id
            print('page_id old is: ',page_id)
        else:
            # Create new record
            new_page = SplashPage(
                html_content=html_content,
                button_url=button_url
            )
            session.add(new_page)
            await session.flush() 
            page_id = new_page.id
            print('page_id new is: ',page_id)


        print("Database commit processing...")
        await session.commit()
        print("Database commit successful")
        
        return JSONResponse(
            content={
                "html": html_content,
                "id": page_id,
                "operation": operation
            }
        )
    
    except Exception as e:
        await session.rollback()
        print(f"API Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    
@router.get("/{page_id}", response_model=SplashPageResponse)
def get_splash_page(
    page_id: str, 
    session: Session = Depends(database_config.get_db)
):
    splash_page = session.get(SplashPage, page_id)
    if not splash_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Splash page not found"
        )
    return splash_page



# @router.post("/splash-generate", status_code=status.HTTP_200_OK)
# async def generate_html_page(
#     data: GenerationRequest,
#     background_tasks: BackgroundTasks,
#     # session: Session = Depends(database_config.get_async_db)
# ):
#     """
#     Generate a splash page HTML based on description and style type.
#     """

#     print(f"Route hit...")

#     query = data.query
#     style_type = data.style_type

#     if style_type not in ["professional", "casual"]:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid style type. Use 'professional' or 'casual'"
#         )

#     try:
#         html_content = await user_chat.generate_splash_page(query, style_type)
#         return JSONResponse(
#             content={"html": html_content},
#             headers={"Content-Type": "application/json; charset=utf-8"}
#         )

#     except Exception as e:
#         print(f"API Error: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Internal server error"
#         )



