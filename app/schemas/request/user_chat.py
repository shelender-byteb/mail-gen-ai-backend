from typing import Optional
from pydantic import BaseModel

class UserChat(BaseModel):
    id: int
    question: str


class GenerationRequest(BaseModel):
    query: str
    style_type: str
