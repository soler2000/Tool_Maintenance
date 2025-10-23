"""Shot counter endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..crud import get_instance
from ..database import get_session
from ..dependencies import get_current_user

router = APIRouter(prefix="/shot-counters", tags=["shot counters"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[schemas.ToolShotCounterRead])
async def list_shot_counters(session: AsyncSession = Depends(get_session)) -> list[schemas.ToolShotCounterRead]:
    result = await session.execute(
        select(models.ToolShotCounter).order_by(models.ToolShotCounter.recorded_at, models.ToolShotCounter.id),
    )
    counters = result.scalars().all()
    return [schemas.ToolShotCounterRead.from_orm(counter) for counter in counters]


@router.post("", response_model=schemas.ToolShotCounterRead, status_code=status.HTTP_201_CREATED)
async def create_shot_counter(
    payload: schemas.ToolShotCounterCreate,
    session: AsyncSession = Depends(get_session),
) -> schemas.ToolShotCounterRead:
    try:
        tool = await get_instance(session, models.Tool, payload.tool_id)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Tool not found") from exc

    counter = models.ToolShotCounter(**payload.dict())
    current_total = max(tool.current_shot_count, tool.initial_shot_count)
    tool.current_shot_count = current_total + counter.shot_count

    session.add(counter)
    await session.commit()
    await session.refresh(counter)
    return schemas.ToolShotCounterRead.from_orm(counter)


@router.get("/{counter_id}", response_model=schemas.ToolShotCounterRead)
async def get_shot_counter(counter_id: str, session: AsyncSession = Depends(get_session)) -> schemas.ToolShotCounterRead:
    try:
        counter = await get_instance(session, models.ToolShotCounter, counter_id)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Shot counter not found") from exc
    return schemas.ToolShotCounterRead.from_orm(counter)


@router.patch("/{counter_id}", response_model=schemas.ToolShotCounterRead)
async def update_shot_counter(
    counter_id: str,
    payload: schemas.ToolShotCounterUpdate,
    session: AsyncSession = Depends(get_session),
) -> schemas.ToolShotCounterRead:
    try:
        counter = await get_instance(session, models.ToolShotCounter, counter_id)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Shot counter not found") from exc

    data = payload.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(counter, key, value)

    await session.flush()

    if "shot_count" in data:
        result = await session.execute(
            select(func.coalesce(func.sum(models.ToolShotCounter.shot_count), 0)).where(
                models.ToolShotCounter.tool_id == counter.tool_id
            )
        )
        total_shots = result.scalar_one()
        tool = await get_instance(session, models.Tool, counter.tool_id)
        tool.current_shot_count = max(tool.initial_shot_count, tool.initial_shot_count + total_shots)

    await session.commit()
    await session.refresh(counter)
    return schemas.ToolShotCounterRead.from_orm(counter)
