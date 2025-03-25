"""
User model.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum,
    Text,
    Boolean,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from app.models.base import Base
from app.models.base import BaseDict


class UserType(str, enum.Enum):
    REGULAR = "regular"
    SERVICE = "service"


class User(Base, BaseDict):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_type = Column(Enum(UserType), default=UserType.REGULAR)

    is_service_account = Column(Boolean, default=False)
    description = Column(Text, nullable=True)

    appointments = relationship(
        "Appointment", foreign_keys="[Appointment.user_id]", back_populates="user"
    )
