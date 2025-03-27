from pydantic import BaseModel, Field
from enum import Enum

class ModelType(str, Enum):
    EMAIL = "email"
    SPLASH_PAGE = "splash_page"
    BANNER = "banner"


class ModelUpdateRequest(BaseModel):
    model_name: str = Field(..., description="The name of the model, e.g., 'gpt-4o'")
    temperature: float = Field(..., ge=0, le=1, description="Temperature value between 0 and 1")
