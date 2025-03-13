from typing import Optional
from pydantic import BaseModel, Field, validator

class UserChat(BaseModel):
    id: int
    question: str



class GenerationRequest(BaseModel):
    id: Optional[str] = Field(
        None, 
        description="Required for update operations"
    )
    query: str
    style_type: str
    operation: str = "start_over"  # "start_over" or "update"
    previous_html: Optional[str] = None
    button_url: Optional[str] = ""
    @validator('id')
    def validate_id(cls, v, values):
        if values.get('operation') == 'update' and not v:
            raise ValueError('ID is required for update operations')
        return v


class EmailGenerationRequest(BaseModel):
    prompt: str
    website_url: str
    previous_email: Optional[str] = None
    operation: str = "generate"  # "generate" or "refine"
    
    
# class GenerationRequest(BaseModel):
#     query: str
#     style_type: str
