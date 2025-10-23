"""Authentication endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas
from ..crud import create_user, get_user_by_username
from ..database import get_session
from ..security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(payload: schemas.UserCreate, session: AsyncSession = Depends(get_session)) -> schemas.UserRead:
    """Register a new user."""

    try:
        user = await create_user(
            session,
            username=payload.username,
            password=payload.password,
            full_name=payload.full_name,
            email=payload.email,
            role=payload.role,
        )
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Username already exists") from exc
    return schemas.UserRead.from_orm(user)


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    payload: schemas.LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> schemas.Token:
    """Authenticate user credentials and issue a JWT access token."""

    try:
        user = await get_user_by_username(session, payload.username)
    except NoResultFound as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials") from exc
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(user.username)
    user.last_login_at = user.last_login_at or user.created_at
    await session.commit()
    return schemas.Token(access_token=access_token)
