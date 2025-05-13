from app.common.database_config import get_async_db
from app.schemas.request.model_update import ModelType
from app.schemas.request.template_update import TemplateType


from app.models.model_config import ModelConfig
from app.models.template import Template

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException,status, BackgroundTasks

import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_deepseek import ChatDeepSeek


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



def get_llm(provider: str, model_name: str, temperature: float):
    """
    Return a LangChain ChatModel for the given provider.
    provider: "openai", "anthropic", or "deepseek"
    """
    if provider.lower() == "anthropic":
        # Claude via langchain-anthropic
        # temperature is supported by ChatAnthropic
        return ChatAnthropic(model=model_name, temperature=temperature)

    elif provider.lower() == "deepseek":
        # Option A: Native DeepSeek client
        return ChatDeepSeek(
            model=model_name,
            temperature=temperature,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        # Option B: DeepSeek via OpenRouter (OpenAI-compatible)
        # return ChatOpenAI(
        #     model_name=model_name,
        #     temperature=temperature,
        #     openai_api_base=os.getenv("DEEPSEEK_API_URL"),
        #     openai_api_key=os.getenv("DEEPSEEK_API_KEY")
        # )

    else:
        # OpenAI via langchain_openai
        # apply your no-temp override for o4-mini / o3-mini
        if model_name in ("o4-mini", "o3-mini"):
            return ChatOpenAI(model_name=model_name)
        return ChatOpenAI(model_name=model_name, temperature=temperature)