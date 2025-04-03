"""
Service account schemas.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator, EmailStr, ConfigDict

from app.schemas.base import BaseAccount


class ServiceAccountCreate(BaseAccount):
    description: Optional[str] = None
    enable_cancellation_scoring: Optional[bool] = True
    cancellation_weight: Optional[float] = 1.0
    no_show_weight: Optional[float] = 2.0


class ServiceAccountUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    enable_cancellation_scoring: Optional[bool] = None
    cancellation_weight: Optional[float] = None
    no_show_weight: Optional[float] = None

    @field_validator("phone")
    def validate_no_phone_change(cls, v):
        if v is not None:
            raise ValueError("Phone number cannot be changed")
        return v


class ServiceAccount(BaseAccount):
    id: int
    description: Optional[str] = None
    created_at: datetime
    enable_cancellation_scoring: Optional[bool] = True
    cancellation_weight: Optional[float] = 1.0
    no_show_weight: Optional[float] = 2.0

    model_config = ConfigDict(from_attributes=True)
