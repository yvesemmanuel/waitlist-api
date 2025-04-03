"""
Appointment model.
"""

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    Enum,
    Text,
    Float,
    String,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from app.models.base import Base
from app.models.base import BaseDict


class AppointmentStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class Appointment(Base, BaseDict):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_phone = Column(String, ForeignKey("users.phone"))
    service_account_phone = Column(String, ForeignKey("service_accounts.phone"))
    appointment_date = Column(DateTime, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.ACTIVE)
    duration_minutes = Column(Integer, default=30)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    penalty = Column(Float, default=0.0)

    user = relationship(
        "User", foreign_keys=[user_phone], back_populates="appointments"
    )
    service_account = relationship(
        "ServiceAccount",
        foreign_keys=[service_account_phone],
        back_populates="appointments",
    )
