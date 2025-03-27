import json
import logging
from typing import List, Optional
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


from app.common.env_config import get_envs_setting
from app.schemas.request.autocomplete import ServiceType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

envs = get_envs_setting()

autocomplete_llm = ChatOpenAI(
    model_name="gpt-4o",
    temperature=0.2
)

SPLASH_PAGE_PROMPT = """
You are an autocomplete system for a splash page generation service.
Based on the partial text the user has typed so far, predict how they would likely complete their request.

Style type: {style_type}
Partial user input: {query}

Your goal is to complete their thought with a SINGLE most likely completion, not multiple options.
The user is typing a request to generate a splash page, and you should provide the most probable direct completion of what they're typing.

IMPORTANT: Return ONLY ONE completion, not multiple options.

Keep the completion natural and focused on how the user would most likely finish their current thought.
"""

EMAIL_PROMPT = """
You are an autocomplete system for an email marketing generation service.
Based on what the user has typed so far, predict the SINGLE most likely completion.

Partial user input: {query}

Your task is to complete their current text input naturally with the most probable continuation.
The user is typing a request to generate a marketing email, and you should predict how they would finish typing.

IMPORTANT: Return ONLY ONE completion that is most likely, not multiple options.

Focus on a natural completion that follows directly from what the user has already typed.
"""

BANNER_PROMPT = """
You are an autocomplete system for a banner ad generation service.
Based on what the user has typed so far, predict the SINGLE most likely completion.

Partial user input: {query}

Provide ONE natural completion that directly continues the user's partial input.
The user is typing a request to generate a banner ad, and you should predict the most probable way they would complete it.

IMPORTANT: Return ONLY ONE completion that is most likely, not multiple options.

Focus on completing the user's current thought with the most probable continuation.
"""


class StructuredFormat(BaseModel):
    completion: str = Field(description="Single autocomplete suggestion for user")

async def get_autocomplete_suggestions(
    query: str,
    service_type: ServiceType,
    style_type: Optional[str] = None
) -> str:
    """
    Generate autocomplete suggestion based on partial user input and service type.
    
    Args:
        query: Partial user input
        service_type: Flag indicating service (0=splash, 1=email, 2=banner)
        style_type: Style type for splash pages (professional/casual)
        
    Returns:
        Single string completion
    """
    # Make sure we have a query
    if not query.strip():
        return ""
    
    try:
        # Select prompt based on service type
        if service_type == ServiceType.SPLASH_PAGE:
            # Default to professional if not specified
            current_style = style_type or "professional"
            if current_style not in ["professional", "casual"]:
                current_style = "professional"
                
            prompt_template = ChatPromptTemplate.from_template(SPLASH_PAGE_PROMPT)
            prompt_vars = {"query": query, "style_type": current_style}
            
        elif service_type == ServiceType.EMAIL:
            prompt_template = ChatPromptTemplate.from_template(EMAIL_PROMPT)
            prompt_vars = {"query": query}
            
        elif service_type == ServiceType.BANNER:
            prompt_template = ChatPromptTemplate.from_template(BANNER_PROMPT)
            prompt_vars = {"query": query}
            
        else:
            logger.error(f"Invalid service type: {service_type}")
            return ""
        
        # Generate suggestion using structured output
        chain = prompt_template | autocomplete_llm.with_structured_output(StructuredFormat)
        response = await chain.ainvoke(prompt_vars)
        
        logger.info(f"\nLLM response: {response}\n")
        
        # Extract the completion
        completion = response.completion
        
        return completion
        
    except Exception as e:
        logger.error(f"Error generating autocomplete suggestion: {str(e)}")
        return ""

def parse_llm_response(content: str) -> List[str]:
    """
    Parse the LLM response and extract completions.
    Handles different formats the LLM might return.
    """
    try:
        # Extract JSON if it's embedded in text (with markdown code blocks)
        if "```json" in content:
            json_content = content.split("```json")[1].split("```")[0].strip()
            completions = json.loads(json_content)
        elif "```" in content:
            # Handle case where json is in code block without language specification
            json_content = content.split("```")[1].split("```")[0].strip()
            completions = json.loads(json_content)
        else:
            # Direct JSON parsing
            completions = json.loads(content)
        
        # Ensure we have a list of strings
        if isinstance(completions, list):
            # Handle both string arrays and object arrays
            result = []
            for item in completions:
                if isinstance(item, str):
                    result.append(item)
                elif isinstance(item, dict) and "text" in item:
                    result.append(item["text"])
            return result[:5]  # Limit to 5 completions
        
        return []
    except Exception as e:
        logger.error(f"Failed to parse completions from LLM response: {str(e)}")
        logger.debug(f"Raw content: {content}")
        return []