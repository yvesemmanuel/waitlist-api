from sqlalchemy.orm import Session
from app import models, schemas
from datetime import datetime, time, date
from fastapi import HTTPException


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone == phone).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    existing_user = get_user_by_phone(db, user.phone)
    if existing_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user.dict(exclude_unset=True)

    if "phone" in update_data and update_data["phone"] is not None:
        existing_user = get_user_by_phone(db, update_data["phone"])
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=400, detail="Phone number already registered"
            )

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    active_appointments = (
        db.query(models.Appointment)
        .filter(
            models.Appointment.user_id == user_id,
            models.Appointment.status == models.AppointmentStatus.ACTIVE,
        )
        .count()
    )

    if active_appointments > 0:
        raise HTTPException(
            status_code=400, detail="Cannot delete user with active appointments"
        )

    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}


def get_appointment(db: Session, appointment_id: int):
    return (
        db.query(models.Appointment)
        .filter(models.Appointment.id == appointment_id)
        .first()
    )


def get_appointments_for_day(db: Session, day: date, skip: int = 0, limit: int = 100):
    start_datetime = datetime.combine(day, time.min)
    end_datetime = datetime.combine(day, time.max)

    return (
        db.query(models.Appointment)
        .filter(
            models.Appointment.appointment_date >= start_datetime,
            models.Appointment.appointment_date <= end_datetime,
        )
        .order_by(models.Appointment.appointment_date)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_appointment(db: Session, appointment: schemas.AppointmentCreate):
    user = get_user(db, appointment.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    appointment_date = appointment.appointment_date.date()

    existing_appointment = (
        db.query(models.Appointment)
        .filter(
            models.Appointment.user_id == appointment.user_id,
            models.Appointment.status == models.AppointmentStatus.ACTIVE,
            models.Appointment.appointment_date
            >= datetime.combine(appointment_date, time.min),
            models.Appointment.appointment_date
            <= datetime.combine(appointment_date, time.max),
        )
        .first()
    )

    if existing_appointment:
        raise HTTPException(
            status_code=400,
            detail="User already has an active appointment for this day",
        )

    db_appointment = models.Appointment(**appointment.model_dump())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


def cancel_appointment(db: Session, appointment_id: int):
    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if db_appointment.status == models.AppointmentStatus.CANCELED:
        raise HTTPException(status_code=400, detail="Appointment is already canceled")

    db_appointment.status = models.AppointmentStatus.CANCELED
    db.commit()
    db.refresh(db_appointment)
    return db_appointment
