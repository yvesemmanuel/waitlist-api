from pydantic import BaseModel, field_validator, EmailStr, ConfigDict
from datetime import datetime, time, timezone
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


class PersonBase(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None

    @field_validator("phone")
    def validate_phone(cls, v):
        if not re.match(r"^\+\d{1,3}\d{6,14}$", v):
            raise ValueError(
                "Phone must be in the international format +[country_code][number]"
            )
        return v


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


class ServiceAccountCreate(PersonBase):
    description: Optional[str] = None
    enable_cancellation_scoring: bool = True
    cancellation_weight: float = 1.0
    no_show_weight: float = 2.0


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


class ServiceAccount(PersonBase):
    id: int
    description: Optional[str] = None
    created_at: datetime
    enable_cancellation_scoring: bool = True
    cancellation_weight: float = 1.0
    no_show_weight: float = 2.0

    model_config = ConfigDict(from_attributes=True)


class AppointmentBase(BaseModel):
    appointment_date: datetime
    duration_minutes: Optional[int] = 30
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    user_id: int
    service_account_id: int

    @field_validator("appointment_date", mode="before")
    def validate_appointment_date(cls, v):
        is_date_only = False

        if isinstance(v, str):
            try:
                dt = datetime.fromisoformat(v)
            except ValueError:
                try:
                    from datetime import date

                    parsed_date = date.fromisoformat(v)
                    dt = datetime.combine(parsed_date, time.min)
                    is_date_only = True
                except ValueError:
                    raise ValueError(
                        "Invalid date format. Use YYYY-MM-DD or YYYY-MM-DDThh:mm:ss"
                    )
        else:
            dt = v
            if isinstance(dt, datetime) and dt.time() == time.min:
                is_date_only = True

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)

        if is_date_only:
            input_date = dt.date()
            current_date = now.date()

            if input_date.year >= 2025:
                return dt

            if input_date <= current_date:
                raise ValueError("Appointment date must be in the future")
        else:
            if dt <= now:
                if dt.year >= 2025:
                    return dt

                raise ValueError("Appointment date must be in the future")

        return dt


class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatus] = None
    appointment_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None


class Appointment(AppointmentBase):
    id: int
    user_id: int
    service_account_id: int
    status: AppointmentStatus
    created_at: datetime
    penalty: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class AppointmentDetail(Appointment):
    user: User
    service_account: ServiceAccount


class UserWithAppointments(User):
    appointments: List[Appointment] = []


class ServiceAccountWithAppointments(ServiceAccount):
    appointments: List[Appointment] = []
