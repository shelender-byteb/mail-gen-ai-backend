import json, uuid
import time
import logging
import re
from typing import Optional

from sqlalchemy.future import select
from fastapi import HTTPException,status, BackgroundTasks
from fastapi.responses import JSONResponse


from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

# from app.utils.langchain_helper import _simple_prompt_assistant, construct_kb_chain, _load_last_10_messages

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

from app.utils.prompt import PROMPT_TEMPLATE, prompt
from app.common.env_config import get_envs_setting


logging.basicConfig(level=logging.INFO)
envs = get_envs_setting()

embeddings = OpenAIEmbeddings(model=envs.EMBEDDINGS_MODEL_NAME)

pinecone_client = Pinecone(api_key=envs.PINECONE_API_KEY)
vectorstore = PineconeVectorStore(
    index=pinecone_client.Index(envs.PINECONE_KNOWLEDGE_BASE_INDEX),
    embedding=embeddings
)


# llm = ChatOpenAI(
#     model_name='gpt-4o',
#     temperature=0.5
# )

llm = ChatOpenAI(
    model_name='o3-mini'
)

async def generate_splash_page(
    query: str, 
    style_type: str, 
    operation: str = "start_over", 
    previous_html: Optional[str] = None,
    button_url: Optional[str] = ""
) -> str:
    """Generate HTML code for a splash page using RAG and LLMs"""
    try:
        print(f"Query is {query}, style type is {style_type}, operation is {operation}")
        
        # Add button_url and operation parameters to the invoke
        chain = prompt | llm

        response = await chain.ainvoke({
            "style_type": style_type,
            "user_input": query,
            "operation": operation,
            "previous_html": previous_html or "",
            "button_url": button_url or "",
        })
        
        print(f"\n\nResponse from chain is {response}\n")

        response = extract_pure_html(response.content)
        return response
    
        # return response.content
    
    except Exception as e:
        print(f"Generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate splash page"
        )

def extract_pure_html(response_content: str) -> str:
    # Regex to find content between <!DOCTYPE html> and </html>
    html_match = re.search(r'(<!DOCTYPE html>.*?</html>)', response_content, re.DOTALL | re.IGNORECASE)
    if html_match:
        logging.info("Extracted pure HTML")
        return html_match.group(1)

    else:
        logging.warning(f"Could not extract pure HTML. Full response: {response_content}")
        return response_content














# import json, uuid
# import time
# import logging
# import re
# from typing import Optional

# from sqlalchemy.future import select
# from fastapi import HTTPException, status, BackgroundTasks
# from fastapi.responses import JSONResponse

# from langchain_openai import OpenAIEmbeddings
# from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_pinecone import PineconeVectorStore
# from pinecone import Pinecone

# from app.common.env_config import get_envs_setting
# from langchain_openai import ChatOpenAI

# # Removed hard-coded prompt imports
# # from app.utils.prompt import PROMPT_TEMPLATE, prompt

# # New imports for dynamic DB loading:
# from app.common.database_config import get_async_db
# from app.models.model_config import ModelConfig
# from app.models.template import Template
# from app.enums.model_type import ModelType
# from app.enums.template_type import TemplateType

# logging.basicConfig(level=logging.INFO)
# envs = get_envs_setting()

# embeddings = OpenAIEmbeddings(model=envs.EMBEDDINGS_MODEL_NAME)

# pinecone_client = Pinecone(api_key=envs.PINECONE_API_KEY)
# vectorstore = PineconeVectorStore(
#     index=pinecone_client.Index(envs.PINECONE_KNOWLEDGE_BASE_INDEX),
#     embedding=embeddings
# )

# async def generate_splash_page(
#     query: str, 
#     style_type: str, 
#     operation: str = "start_over", 
#     previous_html: Optional[str] = None,
#     button_url: Optional[str] = ""
# ) -> str:
#     """Generate HTML code for a splash page using RAG and LLMs.
#        Dynamically loads the LLM configuration and splash page template from the DB.
#     """
#     try:
#         print(f"Query is {query}, style type is {style_type}, operation is {operation}")
        
#         async with get_async_db() as session:
#             # 1. Fetch the splash page model configuration from DB using the ModelType enum.
#             result = await session.execute(
#                 select(ModelConfig).where(ModelConfig.model_type == ModelType.SPLASH_PAGE.value)
#             )
#             splash_model_config = result.scalars().first()
#             if not splash_model_config:
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail="No model configuration found for splash_page"
#                 )
#             dynamic_llm = ChatOpenAI(
#                 model_name=splash_model_config.model_name,
#                 temperature=splash_model_config.temperature
#             )
            
#             # 2. Fetch the splash page template using the TemplateType enum.
#             result = await session.execute(
#                 select(Template).where(Template.template_type == TemplateType.SPLASH_PAGE.value)
#             )
#             splash_template = result.scalars().first()
#             if not splash_template:
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail="No splash page template found"
#                 )
#             dynamic_prompt = ChatPromptTemplate.from_template(splash_template.content)
            
#             # 3. Create a chain with the dynamically loaded prompt and LLM.
#             chain = dynamic_prompt | dynamic_llm

#             # 4. Prepare parameters for the chain invocation.
#             chain_params = {
#                 "style_type": style_type,
#                 "user_input": query,
#                 "operation": operation,
#                 "previous_html": previous_html or "",
#                 "button_url": button_url or "",
#             }
            
#             response = await chain.ainvoke(chain_params)
        
#         print(f"\n\nResponse from chain is {response}\n")
#         response_content = extract_pure_html(response.content)
#         return response_content
    
#     except Exception as e:
#         print(f"Generation failed: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to generate splash page"
#         )

# def extract_pure_html(response_content: str) -> str:
#     # Regex to find content between <!DOCTYPE html> and </html>
#     html_match = re.search(r'(<!DOCTYPE html>.*?</html>)', response_content, re.DOTALL | re.IGNORECASE)
#     if html_match:
#         logging.info("Extracted pure HTML")
#         return html_match.group(1)
#     else:
#         logging.warning(f"Could not extract pure HTML. Full response: {response_content}")
#         return response_content

