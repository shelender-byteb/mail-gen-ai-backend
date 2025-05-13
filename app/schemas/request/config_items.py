from enum import Enum
from pydantic import BaseModel, Field

class ServiceType(str, Enum):
    SPLASH_PAGE = "splash_page"
    BANNER      = "banner"
    BLURB       = "blurb"
    EMAIL       = "email"

class ConfigItemRequest(BaseModel):
    placeholder: str = Field(..., description="Default placeholder text")
    heading:     str = Field(..., description="Main heading")
    subheading:  str = Field(..., description="Secondary heading")
    styleheading: str = Field(..., description="Style heading text")
    boldstyle:    str = Field(..., description="Bold style text")
    cozystyle:    str = Field(..., description="Cozy style text")
    urlheading:   str = Field(..., description="URL heading text")


class ConfigItemResponse(BaseModel):
    placeholder: str = Field(..., description="Default placeholder text")
    heading:     str = Field(..., description="Main heading")
    subheading:  str = Field(..., description="Secondary heading")
    styleheading: str
    boldstyle:    str
    cozystyle:    str
    urlheading:   str

    class Config:
        from_attributes = True