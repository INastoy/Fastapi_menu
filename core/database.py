from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from core.settings import DATABASE_URL

engine = create_async_engine(DATABASE_URL)
Session = sessionmaker(engine, class_=AsyncSession)
Base = declarative_base()


async def get_session() -> AsyncSession:
    async_session = Session()
    async with async_session as session:
        yield session
