from pydantic import BaseModel, Field
from enum import Enum

class TemplateType(str, Enum):
    EMAIL_GENERATION = "email_generation"
    EMAIL_REFINEMENT = "email_refinement"
    SPLASH_PAGE = "splash_page"
    BANNER = "banner"

class TemplateUpdateRequest(BaseModel):
    content: str = Field(..., description="The updated template content")
