"""
Schemas for the application.
"""

from app.schemas.appointment import (
    Appointment,
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentDetail,
    UserWithAppointments,
    ServiceAccountWithAppointments,
)

from app.schemas.service_account import (
    ServiceAccount,
    ServiceAccountCreate,
    ServiceAccountUpdate,
)

from app.schemas.user import (
    BaseAccount,
    User,
    UserCreate,
    UserUpdate,
)

from app.schemas.response import (
    APIResponse,
)

from app.schemas.base import BaseAccount


__all__ = [
    "Appointment",
    "AppointmentCreate",
    "AppointmentUpdate",
    "AppointmentDetail",
    "UserWithAppointments",
    "ServiceAccountWithAppointments",
    "ServiceAccount",
    "ServiceAccountCreate",
    "ServiceAccountUpdate",
    "BaseAccount",
    "User",
    "UserCreate",
    "UserUpdate",
    "APIResponse",
    "BaseAccount",
]
