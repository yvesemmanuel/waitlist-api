import math
from sqlalchemy.orm import Session
from app import models, schemas
from datetime import datetime, time, date, timezone
from fastapi import HTTPException
from typing import Optional, List


def get_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    return user


def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone == phone).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get all regular users"""
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    existing_user = get_user_by_phone(db, user.phone)
    if existing_user:
        raise HTTPException(
            status_code=400, detail=f"User with phone {user.phone} already exists"
        )

    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = get_user(db, user_id)

    user_data = user.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        if key != "phone" and value is not None:
            setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)

    db.delete(db_user)
    db.commit()
    return {"success": True, "message": f"User with id {user_id} deleted"}


def get_service_account(db: Session, service_account_id: int):
    service_account = (
        db.query(models.ServiceAccount)
        .filter(models.ServiceAccount.id == service_account_id)
        .first()
    )
    if not service_account:
        raise HTTPException(
            status_code=404,
            detail=f"Service account with id {service_account_id} not found",
        )
    return service_account


def get_service_account_by_phone(db: Session, phone: str):
    return (
        db.query(models.ServiceAccount)
        .filter(models.ServiceAccount.phone == phone)
        .first()
    )


def get_service_accounts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ServiceAccount).offset(skip).limit(limit).all()


def create_service_account(
    db: Session, service_account: schemas.ServiceAccountCreate
) -> models.ServiceAccount:
    existing_account = get_service_account_by_phone(db, service_account.phone)
    if existing_account:
        raise HTTPException(
            status_code=400,
            detail=f"Service account with phone {service_account.phone} already exists",
        )

    db_service_account = models.ServiceAccount(**service_account.model_dump())
    db.add(db_service_account)
    db.commit()
    db.refresh(db_service_account)
    return db_service_account


def update_service_account(
    db: Session, service_account_id: int, service_account: schemas.ServiceAccountUpdate
):
    db_service_account = get_service_account(db, service_account_id)

    service_account_data = service_account.model_dump(exclude_unset=True)
    for key, value in service_account_data.items():
        if key != "phone" and value is not None:
            setattr(db_service_account, key, value)

    db.commit()
    db.refresh(db_service_account)
    return db_service_account


def delete_service_account(db: Session, service_account_id: int):
    db_service_account = get_service_account(db, service_account_id)

    db.delete(db_service_account)
    db.commit()
    return {
        "success": True,
        "message": f"Service account with id {service_account_id} deleted",
    }


def get_appointment(db: Session, appointment_id: int):
    appointment = (
        db.query(models.Appointment)
        .filter(models.Appointment.id == appointment_id)
        .first()
    )
    if not appointment:
        raise HTTPException(
            status_code=404, detail=f"Appointment with id {appointment_id} not found"
        )
    return appointment


def get_appointment_detail(db: Session, appointment_id: int):
    appointment = get_appointment(db, appointment_id)

    user = get_user(db, appointment.user_id)
    service_account = get_service_account(db, appointment.service_account_id)

    appointment_dict = appointment.to_dict()
    appointment_dict["user"] = user.to_dict()
    appointment_dict["service_account"] = service_account.to_dict()

    return appointment_dict


def get_appointments_for_day(
    db: Session,
    day: date,
    service_account_id: Optional[int] = None,
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
):
    start_of_day = datetime.combine(day, time.min)
    end_of_day = datetime.combine(day, time.max)

    query = db.query(models.Appointment).filter(
        models.Appointment.appointment_date >= start_of_day,
        models.Appointment.appointment_date <= end_of_day,
    )

    if service_account_id:
        query = query.filter(
            models.Appointment.service_account_id == service_account_id
        )

    if user_id:
        query = query.filter(models.Appointment.user_id == user_id)

    return query.offset(skip).limit(limit).all()


def create_appointment(db: Session, appointment: schemas.AppointmentCreate):
    """
    Create a new appointment in the queue system.

    In this system, users request an appointment for a specific day,
    but the exact time slot will be assigned by the service based on
    priority in the queue.
    """
    user = get_user(db, appointment.user_id)
    service_account = get_service_account(db, appointment.service_account_id)

    appointment_date = appointment.appointment_date
    appointment_day = datetime.combine(appointment_date.date(), time.min)
    if appointment_date.tzinfo:
        appointment_day = appointment_day.replace(tzinfo=appointment_date.tzinfo)
    else:
        appointment_day = appointment_day.replace(tzinfo=timezone.utc)

    appointment_day_start = datetime.combine(appointment_day.date(), time.min).replace(
        tzinfo=timezone.utc
    )
    appointment_day_end = datetime.combine(appointment_day.date(), time.max).replace(
        tzinfo=timezone.utc
    )

    existing_appointments = (
        db.query(models.Appointment)
        .filter(
            models.Appointment.user_id == user.id,
            models.Appointment.status == models.AppointmentStatus.ACTIVE,
            models.Appointment.appointment_date >= appointment_day_start,
            models.Appointment.appointment_date <= appointment_day_end,
        )
        .all()
    )

    if existing_appointments:
        raise HTTPException(
            status_code=400,
            detail="You already have an appointment scheduled for this day.",
        )

    penalty = calculate_user_penalty(db, user.id, service_account.id)

    appointment_data = appointment.model_dump()
    appointment_data["appointment_date"] = appointment_day
    appointment_data["status"] = models.AppointmentStatus.ACTIVE
    appointment_data["penalty"] = penalty

    db_appointment = models.Appointment(**appointment_data)
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


def calculate_user_penalty(db: Session, user_id: int, service_account_id: int) -> float:
    """
    Calculate a user reliability score based on appointment history.
    Returns a value between 0-1, where 0 is completely reliable and 1 is completely unreliable.
    """
    service_account = get_service_account(db, service_account_id)

    if not service_account.enable_cancellation_scoring:
        return 0.0

    cancellation_weight = service_account.cancellation_weight
    no_show_weight = service_account.no_show_weight

    total_weight = cancellation_weight + no_show_weight
    if total_weight == 0:
        return 0.0

    normalized_cancellation_weight = cancellation_weight / total_weight
    normalized_no_show_weight = no_show_weight / total_weight

    user_appointments = (
        db.query(models.Appointment)
        .filter(
            models.Appointment.user_id == user_id,
            models.Appointment.service_account_id == service_account_id,
        )
        .all()
    )

    if not user_appointments:
        return 0.0

    total_appointments = len(user_appointments)
    total_cancellations = 0
    total_no_shows = 0
    for appointment in user_appointments:
        if appointment.status == models.AppointmentStatus.CANCELED:
            total_cancellations += 1
        elif appointment.status == models.AppointmentStatus.NO_SHOW:
            total_no_shows += 1

    cancellation_rate = total_cancellations / total_appointments
    no_show_rate = total_no_shows / total_appointments

    recent_penalty = _calculate_recency_weighted_penalty(user_appointments)

    volume_factor = min(total_appointments, 1.0)

    base_penalty = (cancellation_rate * normalized_cancellation_weight) + (
        no_show_rate * normalized_no_show_weight
    )

    adjusted_penalty = base_penalty * (0.7 + (0.3 * recent_penalty))

    reliability_score = adjusted_penalty * volume_factor

    return reliability_score


def _calculate_recency_weighted_penalty(appointments: List[models.Appointment]):
    """
    Calculate a penalty that weighs recent appointment behavior more heavily.
    """
    if not appointments:
        return 0.0

    sorted_appointments = sorted(appointments, key=lambda a: a.created_at, reverse=True)

    today = datetime.now()
    total_weight = 0
    weighted_penalty = 0

    for appointment in sorted_appointments:
        days_ago = (today - appointment.created_at).days

        recency_weight = math.exp(-0.023 * days_ago)
        total_weight += recency_weight

        if appointment.status in [
            models.AppointmentStatus.CANCELED,
            models.AppointmentStatus.NO_SHOW,
        ]:
            penalty = (
                1.0 if appointment.status == models.AppointmentStatus.NO_SHOW else 0.7
            )
            weighted_penalty += penalty * recency_weight

    return weighted_penalty / total_weight if total_weight > 0 else 0.0


def cancel_appointment(db: Session, appointment_id: int):
    appointment = get_appointment(db, appointment_id)

    if appointment.status != models.AppointmentStatus.ACTIVE:
        status_display = appointment.status.value
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel appointment with status '{status_display}'. Only active appointments can be canceled.",
        )

    appointment.status = models.AppointmentStatus.CANCELED

    db.commit()
    db.refresh(appointment)
    return appointment


def complete_appointment(db: Session, appointment_id: int):
    appointment = get_appointment(db, appointment_id)
    appointment.status = models.AppointmentStatus.COMPLETED
    db.commit()
    db.refresh(appointment)
    return appointment


def mark_no_show(db: Session, appointment_id: int):
    appointment = get_appointment(db, appointment_id)
    appointment.status = models.AppointmentStatus.NO_SHOW

    db.commit()
    db.refresh(appointment)
    return appointment


def get_user_appointments(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    get_user(db, user_id)
    return (
        db.query(models.Appointment)
        .filter(models.Appointment.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_service_account_appointments(
    db: Session, service_account_id: int, skip: int = 0, limit: int = 100
):
    get_service_account(db, service_account_id)
    return (
        db.query(models.Appointment)
        .filter(models.Appointment.service_account_id == service_account_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_ranked_appointments_for_service_account(
    db: Session,
    service_account_id: int,
    day: Optional[date] = None,
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
):
    """
    Get appointments for a service account, ranked by a combination of:
    1. User's penalty value (lower penalty = higher priority)
    2. When the appointment was created (earlier creation = higher priority)

    This creates a queue where users who frequently cancel or no-show
    are deprioritized compared to reliable users.
    """
    get_service_account(db, service_account_id)

    query = db.query(models.Appointment).filter(
        models.Appointment.service_account_id == service_account_id,
        models.Appointment.status == models.AppointmentStatus.ACTIVE,
    )

    if user_id:
        query = query.filter(models.Appointment.user_id == user_id)

    if day:
        day_start = datetime.combine(day, time.min).replace(tzinfo=timezone.utc)
        day_end = datetime.combine(day, time.max).replace(tzinfo=timezone.utc)
        query = query.filter(
            models.Appointment.appointment_date >= day_start,
            models.Appointment.appointment_date <= day_end,
        )
    else:
        today = datetime.now(timezone.utc)
        query = query.filter(models.Appointment.appointment_date >= today)

    appointments = query.all()

    def rank_key(appointment):
        # Sort by penalty first (lower penalty = higher priority)
        # Then by creation time (earlier = higher priority)
        return (appointment.penalty, appointment.created_at)

    ranked_appointments = sorted(appointments, key=rank_key)

    paginated_appointments = ranked_appointments[skip : skip + limit]

    return paginated_appointments
