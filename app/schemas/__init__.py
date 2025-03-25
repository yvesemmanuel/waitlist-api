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
    PersonBase,
    User,
    UserCreate,
    UserUpdate,
)

from app.schemas.response import (
    APIResponse,
    APIErrorResponse,
)

from app.schemas.person import PersonBase


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
    "PersonBase",
    "User",
    "UserCreate",
    "UserUpdate",
    "APIResponse",
    "APIErrorResponse",
    "PersonBase",
]
