from functools import lru_cache
import json
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import find_dotenv, load_dotenv
from typing import Optional


load_dotenv(override=True)

class Settings(BaseSettings):


    EMBEDDINGS_MODEL_NAME: str
    OPENAI_API_KEY: str

    # Pinecone settings
    PINECONE_API_KEY: str
    PINECONE_KNOWLEDGE_BASE_INDEX: str


    # LANGCHAIN_TRACING_V2: str
    # LANGCHAIN_ENDPOINT: str
    # LANGCHAIN_API_KEY: str
    # LANGCHAIN_PROJECT: str

    
    # Optional settings
    ENVIRONMENT: Optional[str] = None
    DEBUG: bool = False

    
  
    class Config:
        env_file = ".env"
        case_sensitive = True

def get_envs_setting():
    return Settings()