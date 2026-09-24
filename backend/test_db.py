import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

async def main():
    print(f"Connecting to {settings.DATABASE_URL.split('@')[-1]}...")
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async with engine.connect() as conn:
        print("Connected!")
    await engine.dispose()

asyncio.run(main())
