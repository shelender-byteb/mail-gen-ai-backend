# app/models/splash_page.py
from sqlalchemy import Column, String, Text, DateTime
from datetime import datetime
import uuid
from app.common.database_config import Base

class SplashPage(Base):
    __tablename__ = "splash_pages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    html_content = Column(Text, nullable=False)
    button_url = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)