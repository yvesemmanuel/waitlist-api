"""
Appointment routers.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.schemas import (
    Appointment,
    AppointmentCreate,
    AppointmentDetail,
    APIResponse,
)
from app.services import AppointmentService
from app.models.database import get_db

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=APIResponse[Appointment],
    status_code=status.HTTP_201_CREATED,
)
async def create_appointment(
    appointment: AppointmentCreate, db: Session = Depends(get_db)
):
    appointment_model = AppointmentService.create_appointment(
        db=db, appointment=appointment
    )
    return APIResponse(
        message="Appointment created successfully", data=appointment_model.to_dict()
    )


@router.get(
    "/",
    response_model=APIResponse[List[Appointment]],
    status_code=status.HTTP_200_OK,
)
async def read_appointments(
    service_account_id: int = Query(..., description="The service account ID"),
    day: Optional[date] = Query(
        None, description="Optional: Filter by day (YYYY-MM-DD)"
    ),
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Get appointments for a service account, ranked as a queue.

    Appointments are ranked by:
    1. User's penalty value (lower penalty = higher priority)
    2. When the appointment was created (earlier creation = higher priority)

    This creates a queue where users who frequently cancel or no-show
    are deprioritized compared to reliable users.
    """
    ranked_appointments = AppointmentService.get_ranked_appointments(
        db=db,
        service_account_id=service_account_id,
        day=day,
        user_id=user_id,
        skip=skip,
        limit=limit,
    )
    return APIResponse(
        message="Appointments queue retrieved successfully",
        data=[appointment.to_dict() for appointment in ranked_appointments],
    )


@router.get(
    "/{appointment_id}",
    response_model=APIResponse[AppointmentDetail],
    status_code=status.HTTP_200_OK,
)
async def read_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment_detail = AppointmentService.get_appointment_detail(
        db, appointment_id=appointment_id
    )
    return APIResponse(
        message=f"Appointment {appointment_id} details retrieved successfully",
        data=appointment_detail,
    )


@router.delete(
    "/{appointment_id}",
    response_model=APIResponse[Appointment],
    status_code=status.HTTP_200_OK,
)
async def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):
    cancelled_appointment = AppointmentService.cancel_appointment(
        db, appointment_id=appointment_id
    )
    return APIResponse(
        message=f"Appointment {appointment_id} cancelled successfully",
        data=cancelled_appointment.to_dict(),
    )


@router.put(
    "/{appointment_id}/complete",
    response_model=APIResponse[Appointment],
    status_code=status.HTTP_200_OK,
)
async def complete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    completed_appointment = AppointmentService.complete_appointment(
        db, appointment_id=appointment_id
    )
    return APIResponse(
        message=f"Appointment {appointment_id} marked as completed",
        data=completed_appointment.to_dict(),
    )


@router.put(
    "/{appointment_id}/no-show",
    response_model=APIResponse[Appointment],
    status_code=status.HTTP_200_OK,
)
async def mark_no_show(appointment_id: int, db: Session = Depends(get_db)):
    no_show_appointment = AppointmentService.mark_no_show(
        db, appointment_id=appointment_id
    )
    return APIResponse(
        message=f"Appointment {appointment_id} marked as no-show",
        data=no_show_appointment.to_dict(),
    )
