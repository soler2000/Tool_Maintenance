"""SQLAlchemy ORM models for the Tool Maintenance Management System."""
from __future__ import annotations

import enum
from datetime import date, datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


UUID_STR = String(36)


def uuid_str() -> str:
    """Return a new UUID4 string."""

    return str(uuid4())


class ToolStatus(str, enum.Enum):
    active = "active"
    maintenance = "maintenance"
    retired = "retired"


class ShotSource(str, enum.Enum):
    manual = "manual"
    imported = "imported"
    automatic = "automatic"


class Severity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ActionStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class PhotoAngle(str, enum.Enum):
    front = "front"
    rear = "rear"
    core = "core"
    cavity = "cavity"
    other = "other"


class UserRole(str, enum.Enum):
    technician = "technician"
    engineer = "engineer"
    manager = "manager"
    admin = "admin"


class Tool(Base):
    __tablename__ = "tools"

    id: Mapped[str] = mapped_column(UUID_STR, primary_key=True, default=uuid_str)
    asset_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(120))
    cavity_count: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[ToolStatus] = mapped_column(Enum(ToolStatus), default=ToolStatus.active, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    shot_counters: Mapped[list["ToolShotCounter"]] = relationship(back_populates="tool", cascade="all, delete-orphan")
    maintenance_logs: Mapped[list["MaintenanceLog"]] = relationship(back_populates="tool", cascade="all, delete-orphan")
    failure_reports: Mapped[list["FailureReport"]] = relationship(back_populates="tool", cascade="all, delete-orphan")
    photos: Mapped[list["ToolPhoto"]] = relationship(back_populates="tool", cascade="all, delete-orphan")
    action_items: Mapped[list["ActionItem"]] = relationship(back_populates="tool", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID_STR, primary_key=True, default=uuid_str)
    username: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.technician)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    maintenance_logs: Mapped[list["MaintenanceLog"]] = relationship(back_populates="performed_by_user")
    failure_reports: Mapped[list["FailureReport"]] = relationship(back_populates="reported_by_user")
    action_items: Mapped[list["ActionItem"]] = relationship(back_populates="assignee")


class ToolShotCounter(Base):
    __tablename__ = "tool_shot_counters"

    id: Mapped[str] = mapped_column(UUID_STR, primary_key=True, default=uuid_str)
    tool_id: Mapped[str] = mapped_column(ForeignKey("tools.id", ondelete="CASCADE"), nullable=False)
    shot_count: Mapped[int] = mapped_column(Integer, nullable=False)
    recorded_by: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    source: Mapped[ShotSource] = mapped_column(Enum(ShotSource), default=ShotSource.manual, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    tool: Mapped[Tool] = relationship(back_populates="shot_counters")
    recorded_by_user: Mapped[Optional[User]] = relationship()


class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id: Mapped[str] = mapped_column(UUID_STR, primary_key=True, default=uuid_str)
    tool_id: Mapped[str] = mapped_column(ForeignKey("tools.id", ondelete="CASCADE"), nullable=False)
    performed_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    checklist_template: Mapped[Optional[str]] = mapped_column(UUID_STR)
    performed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    observations: Mapped[Optional[str]] = mapped_column(Text)
    follow_up_required: Mapped[bool] = mapped_column(Boolean, default=False)

    tool: Mapped[Tool] = relationship(back_populates="maintenance_logs")
    performed_by_user: Mapped[User] = relationship(back_populates="maintenance_logs")


class FailureCode(Base):
    __tablename__ = "failure_codes"

    id: Mapped[str] = mapped_column(UUID_STR, primary_key=True, default=uuid_str)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    severity_default: Mapped[Severity] = mapped_column(Enum(Severity), default=Severity.medium)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    failure_reports: Mapped[list["FailureReport"]] = relationship(back_populates="failure_code")


class FailureReport(Base):
    __tablename__ = "failure_reports"

    id: Mapped[str] = mapped_column(UUID_STR, primary_key=True, default=uuid_str)
    tool_id: Mapped[str] = mapped_column(ForeignKey("tools.id", ondelete="CASCADE"), nullable=False)
    reported_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    failure_code_id: Mapped[Optional[str]] = mapped_column(ForeignKey("failure_codes.id"))
    severity: Mapped[Severity] = mapped_column(Enum(Severity), default=Severity.medium, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    containment_action: Mapped[Optional[str]] = mapped_column(Text)

    tool: Mapped[Tool] = relationship(back_populates="failure_reports")
    reported_by_user: Mapped[User] = relationship(back_populates="failure_reports")
    failure_code: Mapped[Optional[FailureCode]] = relationship(back_populates="failure_reports")
    photos: Mapped[list["FailurePhoto"]] = relationship(back_populates="failure_report", cascade="all, delete-orphan")
    action_items: Mapped[list["ActionItem"]] = relationship(back_populates="failure_report")


class FailurePhoto(Base):
    __tablename__ = "failure_photos"

    id: Mapped[str] = mapped_column(UUID_STR, primary_key=True, default=uuid_str)
    failure_report_id: Mapped[str] = mapped_column(ForeignKey("failure_reports.id", ondelete="CASCADE"), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(255), nullable=False)
    caption: Mapped[Optional[str]] = mapped_column(String(255))
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    failure_report: Mapped[FailureReport] = relationship(back_populates="photos")


class ToolPhoto(Base):
    __tablename__ = "tool_photos"

    id: Mapped[str] = mapped_column(UUID_STR, primary_key=True, default=uuid_str)
    tool_id: Mapped[str] = mapped_column(ForeignKey("tools.id", ondelete="CASCADE"), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(255), nullable=False)
    angle: Mapped[Optional[PhotoAngle]] = mapped_column(Enum(PhotoAngle))
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tool: Mapped[Tool] = relationship(back_populates="photos")


class ActionItem(Base):
    __tablename__ = "action_items"

    id: Mapped[str] = mapped_column(UUID_STR, primary_key=True, default=uuid_str)
    tool_id: Mapped[str] = mapped_column(ForeignKey("tools.id", ondelete="CASCADE"), nullable=False)
    failure_report_id: Mapped[Optional[str]] = mapped_column(ForeignKey("failure_reports.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    assigned_to: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[ActionStatus] = mapped_column(Enum(ActionStatus), default=ActionStatus.open, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    tool: Mapped[Tool] = relationship(back_populates="action_items")
    failure_report: Mapped[Optional[FailureReport]] = relationship(back_populates="action_items")
    assignee: Mapped[User] = relationship(back_populates="action_items")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(UUID_STR, primary_key=True, default=uuid_str)
    user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    entity_type: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(120), nullable=False)
    action: Mapped[str] = mapped_column(String(60), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text)


class IntegrationEvent(Base):
    __tablename__ = "integration_events"

    id: Mapped[str] = mapped_column(UUID_STR, primary_key=True, default=uuid_str)
    source: Mapped[str] = mapped_column(String(120), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(60), default="received")
    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)


__all__ = [
    "Tool",
    "ToolShotCounter",
    "MaintenanceLog",
    "FailureCode",
    "FailureReport",
    "FailurePhoto",
    "ToolPhoto",
    "ActionItem",
    "User",
    "AuditLog",
    "IntegrationEvent",
    "ToolStatus",
    "ShotSource",
    "Severity",
    "ActionStatus",
    "PhotoAngle",
    "UserRole",
]
