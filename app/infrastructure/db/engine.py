from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.infrastructure.db.config import pg_settings

engine: AsyncEngine = create_async_engine(
    url=pg_settings.get_database_url,
    echo=pg_settings.get_alchemy_echo,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300,
)

SessionFactory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with SessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()


async def dispose_db_engine():
    """Close database connection"""
    await engine.dispose()
