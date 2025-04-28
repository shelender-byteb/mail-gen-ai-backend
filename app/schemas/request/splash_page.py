from typing import Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class ImageDetail(BaseModel):
    url: str
    alt: str

    class Config:
        extra = "ignore"


class GenerationRequest(BaseModel):
    id: Optional[str] = Field(
        None, 
        description="Required for update operations"
    )
    query: str
    style_type: str
    operation: str = "start_over"  # "start_over" or "update"
    previous_html: Optional[str] = None
    image_url: Optional[List[ImageDetail]] = None
    button_url: Optional[str] = ""
    @validator('id')
    def validate_id(cls, v, values):
        if values.get('operation') == 'update' and not v:
            raise ValueError('ID is required for update operations')
        return v


class Operation(str, Enum):
    EMAIL_GENERATION = "generate"
    EMAIL_REFINEMENT = "refine"

class EmailStyle(str, Enum):
    PROFESSIONAL_EMAIL = "professional"
    SALESY_EMAIL = "casual"




class EmailGenerationRequest(BaseModel):
    prompt: str
    website_url: str
    previous_email: Optional[str] = None
    operation: Operation
    email_style: EmailStyle
    image_urls: Optional[List[ImageDetail]] = None

    
    
# class GenerationRequest(BaseModel):
#     query: str
#     style_type: str
