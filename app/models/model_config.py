from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.common.database_config import Base

class ModelConfig(Base):
    __tablename__ = "model_configs"

    id = Column(Integer, primary_key=True, index=True)
    model_type = Column(String, unique=True, nullable=False)
    model_name = Column(String, nullable=False)
    temperature = Column(Float, nullable=False)
    provider = Column(String, nullable=False, server_default="openai")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
