from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

class Operation(str, Enum):
    BANNER_GENERATION = "start_over"
    BANNER_REFINEMENT = "update"


class BannerGenerationRequest(BaseModel):
    user_prompt: str
    width: int
    height: int = 500
    operation: Operation
    website_url: Optional[str] = None
    previous_banner: Optional[str] = None
