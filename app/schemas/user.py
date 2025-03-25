"""
User schemas.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator, EmailStr, ConfigDict

from app.schemas.person import PersonBase


class UserCreate(PersonBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    @field_validator("phone")
    def validate_no_phone_change(cls, v):
        if v is not None:
            raise ValueError("Phone number cannot be changed")
        return v


class User(PersonBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
