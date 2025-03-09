from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
    Text,
    Float,
    Boolean,
)
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone
from app.database import Base


class AppointmentStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class UserType(str, enum.Enum):
    REGULAR = "regular"
    SERVICE = "service"


class BaseDict:
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


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


class Appointment(Base, BaseDict):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    service_account_id = Column(Integer, ForeignKey("service_accounts.id"))
    appointment_date = Column(DateTime, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.ACTIVE)
    duration_minutes = Column(Integer, default=30)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    penalty = Column(Float, default=0.0)

    user = relationship("User", foreign_keys=[user_id], back_populates="appointments")
    service_account = relationship(
        "ServiceAccount",
        foreign_keys=[service_account_id],
        back_populates="appointments",
    )
