from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from config.db import AsyncSessionLocal


@asynccontextmanager
async def get_db_readonly() -> AsyncSession: # для функций без commit
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_db() -> AsyncSession: # для функций с commit
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()