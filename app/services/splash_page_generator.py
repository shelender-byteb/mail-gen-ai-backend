import json, uuid
import time
import logging
import re
from typing import Optional

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException,status, BackgroundTasks
from fastapi.responses import JSONResponse


from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

# from app.utils.langchain_helper import _simple_prompt_assistant, construct_kb_chain, _load_last_10_messages

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

from app.utils.prompt import prompt
from app.utils.website_scraper import scrape_website
from app.common.env_config import get_envs_setting
from app.schemas.request.splash_page import ImageDetail

# New imports for dynamic DB loading:
from app.common.database_config import get_async_db
from app.models.model_config import ModelConfig
from app.models.template import Template
from app.schemas.request.model_update import ModelType
from app.schemas.request.template_update import TemplateType

from app.utils.database_utils import load_model_config, load_system_template


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
    model_name='o4-mini'
)

async def generate_splash_page(
    query: str, 
    style_type: str, 
    session: AsyncSession,   
    operation: str = "start_over", 
    previous_html: Optional[str] = None,
    button_url: Optional[str] = "",
    image_urls: Optional[ImageDetail] = None,
) -> str:
    """Generate HTML code for a splash page using RAG and LLMs"""
    try:
        print(f"Query is {query}, style type is {style_type}, operation is {operation}")

        cfg = await load_model_config(ModelType.SPLASH_PAGE, session)
        SPLASH_SYSTEM_PROMPT = await load_system_template(TemplateType.SPLASH_PAGE, session)
        SPLASH_HUMAN_PROMPT = """
        User Query:
        Style Type: {style_type}
        Description: {user_input}
        Operation: {operation}
        Button URL: {button_url}
        Image URLs: {image_urls}

        Previous HTML: {previous_html}
        Website URL: {website_url}
        Scraped Content: {website_content}
        """

        # 2. Build prompt
        splash_db_prompt = ChatPromptTemplate.from_messages([
            ("system", SPLASH_SYSTEM_PROMPT),
            ("human", SPLASH_HUMAN_PROMPT)
        ])

        print(f"\nStarting prompt of splash is : {splash_db_prompt[:200]}\n\n")
        print(f"Ending prompt of splash is : {splash_db_prompt[-200:]}\n")

        if cfg.model_name == "o4-mini" or cfg.model_name == "o3-mini":
            dyn_llm = ChatOpenAI(model_name=cfg.model_name)
        else:
            dyn_llm = ChatOpenAI(model_name=cfg.model_name, temperature=cfg.temperature)
            
        chain = splash_db_prompt | dyn_llm
        # chain = prompt | llm

        website_data = ""
        if operation == "start_over":
            website_data = await scrape_website(button_url)
                
            if 'error' in website_data:
                logging.error(f"Website scraping error: {website_data['error']}")
                
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to scrape website: {website_data['error']}. Please check the URL and try again."
                )

        response = await chain.ainvoke({
            "style_type": style_type,
            "user_input": query,
            "operation": operation,
            "previous_html": previous_html or "",
            "button_url": button_url or "",
            "website_url": button_url or "",
            "website_content": website_data or "",
            "image_urls": image_urls or "",
        })
        
        print(f"\n\nResponse from chain is {response}\n")

        response = extract_pure_html(response.content)
        return response
    
        # return response.content
    
    except Exception as e:
        print(f"Generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate splash page: {str(e)}"
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
# from fastapi import HTTPException,status, BackgroundTasks
# from fastapi.responses import JSONResponse


# from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
# from langchain_core.prompts import ChatPromptTemplate

# from langchain_pinecone import PineconeVectorStore
# from pinecone import Pinecone

# # from app.utils.langchain_helper import _simple_prompt_assistant, construct_kb_chain, _load_last_10_messages

# from langchain_openai import ChatOpenAI
# from langchain_openai import OpenAIEmbeddings

# from app.utils.prompt import prompt
# from app.utils.website_scraper import scrape_website
# from app.common.env_config import get_envs_setting
# from app.schemas.request.splash_page import ImageDetail


# logging.basicConfig(level=logging.INFO)
# envs = get_envs_setting()

# embeddings = OpenAIEmbeddings(model=envs.EMBEDDINGS_MODEL_NAME)

# pinecone_client = Pinecone(api_key=envs.PINECONE_API_KEY)
# vectorstore = PineconeVectorStore(
#     index=pinecone_client.Index(envs.PINECONE_KNOWLEDGE_BASE_INDEX),
#     embedding=embeddings
# )


# # llm = ChatOpenAI(
# #     model_name='gpt-4o',
# #     temperature=0.5
# # )

# llm = ChatOpenAI(
#     model_name='o4-mini'
# )

# async def generate_splash_page(
#     query: str, 
#     style_type: str, 
#     operation: str = "start_over", 
#     previous_html: Optional[str] = None,
#     button_url: Optional[str] = "",
#     image_urls: Optional[ImageDetail] = None
# ) -> str:
#     """Generate HTML code for a splash page using RAG and LLMs"""
#     try:
#         print(f"Query is {query}, style type is {style_type}, operation is {operation}")
        
#         # Add button_url and operation parameters to the invoke
#         chain = prompt | llm

#         website_data = ""
#         if operation == "start_over":
#             website_data = await scrape_website(button_url)
                
#             if 'error' in website_data:
#                 logging.error(f"Website scraping error: {website_data['error']}")
                
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail=f"Failed to scrape website: {website_data['error']}. Please check the URL and try again."
#                 )

#         response = await chain.ainvoke({
#             "style_type": style_type,
#             "user_input": query,
#             "operation": operation,
#             "previous_html": previous_html or "",
#             "button_url": button_url or "",
#             "website_url": button_url or "",
#             "website_content": website_data or "",
#             "image_urls": image_urls or "",
#         })
        
#         print(f"\n\nResponse from chain is {response}\n")

#         response = extract_pure_html(response.content)
#         return response
    
#         # return response.content
    
#     except Exception as e:
#         print(f"Generation failed: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to generate splash page: {str(e)}"
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


