"""
Appointment service.
"""

import math
from sqlalchemy.orm import Session

from app.schemas import AppointmentCreate
from app.models.appointment import Appointment, AppointmentStatus
from datetime import datetime, time, date, timezone
from fastapi import HTTPException
from typing import Optional, List

from app.services.user import UserService
from app.services.service_account import ServiceAccountService


class AppointmentService:
    """Service class containing appointment-related business logic"""

    @staticmethod
    def get_appointment(db: Session, appointment_id: int) -> Appointment:
        """Retrieve a single appointment by ID.

        Parameters:
        -----------
        db: Session
            Database session
        appointment_id: int
            ID of appointment to retrieve

        Returns:
        --------
        Appointment
            The Appointment object if found

        Raises:
        -------
        HTTPException: 404 if appointment not found
        """
        db_appointment = (
            db.query(Appointment).filter(Appointment.id == appointment_id).first()
        )
        if not db_appointment:
            raise HTTPException(
                status_code=404,
                detail=f"Appointment with id {appointment_id} not found",
            )
        return db_appointment

    @staticmethod
    def get_appointment_detail(db: Session, appointment_id: int) -> dict:
        """Get detailed appointment information with user and service account data.

        Parameters:
        -----------
        db: Session
            Database session
        appointment_id: int
            ID of appointment to retrieve

        Returns:
        --------
        dict
            Combined appointment details with user and service account information
        """
        db_appointment = AppointmentService.get_appointment(db, appointment_id)
        user = UserService.get_user(db, db_appointment.user_id)
        service_account = ServiceAccountService.get_service_account(
            db, db_appointment.service_account_id
        )

        return {
            **db_appointment.to_dict(),
            "user": user.to_dict(),
            "service_account": service_account.to_dict(),
        }

    @staticmethod
    def get_appointments_for_day(
        db: Session,
        day: date,
        service_account_id: Optional[int] = None,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Appointment]:
        """Get paginated appointments for a specific day with optional filters.

        Parameters:
        -----------
        db: Session
            Database session
        day: date
            Date to filter appointments
        service_account_id: Optional[int]
            Filter by service account ID
        user_id: Optional[int]
            Filter by user ID
        skip: int
            Number of records to skip
        limit: int
            Maximum number of records to return

        Returns:
        --------
        List[Appointment]
            List of filtered appointments
        """
        start_of_day = datetime.combine(day, time.min).replace(tzinfo=timezone.utc)
        end_of_day = datetime.combine(day, time.max).replace(tzinfo=timezone.utc)

        query = db.query(Appointment).filter(
            Appointment.appointment_date >= start_of_day,
            Appointment.appointment_date <= end_of_day,
        )

        if service_account_id:
            query = query.filter(Appointment.service_account_id == service_account_id)

        if user_id:
            query = query.filter(Appointment.user_id == user_id)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def create_appointment(db: Session, appointment: AppointmentCreate) -> Appointment:
        """Create a new appointment with queue-based scheduling.

        Parameters:
        -----------
        db: Session
            Database session
        appointment: AppointmentCreate
            Appointment creation data

        Returns:
        --------
        Appointment
            Created appointment object

        Raises:
        -------
        HTTPException: 400 if duplicate appointment exists
        """
        user = UserService.get_user(db, appointment.user_id)
        service_account = ServiceAccountService.get_service_account(
            db, appointment.service_account_id
        )

        appointment_day_start = datetime.combine(
            appointment.appointment_date.date(), time.min
        ).replace(tzinfo=timezone.utc)

        appointment_day_end = datetime.combine(
            appointment.appointment_date.date(), time.max
        ).replace(tzinfo=timezone.utc)

        existing = (
            db.query(Appointment)
            .filter(
                Appointment.user_id == user.id,
                Appointment.status == AppointmentStatus.ACTIVE,
                Appointment.appointment_date >= appointment_day_start,
                Appointment.appointment_date <= appointment_day_end,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="You already have an appointment scheduled for this day",
            )

        penalty = AppointmentService.calculate_user_penalty(
            db, user.id, service_account.id
        )

        db_appointment = Appointment(
            **appointment.model_dump(),
            status=AppointmentStatus.ACTIVE,
            penalty=penalty,
        )

        db.add(db_appointment)
        db.commit()
        db.refresh(db_appointment)
        return db_appointment

    @staticmethod
    def calculate_user_penalty(
        db: Session, user_id: int, service_account_id: int
    ) -> float:
        """Calculate user reliability score based on historical behavior.

        Parameters:
        -----------
        db: Session
            Database session
        user_id: int
            Target user ID
        service_account_id: int
            Service account ID

        Returns:
        --------
        float
            Penalty score between 0 (reliable) and 1 (unreliable)
        """
        service_account = ServiceAccountService.get_service_account(
            db, service_account_id
        )

        if not service_account.enable_cancellation_scoring:
            return 0.0

        history = (
            db.query(Appointment)
            .filter(
                Appointment.user_id == user_id,
                Appointment.service_account_id == service_account_id,
            )
            .all()
        )

        if not history:
            return 0.0

        cancellation_weight = service_account.cancellation_weight
        no_show_weight = service_account.no_show_weight
        total_weight = cancellation_weight + no_show_weight

        if total_weight == 0:
            return 0.0

        norm_cancel = cancellation_weight / total_weight
        norm_no_show = no_show_weight / total_weight

        total = len(history)
        cancellations = sum(
            1 for a in history if a.status == AppointmentStatus.CANCELED
        )
        no_shows = sum(1 for a in history if a.status == AppointmentStatus.NO_SHOW)

        cancel_rate = cancellations / total
        no_show_rate = no_shows / total

        recent_penalty = AppointmentService._calculate_recency_weighted_penalty(history)
        volume_factor = min(total / 10, 1.0)  # Normalize over 10 appointments

        base_penalty = (cancel_rate * norm_cancel) + (no_show_rate * norm_no_show)
        adjusted_penalty = base_penalty * (0.7 + (0.3 * recent_penalty))

        return min(adjusted_penalty * volume_factor, 1.0)

    @staticmethod
    def _calculate_recency_weighted_penalty(
        appointments: List[Appointment],
    ) -> float:
        """Calculate recency-weighted penalty score.

        Parameters:
        -----------
        appointments: List[Appointment]
            List of user's historical appointments

        Returns:
        --------
        float
            Recency-adjusted penalty factor
        """
        if not appointments:
            return 0.0

        sorted_appts = sorted(appointments, key=lambda a: a.created_at, reverse=True)
        today = datetime.now(timezone.utc)
        total_weight = 0.0
        weighted_penalty = 0.0
        for apt in sorted_appts:
            created_at_utc = apt.created_at.replace(tzinfo=timezone.utc)
            days_old = (today - created_at_utc).days
            recency_weight = math.exp(-0.023 * days_old)  # Half-life of ~30 days

            if apt.status in [
                AppointmentStatus.CANCELED,
                AppointmentStatus.NO_SHOW,
            ]:
                penalty = 1.0 if apt.status == AppointmentStatus.NO_SHOW else 0.7
                weighted_penalty += penalty * recency_weight

            total_weight += recency_weight

        return weighted_penalty / total_weight if total_weight > 0 else 0.0

    @staticmethod
    def update_appointment_status(
        db: Session, appointment_id: int, new_status: AppointmentStatus
    ) -> Appointment:
        """Update appointment status with validation.

        Parameters:
        -----------
        db: Session
            Database session
        appointment_id: int
            Target appointment ID
        new_status: AppointmentStatus
            New status to set

        Returns:
        --------
        Appointment
            Updated appointment object
        """
        db_appointment = AppointmentService.get_appointment(db, appointment_id)

        if new_status == AppointmentStatus.CANCELED:
            if db_status != AppointmentStatus.ACTIVE:
                raise HTTPException(
                    status_code=400, detail="Only active appointments can be canceled"
                )

        db_status = new_status
        db.commit()
        db.refresh(db_appointment)
        return db_appointment

    @staticmethod
    def get_user_appointments(
        db: Session, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Appointment]:
        """Get paginated appointments for a specific user.

        Parameters:
        -----------
        db: Session
            Database session
        user_id: int
            Target user ID
        skip: int
            Number of records to skip
        limit: int
            Maximum number of records to return

        Returns:
        --------
        List[Appointment]
            List of user's appointments
        """
        UserService.get_user(db, user_id)
        return (
            db.query(Appointment)
            .filter(Appointment.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_service_account_appointments(
        db: Session, service_account_id: int, skip: int = 0, limit: int = 100
    ) -> List[Appointment]:
        """Get paginated appointments for a service account.

        Parameters:
        -----------
        db: Session
            Database session
        service_account_id: int
            Target service account ID
        skip: int
            Number of records to skip
        limit: int
            Maximum number of records to return

        Returns:
        --------
        List[Appointment]
            List of service account's appointments
        """
        ServiceAccountService.get_service_account(db, service_account_id)
        return (
            db.query(Appointment)
            .filter(Appointment.service_account_id == service_account_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_ranked_appointments(
        db: Session,
        service_account_id: int,
        day: Optional[date] = None,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Appointment]:
        """Get prioritized appointments based on penalty and creation time.

        Parameters:
        -----------
        db: Session
            Database session
        service_account_id: int
            Target service account ID
        day: Optional[date]
            Filter for specific day
        user_id: Optional[int]
            Filter for specific user
        skip: int
            Number of records to skip
        limit: int
            Maximum number of records to return

        Returns:
        --------
        List[Appointment]
            Prioritized list of appointments
        """
        base_query = db.query(Appointment).filter(
            Appointment.service_account_id == service_account_id,
            Appointment.status == AppointmentStatus.ACTIVE,
        )

        if user_id:
            base_query = base_query.filter(Appointment.user_id == user_id)

        if day:
            day_start = datetime.combine(day, time.min).replace(tzinfo=timezone.utc)
            day_end = datetime.combine(day, time.max).replace(tzinfo=timezone.utc)
            base_query = base_query.filter(
                Appointment.appointment_date >= day_start,
                Appointment.appointment_date <= day_end,
            )
        else:
            today = datetime.now(timezone.utc)
            base_query = base_query.filter(Appointment.appointment_date >= today)

        appointments = base_query.all()
        sorted_appointments = sorted(
            appointments, key=lambda x: (x.penalty, x.created_at)
        )

        return sorted_appointments[skip : skip + limit]

    @staticmethod
    def cancel_appointment(db: Session, appointment_id: int) -> Appointment:
        """Cancel an appointment.

        Parameters:
        -----------
        db: Session
            Database session
        appointment_id: int

        Returns:
        --------
        Appointment
            Cancelled appointment object
        """
        appointment = AppointmentService.get_appointment(db, appointment_id)

        if appointment.status != AppointmentStatus.ACTIVE:
            status_display = appointment.status.value
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel appointment with status '{status_display}'. Only active appointments can be canceled.",
            )

        appointment.status = AppointmentStatus.CANCELED

        db.commit()
        db.refresh(appointment)
        return appointment

    @staticmethod
    def complete_appointment(db: Session, appointment_id: int) -> Appointment:
        """Complete an appointment.

        Parameters:
        -----------
        db: Session
            Database session
        appointment_id: int

        Returns:
        --------
        Appointment
            Completed appointment object
        """
        appointment = AppointmentService.get_appointment(db, appointment_id)
        appointment.status = AppointmentStatus.COMPLETED
        db.commit()
        db.refresh(appointment)
        return appointment

    @staticmethod
    def mark_no_show(db: Session, appointment_id: int) -> Appointment:
        """Mark an appointment as no show.

        Parameters:
        -----------
        db: Session
            Database session
        appointment_id: int

        Returns:
        --------
        Appointment
            Marked no show appointment object
        """
        appointment = AppointmentService.get_appointment(db, appointment_id)
        appointment.status = AppointmentStatus.NO_SHOW

        db.commit()
        db.refresh(appointment)
        return appointment

    @staticmethod
    def get_user_appointments(
        db: Session, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Appointment]:
        """Get paginated appointments for a specific user.

        Parameters:
        -----------
        """
        UserService.get_user(db, user_id)
        return (
            db.query(Appointment)
            .filter(Appointment.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
