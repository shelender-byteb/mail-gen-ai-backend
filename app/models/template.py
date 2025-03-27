from sqlalchemy import Column, Integer, String, DateTime, func
from app.common.database_config import Base

class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    template_type = Column(String, unique=True, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
