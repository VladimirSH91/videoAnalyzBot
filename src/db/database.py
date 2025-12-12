from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from config.settings import settings


POSTGRES_URL = f'postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@' \
               f'{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}'
engine = create_async_engine(POSTGRES_URL)

async_database_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_async_session():
    async with async_database_session_maker() as session:
        yield session

Base = declarative_base()
