from typing import Optional
from pydantic import BaseModel

class UserChat(BaseModel):
    id: int
    question: str



class GenerationRequest(BaseModel):
    query: str
    style_type: str
    operation: str = "start_over"  # "start_over" or "update"
    previous_html: Optional[str] = None
    button_url: Optional[str] = ""


class EmailGenerationRequest(BaseModel):
    prompt: str
    website_url: str
    previous_email: Optional[str] = None
    operation: str = "generate"  # "generate" or "refine"
    
    
# class GenerationRequest(BaseModel):
#     query: str
#     style_type: str
