
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db.sessions import DATABASE_URL


# This async setup is intended for the PostgreSQL database used by the project.
if not DATABASE_URL.startswith("postgresql://"):
    raise RuntimeError(
        "Async database sessions require a PostgreSQL DATABASE_URL."
    )


# Convert the normal PostgreSQL driver URL to the asyncpg driver URL.
ASYNC_DATABASE_URL = DATABASE_URL.replace(
    "postgresql://",
    "postgresql+asyncpg://",
    1,
)


# Create the asynchronous SQLAlchemy engine.
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_pre_ping=True,
)


# Create async database sessions.
# expire_on_commit=False allows returned ORM objects to be read after commit.
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide one async database session per request.

    The session is automatically closed when the request finishes.
    """
    async with AsyncSessionLocal() as session:
        yield session
