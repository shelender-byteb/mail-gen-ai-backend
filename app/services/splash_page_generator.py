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

from pydantic import BaseModel, Field

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

from app.utils.database_utils import load_model_config, load_system_template, get_llm

import random
LAST_EXAMPLE = random.randint(1, 5)


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

class ScrapeResult(BaseModel):
    summary: str = Field(..., description="2–3 paragraph summary of the page content")
    image_urls: list[str] = Field(..., description="All image URLs found on the page")


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
    global LAST_EXAMPLE
    try:
        print(f"Query is {query}, style type is {style_type}, operation is {operation}")

        # cfg = await load_model_config(ModelType.SPLASH_PAGE, session)
        # SPLASH_SYSTEM_PROMPT = await load_system_template(TemplateType.SPLASH_PAGE, session)
         # branch on style_type and load the matching system prompt
        cfg = await load_model_config(ModelType.SPLASH_PAGE, session)
        if style_type == "professional":
            SPLASH_SYSTEM_PROMPT = await load_system_template(
                TemplateType.SPLASH_PAGE_PROFESSIONAL, session
            )
        else:
            SPLASH_SYSTEM_PROMPT = await load_system_template(
                TemplateType.SPLASH_PAGE_CASUAL, session
            )

        SPLASH_HUMAN_PROMPT = """
        User Query:
        Description: {user_input}
        Operation: {operation}
        Button URL: {button_url}
        **User-Provided Images** (must embed each of these): {user_image_urls}
        Previous HTML: {previous_html}
        Website URL: {website_url}
        Website Context Summary (2–3 paragraphs): {website_content}
        """

        # **Optional Scraped Images** (for inspiration; include only if helpful): {scraped_image_urls}


        if style_type == "professional":
            while True:
                # Generate a random number between 1 and 5
                example_num = random.randint(1, 5)
                if example_num != LAST_EXAMPLE:
                    LAST_EXAMPLE = example_num
                    break

            SPLASH_HUMAN_PROMPT += f"""
            \nWARNING: You are currently generating splash pages that all use the exact same layout pattern. This is PROHIBITED. Each design must be structurally unique, not just varying in colors or minor styling.

            IMPORTANT INSTRUCTION: For this request, follow the structure and layout approach of Example {example_num} from the system prompt. Do not mix examples - use exactly the layout pattern from Example {example_num}.
            """
            # SPLASH_HUMAN_PROMPT += """
            # \nWARNING: You are currently generating splash pages that all use the exact same layout pattern. This is PROHIBITED. Each design must be structurally unique, not just varying in colors or minor styling.
            # Follow the examples provided in the system prompt for guidance. Pick the design of any example randomly
            # """

        # 2. Build prompt
        splash_db_prompt = ChatPromptTemplate.from_messages([
            ("system", SPLASH_SYSTEM_PROMPT),
            ("human", SPLASH_HUMAN_PROMPT)
        ])

        # print(f"\n\n\nStarting prompt of splash is : {splash_db_prompt}\n\n")

        print(f"Ending prompt of splash is : {splash_db_prompt[-200:]}\n")

        # if cfg.model_name == "o4-mini" or cfg.model_name == "o3-mini":
        #     dyn_llm = ChatOpenAI(model_name=cfg.model_name)
        # else:
        #     dyn_llm = ChatOpenAI(model_name=cfg.model_name, temperature=cfg.temperature)
        dyn_llm = get_llm(cfg.provider, cfg.model_name, cfg.temperature)
            
        chain = splash_db_prompt | dyn_llm
        # chain = prompt | llm

        website_data = ""
        if operation == "start_over":
            website_data = await scrape_website(button_url)

            print(f"\n\n\nWebisite data is {str(website_data)[:200]}\n\n\n")
                
            if 'error' in website_data:
                logging.error(f"Website scraping error: {website_data['error']}")
                
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to scrape website: {website_data['error']}. Please check the URL and try again."
                )
            # 2) preprocess the raw scraped content with a separate LLM chain
            SCRAPE_SYSTEM = """
            You are a specialist content-extraction assistant. You will be given raw HTML/text scraped from a website.  
            Your task is two-fold:

            1. Produce a **high-quality**, **well-structured** summary in **2–3 paragraphs** (each paragraph 2–4 sentences).  
            - Emphasize the site’s key messages, branding cues, tone and any calls-to-action.  
            - Think ahead: this summary will be used by another LLM to generate a complete splash page, so include every detail that could inform design, copy and imagery.

            2. Extract **every** image URL you find into a JSON list.

            **Output** exactly a JSON object with these two fields:
            ```json
            {{
            "summary": "Your 2–3 paragraph summary here…",
            "image_urls": ["https://…", "https://…", …]
            }}
            """
            SCRAPE_HUMAN = "Raw content:\n{raw_content}"

            scrape_prompt = ChatPromptTemplate.from_messages([
                ("system", SCRAPE_SYSTEM),
                ("human", SCRAPE_HUMAN)
            ])

            autocomplete_llm = ChatOpenAI(model_name="o4-mini")
            structured_llm = autocomplete_llm.with_structured_output(ScrapeResult)

            pre_chain = scrape_prompt | structured_llm

            pre_resp = await pre_chain.ainvoke({
                "raw_content": website_data.get("content","")
            })
            # parse the JSON out
            processed_content    = pre_resp.summary
            extracted_image_urls = pre_resp.image_urls

            print(f"\n\n\nProcessed content is {processed_content}\n\n\n")
            print(f"\n\n\nExtracted image urls are {extracted_image_urls}\n\n\n")
        else:
            processed_content    = ""
            extracted_image_urls = []

        response = await chain.ainvoke({
            "user_input": query,
            "operation": operation,
            "previous_html": previous_html or "",
            "button_url": button_url or "",
            "website_url": button_url or "",
            "website_content": processed_content,
            "user_image_urls": image_urls,
            # "scraped_image_urls": "\n".join(extracted_image_urls)
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










