from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from astro_bot.database.engine import async_engine


def inject_db_session() -> AsyncSession:
    session_maker = sessionmaker(async_engine, autocommit=False, autoflush=False, class_=AsyncSession)
    return session_maker()
