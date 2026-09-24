from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False, connect_args={"statement_cache_size": 0}) if settings.DATABASE_URL else None
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
) if engine else None

async def get_db():
    if not AsyncSessionLocal:
        raise ValueError("DATABASE_URL is not configured")
    async with AsyncSessionLocal() as session:
        yield session
