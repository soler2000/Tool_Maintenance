"""Database configuration and session management."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import get_settings


class Base(DeclarativeBase):
    """Declarative base for SQLAlchemy models."""


_settings = get_settings()
_engine: AsyncEngine = create_async_engine(_settings.database_url, future=True, echo=_settings.debug)
SessionLocal = async_sessionmaker(bind=_engine, expire_on_commit=False)


@asynccontextmanager
async def lifespan_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async session for FastAPI lifespan events."""

    async with SessionLocal() as session:
        yield session


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields an async database session."""

    async with SessionLocal() as session:
        yield session


async def init_models() -> None:
    """Create database schema if it does not exist."""

    from . import models  # noqa: WPS433 F401 (import required for model discovery)

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_apply_schema_backfills)


def _apply_schema_backfills(connection: Connection) -> None:
    """Add any missing columns required by recent releases."""

    if connection.dialect.name != "sqlite":
        return

    inspector = inspect(connection)
    tool_columns = {column["name"] for column in inspector.get_columns("tools")}

    if "initial_shot_count" not in tool_columns:
        connection.execute(
            text(
                "ALTER TABLE tools "
                "ADD COLUMN initial_shot_count INTEGER NOT NULL DEFAULT 0"
            )
        )

    if "current_shot_count" not in tool_columns:
        connection.execute(
            text(
                "ALTER TABLE tools "
                "ADD COLUMN current_shot_count INTEGER NOT NULL DEFAULT 0"
            )
        )


__all__ = ["Base", "SessionLocal", "get_session", "init_models", "lifespan_session"]
