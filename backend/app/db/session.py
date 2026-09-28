from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from app.core.config import settings

# Append ?prepared_statement_cache_size=0 to URL if not present
db_url = str(settings.DATABASE_URL)
if db_url and "?" not in db_url:
    db_url += "?prepared_statement_cache_size=0"
elif db_url:
    db_url += "&prepared_statement_cache_size=0"

engine = create_async_engine(
    db_url, 
    echo=False, 
    poolclass=NullPool,
    connect_args={"statement_cache_size": 0}
) if settings.DATABASE_URL else None
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
