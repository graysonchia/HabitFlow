import asyncio
from app.database import engine

async def test():
    async with engine.connect() as conn:
        print("✅ Database connection successful")

asyncio.run(test())