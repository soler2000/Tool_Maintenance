"""Maintenance log endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..crud import create_instance, get_instance, list_instances
from ..database import get_session
from ..dependencies import get_current_user

router = APIRouter(prefix="/maintenance", tags=["maintenance"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[schemas.MaintenanceLogRead])
async def list_maintenance_logs(session: AsyncSession = Depends(get_session)) -> list[schemas.MaintenanceLogRead]:
    logs = await list_instances(session, models.MaintenanceLog)
    return [schemas.MaintenanceLogRead.from_orm(log) for log in logs]


@router.post("", response_model=schemas.MaintenanceLogRead, status_code=status.HTTP_201_CREATED)
async def create_maintenance_log(
    payload: schemas.MaintenanceLogCreate,
    session: AsyncSession = Depends(get_session),
) -> schemas.MaintenanceLogRead:
    log = models.MaintenanceLog(**payload.dict())
    log = await create_instance(session, log)
    return schemas.MaintenanceLogRead.from_orm(log)


@router.get("/{log_id}", response_model=schemas.MaintenanceLogRead)
async def get_maintenance_log(log_id: str, session: AsyncSession = Depends(get_session)) -> schemas.MaintenanceLogRead:
    try:
        log = await get_instance(session, models.MaintenanceLog, log_id)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Maintenance log not found") from exc
    return schemas.MaintenanceLogRead.from_orm(log)
