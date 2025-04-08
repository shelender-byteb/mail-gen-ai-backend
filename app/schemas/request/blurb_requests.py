from typing import Optional
from pydantic import BaseModel, Field, validator

from enum import Enum

class Operation(str, Enum):
    BLURB_GENERATION = "start_over"
    BLURB_REFINEMENT = "update"


class PowerBlurbGenerationRequest(BaseModel):
    prompt: str
    website_url: str
    operation: Operation
    previous_blurb: Optional[str] = None


class PowerBlurbGenerationResponse(BaseModel):
    html: str 