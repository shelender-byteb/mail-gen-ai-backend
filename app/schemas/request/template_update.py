from pydantic import BaseModel, Field
from enum import Enum

class TemplateType(str, Enum):
    CASUAL_EMAIL_GENERATION = "casual_email_generation"
    CASUAL_EMAIL_REFINEMENT = "casual_email_refinement"
    PROFESSIONAL_EMAIL_GENERATION = "professional_email_generation"
    PROFESSIONAL_EMAIL_REFINEMENT = "professional_email_refinement"
    SPLASH_PAGE = "splash_page"
    BANNER_GENERATION = "banner_generation"
    BANNER_REFINEMENT = "banner_refinement"
    BLURB_GENERATION = "blurb_generation"
    BLURB_REFINEMENT = "blurb_refinement"
    

class TemplateUpdateRequest(BaseModel):
    content: str = Field(..., description="The updated template content")
