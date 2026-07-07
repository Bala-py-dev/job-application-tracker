from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models import ApplicationStatus


class ApplicationBase(BaseModel):
    company: str
    role: str
    location: Optional[str] = None
    source: Optional[str] = None
    next_action: Optional[str] = None
    next_action_date: Optional[datetime] = None
    notes: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    status: ApplicationStatus = ApplicationStatus.applied


class ApplicationUpdate(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None
    source: Optional[str] = None
    next_action: Optional[str] = None
    next_action_date: Optional[datetime] = None
    notes: Optional[str] = None


class StatusUpdate(BaseModel):
    status: ApplicationStatus
    note: Optional[str] = None


class StatusEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    old_status: Optional[ApplicationStatus] = None
    new_status: ApplicationStatus
    note: Optional[str] = None
    created_at: datetime


class ApplicationOut(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: ApplicationStatus
    applied_date: datetime
    created_at: datetime
    updated_at: datetime
    events: list[StatusEventOut] = []


class EmailIn(BaseModel):
    text: str


class ExtractedApplication(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    next_action: Optional[str] = None
    next_action_date: Optional[datetime] = None


class ReminderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company: str
    role: str
    status: ApplicationStatus
    next_action: Optional[str] = None
    next_action_date: Optional[datetime] = None
