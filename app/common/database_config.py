from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.common import env_config


#getting all the envs
envs = env_config.get_envs_setting()
# SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{envs.MYSQL_USER}:{envs.MYSQL_PASSWORD}@{envs.MYSQL_HOST}/{envs.MYSQL_DB}"
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg2://{envs.POSTGRES_USER}:{envs.POSTGRES_PASSWORD}"
    f"@{envs.POSTGRES_HOST}:{envs.POSTGRES_PORT}/{envs.POSTGRES_DB}"
)
SQLALCHEMY_DATABASE_URL_ASYNC = envs.DATABASE_URI_ASYNC

ENGINE = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=50,        
    max_overflow=10,       
    pool_timeout=90,
    pool_pre_ping=True,
    pool_recycle=3600,
)

ASYNC_ENGINE = create_async_engine(
    SQLALCHEMY_DATABASE_URL_ASYNC,
    pool_size=50,
    max_overflow=10,
    pool_timeout=90,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)


# Async session
AsyncSessionLocal = sessionmaker(
    bind=ASYNC_ENGINE,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Async dependency
async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Import all models here
from app.models.splash_page import SplashPage
from app.models.template import Template
from app.models.model_config import ModelConfig

# Create tables synchronously
Base.metadata.create_all(bind=ENGINE)