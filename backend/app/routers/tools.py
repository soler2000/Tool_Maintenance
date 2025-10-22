"""Tool management endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..crud import create_instance, delete_instance, get_instance, list_instances, update_instance
from ..database import get_session
from ..dependencies import get_current_user

router = APIRouter(prefix="/tools", tags=["tools"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[schemas.ToolRead])
async def list_tools(session: AsyncSession = Depends(get_session)) -> list[schemas.ToolRead]:
    tools = await list_instances(session, models.Tool)
    return [schemas.ToolRead.from_orm(tool) for tool in tools]


@router.post("", response_model=schemas.ToolRead, status_code=status.HTTP_201_CREATED)
async def create_tool(payload: schemas.ToolCreate, session: AsyncSession = Depends(get_session)) -> schemas.ToolRead:
    tool = models.Tool(**payload.dict())
    tool = await create_instance(session, tool)
    return schemas.ToolRead.from_orm(tool)


@router.get("/{tool_id}", response_model=schemas.ToolRead)
async def get_tool(tool_id: str, session: AsyncSession = Depends(get_session)) -> schemas.ToolRead:
    try:
        tool = await get_instance(session, models.Tool, tool_id)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Tool not found") from exc
    return schemas.ToolRead.from_orm(tool)


@router.patch("/{tool_id}", response_model=schemas.ToolRead)
async def update_tool(tool_id: str, payload: schemas.ToolUpdate, session: AsyncSession = Depends(get_session)) -> schemas.ToolRead:
    try:
        tool = await get_instance(session, models.Tool, tool_id)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Tool not found") from exc
    tool = await update_instance(session, tool, payload.dict(exclude_unset=True))
    return schemas.ToolRead.from_orm(tool)


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(tool_id: str, session: AsyncSession = Depends(get_session)) -> None:
    try:
        tool = await get_instance(session, models.Tool, tool_id)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Tool not found") from exc
    await delete_instance(session, tool)
