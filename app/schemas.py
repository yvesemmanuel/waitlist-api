from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List, Any, Generic, TypeVar
import re
from app.models import AppointmentStatus

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str
    data: Optional[T] = None
    error: Optional[str] = None


class APIErrorResponse(BaseModel):
    success: bool = False
    message: str = "An error occurred"
    error: str
    data: Optional[Any] = None


class UserBase(BaseModel):
    name: str
    phone: str

    @field_validator("phone")
    def validate_phone(cls, v):
        if not re.match(r"^\+55\d{10,11}$", v):
            raise ValueError("Phone must be in the format +55XXXXXXXXXXX")
        return v


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("phone")
    def validate_phone(cls, v):
        if v is None:
            return v
        if not re.match(r"^\+55\d{10,11}$", v):
            raise ValueError("Phone must be in the format +55XXXXXXXXXXX")
        return v


class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class AppointmentBase(BaseModel):
    appointment_date: datetime


class AppointmentCreate(AppointmentBase):
    user_id: int


class AppointmentUpdate(BaseModel):
    status: AppointmentStatus


class Appointment(AppointmentBase):
    id: int
    user_id: int
    status: AppointmentStatus
    created_at: datetime
    user: Optional[User] = None

    class Config:
        orm_mode = True


class UserResponse(User):
    appointments: List[Appointment] = []


class AppointmentResponse(Appointment):
    pass


class AppointmentListResponse(BaseModel):
    appointments: List[Appointment]
