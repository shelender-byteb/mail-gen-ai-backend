from typing import Optional
from enum import Enum
from pydantic import BaseModel

class ServiceType(int, Enum):
    SPLASH_PAGE = 0
    EMAIL = 1
    BANNER = 2

class AutocompleteRequest(BaseModel):
    query: str
    service_type: int
    style_type: Optional[str]
    
class AutocompleteResponse(BaseModel):
    completion: str