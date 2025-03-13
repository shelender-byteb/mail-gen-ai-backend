from datetime import datetime
from pydantic import BaseModel
from typing import List


class ChatbotResponse(BaseModel):
    id: str
    answer: str

class Chats(BaseModel):
    role: str
    message: str

class GetMessagesResponse(BaseModel):
    id: str
    chat_messages: List[dict]

class SplashPageResponse(BaseModel):
    id: str
    html_content: str
    button_url: str | None
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True