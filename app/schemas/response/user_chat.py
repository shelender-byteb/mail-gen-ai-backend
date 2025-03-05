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