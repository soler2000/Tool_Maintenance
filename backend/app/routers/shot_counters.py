"""Shot counter endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..crud import create_instance, get_instance, list_instances
from ..database import get_session
from ..dependencies import get_current_user

router = APIRouter(prefix="/shot-counters", tags=["shot counters"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[schemas.ToolShotCounterRead])
async def list_shot_counters(session: AsyncSession = Depends(get_session)) -> list[schemas.ToolShotCounterRead]:
    counters = await list_instances(session, models.ToolShotCounter)
    return [schemas.ToolShotCounterRead.from_orm(counter) for counter in counters]


@router.post("", response_model=schemas.ToolShotCounterRead, status_code=status.HTTP_201_CREATED)
async def create_shot_counter(
    payload: schemas.ToolShotCounterCreate,
    session: AsyncSession = Depends(get_session),
) -> schemas.ToolShotCounterRead:
    counter = models.ToolShotCounter(**payload.dict())
    counter = await create_instance(session, counter)
    return schemas.ToolShotCounterRead.from_orm(counter)


@router.get("/{counter_id}", response_model=schemas.ToolShotCounterRead)
async def get_shot_counter(counter_id: str, session: AsyncSession = Depends(get_session)) -> schemas.ToolShotCounterRead:
    try:
        counter = await get_instance(session, models.ToolShotCounter, counter_id)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Shot counter not found") from exc
    return schemas.ToolShotCounterRead.from_orm(counter)
