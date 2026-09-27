"""Pydantic schemas for Asset management."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class AssetBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    target: str = Field(..., min_length=1, max_length=253)
    description: Optional[str] = None
    environment: str = Field(
        "production", pattern="^(production|staging|development|internal)$"
    )
    owner: str = Field("Security Operations", max_length=100)
    criticality: str = Field("high", pattern="^(critical|high|medium|low)$")
    tags: str = Field("", description="Comma-separated tags")


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    environment: Optional[str] = Field(
        None, pattern="^(production|staging|development|internal)$"
    )
    owner: Optional[str] = Field(None, max_length=100)
    criticality: Optional[str] = Field(None, pattern="^(critical|high|medium|low)$")
    tags: Optional[str] = None


class AssetResponse(AssetBase):
    id: str
    created_at: datetime
    updated_at: datetime
    last_scanned_at: Optional[datetime] = None
    scan_status: str
    current_risk_score: int
    open_ports_count: int = 0
    vulnerabilities_count: int = 0

    model_config = ConfigDict(from_attributes=True)
