from pydantic import BaseModel, Field
from enum import Enum

class ModelType(str, Enum):
    CASUAL_EMAIL = "casual_email"
    PROFESSIONAL_EMAIL = "professional_email"
    SPLASH_PAGE = "splash_page"
    BANNER = "banner"
    BLURB = "blurb"


class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"

class ModelUpdateRequest(BaseModel):
    model_name: str = Field(..., description="The name of the model, e.g., 'gpt-4o'")
    temperature: float = Field(..., ge=0, le=1, description="Temperature value between 0 and 1")
    provider: LLMProvider = Field(LLMProvider.OPENAI, description="LLM provider to use")