from app.common.database_config import get_async_db
from app.schemas.request.model_update import ModelType
from app.schemas.request.template_update import TemplateType


from app.models.model_config import ModelConfig
from app.models.template import Template

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException,status, BackgroundTasks


async def load_system_template(template_type: TemplateType, session: AsyncSession) -> str:
    # print(f"Template type is {template_type}")
       
    # 2. Fetch the splash page template using the TemplateType enum.
    result = await session.execute(
        select(Template).where(Template.template_type == template_type.value)
    )
    template = result.scalars().first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No system template found"
        )
    return template.content
    


async def load_model_config(model_type: ModelType, session: AsyncSession) -> ModelConfig:
    """
    Fetches the model configuration (name + temperature) for the given model_type.
    """
    # print(f"Model type is {model_type}")
        
    result = await session.execute(
        select(ModelConfig).where(ModelConfig.model_type == model_type.value)
    )
    cfg = result.scalars().first()
    if not cfg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No model configuration found for {model_type}"
        )
    return cfg