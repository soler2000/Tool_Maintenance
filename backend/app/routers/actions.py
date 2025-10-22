"""Action item endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..crud import create_instance, get_instance, list_instances, update_instance
from ..database import get_session
from ..dependencies import get_current_user

router = APIRouter(prefix="/actions", tags=["actions"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[schemas.ActionItemRead])
async def list_action_items(session: AsyncSession = Depends(get_session)) -> list[schemas.ActionItemRead]:
    items = await list_instances(session, models.ActionItem)
    return [schemas.ActionItemRead.from_orm(item) for item in items]


@router.post("", response_model=schemas.ActionItemRead, status_code=status.HTTP_201_CREATED)
async def create_action_item(
    payload: schemas.ActionItemCreate,
    session: AsyncSession = Depends(get_session),
) -> schemas.ActionItemRead:
    item = models.ActionItem(**payload.dict())
    item = await create_instance(session, item)
    return schemas.ActionItemRead.from_orm(item)


@router.patch("/{action_id}", response_model=schemas.ActionItemRead)
async def update_action_item(
    action_id: str,
    payload: schemas.ActionItemUpdate,
    session: AsyncSession = Depends(get_session),
) -> schemas.ActionItemRead:
    try:
        item = await get_instance(session, models.ActionItem, action_id)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Action item not found") from exc
    item = await update_instance(session, item, payload.dict(exclude_unset=True))
    return schemas.ActionItemRead.from_orm(item)
