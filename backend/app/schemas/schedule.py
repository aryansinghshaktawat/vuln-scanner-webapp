"""Pydantic schemas for Scan Schedules."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ScheduleBase(BaseModel):
    asset_id: str
    profile: str = Field("full", pattern="^(quick|full|port_only|vuln_only)$")
    cadence: str = "Every 24 hours"
    interval_hours: int = Field(24, ge=1, le=8760)
    enabled: bool = True


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleUpdate(BaseModel):
    profile: Optional[str] = Field(None, pattern="^(quick|full|port_only|vuln_only)$")
    cadence: Optional[str] = None
    interval_hours: Optional[int] = Field(None, ge=1, le=8760)
    enabled: Optional[bool] = None


class ScheduleResponse(ScheduleBase):
    id: str
    asset_name: Optional[str] = None
    asset_target: Optional[str] = None
    next_run: datetime
    last_run: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
