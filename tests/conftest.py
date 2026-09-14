import pytest_asyncio
from app.db.session import engine


@pytest_asyncio.fixture(autouse=True)
async def cleanup_db_engine():
    """
    Automatically disposes of pooled DB connections before and after each test
    to prevent cross-event-loop connection reuse errors in asyncpg.
    """
    await engine.dispose()
    yield
    await engine.dispose()
