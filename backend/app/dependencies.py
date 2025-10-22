"""Reusable dependency functions."""
from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from . import models
from .crud import get_instance, get_user_by_username
from .database import get_session
from .security import decode_token
from .config import get_settings

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> models.User:
    """Resolve the currently authenticated user from a JWT token."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        username = payload.get("sub")
    except Exception as exc:  # noqa: BLE001 - propagate as HTTP error
        raise credentials_exception from exc
    if not username:
        raise credentials_exception
    try:
        user = await get_user_by_username(session, username)
    except NoResultFound as exc:
        raise credentials_exception from exc
    return user


async def get_tool(tool_id: str, session: AsyncSession = Depends(get_session)) -> models.Tool:
    return await get_instance(session, models.Tool, tool_id)


async def get_failure_code(failure_code_id: str, session: AsyncSession = Depends(get_session)) -> models.FailureCode:
    return await get_instance(session, models.FailureCode, failure_code_id)


async def get_failure_report(report_id: str, session: AsyncSession = Depends(get_session)) -> models.FailureReport:
    return await get_instance(session, models.FailureReport, report_id)


async def get_action_item(action_id: str, session: AsyncSession = Depends(get_session)) -> models.ActionItem:
    return await get_instance(session, models.ActionItem, action_id)


__all__ = [
    "get_current_user",
    "oauth2_scheme",
    "get_tool",
    "get_failure_code",
    "get_failure_report",
    "get_action_item",
]
