"""Core module for database session related operations."""

from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from src.config import settings

crud_conn_url = "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
    settings.DB_USER,
    settings.DB_PASSWORD,
    settings.DB_HOST,
    settings.DB_PORT,
    settings.DB_NAME,
)

crud_engine = create_async_engine(crud_conn_url, pool_pre_ping=True)

read_only_conn_url = "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
    settings.DB_USER,
    settings.DB_PASSWORD,
    settings.DB_HOST_READ_ONLY or settings.DB_HOST,
    settings.DB_PORT,
    settings.DB_NAME,
)

read_only_engine = create_async_engine(read_only_conn_url, pool_pre_ping=True)


async def create_async_session(read_only: bool = True) -> async_scoped_session[AsyncSession]:
    """Create an asynchronous scoped session for database operations.

    This function sets up an asynchronous session using the provided engine and
    session factory. The session is scoped to the current task, ensuring that
    each task gets its own session.

    Returns:
        async_scoped_session[AsyncSession]: An asynchronous scoped session for
        performing database operations.

    """
    async_session = async_scoped_session(
        session_factory=async_sessionmaker(
            read_only_engine if read_only else crud_engine,
            expire_on_commit=False,
            class_=AsyncSession,
            autoflush=False,
        ),
        scopefunc=current_task,
    )
    return async_session
