from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from config.settings import settings


engine = create_async_engine(settings.database_url, pool_pre_ping=True)

async_database_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_async_session():
    async with async_database_session_maker() as session:
        yield session

Base = declarative_base()
