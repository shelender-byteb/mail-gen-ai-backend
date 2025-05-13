from sqlalchemy import Column, Integer, String, DateTime, func
from app.common.database_config import Base

class ConfigItem(Base):
    __tablename__ = "config_items"

    id           = Column(Integer, primary_key=True, index=True)
    service_type = Column(String, unique=True, nullable=False)
    placeholder  = Column(String, nullable=False)
    heading      = Column(String, nullable=False)
    subheading   = Column(String, nullable=False)
    styleheading = Column(String, nullable=False)
    boldstyle    = Column(String, nullable=False)
    cozystyle    = Column(String, nullable=False)
    urlheading   = Column(String, nullable=False)
    created_at   = Column(DateTime, server_default=func.now())
    updated_at   = Column(DateTime, server_default=func.now(), onupdate=func.now())
