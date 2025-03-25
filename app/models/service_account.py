"""
Service model.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Float,
    Boolean,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.models.base import Base
from app.models.base import BaseDict


class ServiceAccount(Base, BaseDict):
    __tablename__ = "service_accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    enable_cancellation_scoring = Column(Boolean, default=True)
    cancellation_weight = Column(Float, default=1.0)
    no_show_weight = Column(Float, default=2.0)

    appointments = relationship(
        "Appointment",
        foreign_keys="[Appointment.service_account_id]",
        back_populates="service_account",
    )
