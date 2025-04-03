"""
Appointment schemas.
"""

from typing import Optional, List
from datetime import datetime, time, timezone
from pydantic import BaseModel, field_validator, ConfigDict

from app.models.appointment import AppointmentStatus
from app.schemas.user import User
from app.schemas.service_account import ServiceAccount


class AppointmentBase(BaseModel):
    appointment_date: datetime
    duration_minutes: Optional[int] = 30
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    user_phone: str
    service_account_phone: str

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
    user_phone: str
    service_account_phone: str
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
