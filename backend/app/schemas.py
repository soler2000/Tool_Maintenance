"""Pydantic schemas for API request/response models."""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from pydantic.config import ConfigDict

from .models import ActionStatus, PhotoAngle, Severity, ShotSource, ToolStatus, UserRole


class APIModel(BaseModel):
    """Base schema with attribute-based serialisation enabled."""

    model_config = ConfigDict(from_attributes=True)


class UserBase(APIModel):
    username: str
    full_name: str
    email: Optional[EmailStr]
    role: UserRole = UserRole.technician


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserRead(UserBase):
    id: str
    created_at: datetime
    last_login_at: Optional[datetime]


class ToolBase(APIModel):
    asset_number: str
    name: str
    description: Optional[str]
    manufacturer: Optional[str]
    cavity_count: Optional[int]
    initial_shot_count: int = 0
    max_shot_count: Optional[int]
    status: ToolStatus = ToolStatus.active
    location: Optional[str]


class ToolCreate(ToolBase):
    pass


class ToolUpdate(APIModel):
    name: Optional[str]
    description: Optional[str]
    manufacturer: Optional[str]
    cavity_count: Optional[int]
    initial_shot_count: Optional[int]
    max_shot_count: Optional[int]
    status: Optional[ToolStatus]
    location: Optional[str]


class ToolRead(ToolBase):
    id: str
    created_at: datetime
    updated_at: datetime


class ToolShotCounterBase(APIModel):
    shot_count: int
    recorded_by: Optional[str]
    source: ShotSource = ShotSource.manual
    recorded_at: Optional[datetime]


class ToolShotCounterCreate(ToolShotCounterBase):
    tool_id: str


class ToolShotCounterRead(ToolShotCounterBase):
    id: str
    tool_id: str


class MaintenanceLogBase(APIModel):
    tool_id: str
    performed_by: str
    checklist_template: Optional[str]
    performed_at: Optional[datetime]
    duration_minutes: Optional[int]
    observations: Optional[str]
    follow_up_required: bool = False


class MaintenanceLogCreate(MaintenanceLogBase):
    pass


class MaintenanceLogRead(MaintenanceLogBase):
    id: str


class FailureCodeBase(APIModel):
    code: str
    name: str
    description: Optional[str]
    severity_default: Severity = Severity.medium
    active: bool = True


class FailureCodeCreate(FailureCodeBase):
    pass


class FailureCodeUpdate(APIModel):
    name: Optional[str]
    description: Optional[str]
    severity_default: Optional[Severity]
    active: Optional[bool]


class FailureCodeRead(FailureCodeBase):
    id: str


class FailureReportBase(APIModel):
    tool_id: str
    reported_by: str
    failure_code_id: Optional[str]
    severity: Severity = Severity.medium
    description: Optional[str]
    occurred_at: Optional[datetime]
    containment_action: Optional[str]


class FailureReportCreate(FailureReportBase):
    pass


class FailureReportRead(FailureReportBase):
    id: str


class FailurePhotoBase(APIModel):
    failure_report_id: str
    storage_path: str
    caption: Optional[str]
    captured_at: Optional[datetime]


class FailurePhotoCreate(FailurePhotoBase):
    pass


class FailurePhotoRead(FailurePhotoBase):
    id: str


class ToolPhotoBase(APIModel):
    tool_id: str
    storage_path: str
    angle: Optional[PhotoAngle]
    captured_at: Optional[datetime]


class ToolPhotoCreate(ToolPhotoBase):
    pass


class ToolPhotoRead(ToolPhotoBase):
    id: str


class ActionItemBase(APIModel):
    tool_id: str
    failure_report_id: Optional[str]
    title: str
    description: Optional[str]
    assigned_to: str
    due_date: Optional[date]
    status: ActionStatus = ActionStatus.open
    completed_at: Optional[datetime]


class ActionItemCreate(ActionItemBase):
    pass


class ActionItemUpdate(APIModel):
    title: Optional[str]
    description: Optional[str]
    assigned_to: Optional[str]
    due_date: Optional[date]
    status: Optional[ActionStatus]
    completed_at: Optional[datetime]


class ActionItemRead(ActionItemBase):
    id: str


class Token(APIModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(APIModel):
    sub: str
    exp: int


class LoginRequest(APIModel):
    username: str
    password: str
