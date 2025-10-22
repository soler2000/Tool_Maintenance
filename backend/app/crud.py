"""Database persistence helpers."""
from __future__ import annotations

from typing import Iterable, Sequence, TypeVar

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from . import models
from .security import hash_password

ModelT = TypeVar("ModelT", bound=models.Base)


async def create_user(session: AsyncSession, *, username: str, password: str, **kwargs) -> models.User:
    """Create a new user with hashed password."""

    user = models.User(username=username, password_hash=hash_password(password), **kwargs)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user_by_username(session: AsyncSession, username: str) -> models.User:
    """Fetch a user by their username."""

    result = await session.execute(select(models.User).where(models.User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise NoResultFound
    return user


async def create_instance(session: AsyncSession, instance: ModelT) -> ModelT:
    """Persist and refresh an instance."""

    session.add(instance)
    await session.commit()
    await session.refresh(instance)
    return instance


async def update_instance(session: AsyncSession, instance: ModelT, data: dict[str, object]) -> ModelT:
    """Update attributes on an instance and persist changes."""

    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)
    await session.commit()
    await session.refresh(instance)
    return instance


async def delete_instance(session: AsyncSession, instance: ModelT) -> None:
    """Delete an instance from the database."""

    await session.delete(instance)
    await session.commit()


async def list_instances(session: AsyncSession, model: type[ModelT]) -> Sequence[ModelT]:
    """Return all rows for a model."""

    result = await session.execute(select(model))
    return result.scalars().all()


async def get_instance(session: AsyncSession, model: type[ModelT], identifier: str) -> ModelT:
    """Retrieve a single instance by primary key."""

    result = await session.execute(select(model).where(model.id == identifier))
    instance = result.scalar_one_or_none()
    if instance is None:
        raise NoResultFound
    return instance


__all__ = [
    "create_user",
    "get_user_by_username",
    "create_instance",
    "update_instance",
    "delete_instance",
    "list_instances",
    "get_instance",
]
