"""Failure code and report endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..crud import create_instance, get_instance, list_instances, update_instance
from ..database import get_session
from ..dependencies import get_current_user

router = APIRouter(prefix="/failures", tags=["failures"], dependencies=[Depends(get_current_user)])


@router.get("/codes", response_model=list[schemas.FailureCodeRead])
async def list_failure_codes(session: AsyncSession = Depends(get_session)) -> list[schemas.FailureCodeRead]:
    codes = await list_instances(session, models.FailureCode)
    return [schemas.FailureCodeRead.from_orm(code) for code in codes]


@router.post("/codes", response_model=schemas.FailureCodeRead, status_code=status.HTTP_201_CREATED)
async def create_failure_code(
    payload: schemas.FailureCodeCreate,
    session: AsyncSession = Depends(get_session),
) -> schemas.FailureCodeRead:
    code = models.FailureCode(**payload.dict())
    code = await create_instance(session, code)
    return schemas.FailureCodeRead.from_orm(code)


@router.patch("/codes/{code_id}", response_model=schemas.FailureCodeRead)
async def update_failure_code(
    code_id: str,
    payload: schemas.FailureCodeUpdate,
    session: AsyncSession = Depends(get_session),
) -> schemas.FailureCodeRead:
    try:
        code = await get_instance(session, models.FailureCode, code_id)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Failure code not found") from exc
    code = await update_instance(session, code, payload.dict(exclude_unset=True))
    return schemas.FailureCodeRead.from_orm(code)


@router.get("/reports", response_model=list[schemas.FailureReportRead])
async def list_failure_reports(session: AsyncSession = Depends(get_session)) -> list[schemas.FailureReportRead]:
    reports = await list_instances(session, models.FailureReport)
    return [schemas.FailureReportRead.from_orm(report) for report in reports]


@router.post("/reports", response_model=schemas.FailureReportRead, status_code=status.HTTP_201_CREATED)
async def create_failure_report(
    payload: schemas.FailureReportCreate,
    session: AsyncSession = Depends(get_session),
) -> schemas.FailureReportRead:
    report = models.FailureReport(**payload.dict())
    report = await create_instance(session, report)
    return schemas.FailureReportRead.from_orm(report)


@router.get("/reports/{report_id}", response_model=schemas.FailureReportRead)
async def get_failure_report(report_id: str, session: AsyncSession = Depends(get_session)) -> schemas.FailureReportRead:
    try:
        report = await get_instance(session, models.FailureReport, report_id)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Failure report not found") from exc
    return schemas.FailureReportRead.from_orm(report)


@router.patch("/reports/{report_id}", response_model=schemas.FailureReportRead)
async def update_failure_report(
    report_id: str,
    payload: schemas.FailureReportUpdate,
    session: AsyncSession = Depends(get_session),
) -> schemas.FailureReportRead:
    try:
        report = await get_instance(session, models.FailureReport, report_id)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Failure report not found") from exc

    report = await update_instance(session, report, payload.dict(exclude_unset=True))
    return schemas.FailureReportRead.from_orm(report)
