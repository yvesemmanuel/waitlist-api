from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/", response_model=schemas.APIResponse[schemas.Appointment], status_code=201
)
def create_appointment(
    appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)
):
    try:
        db_appointment = crud.create_appointment(db=db, appointment=appointment)
        return schemas.APIResponse(
            message="Appointment created successfully", data=db_appointment
        )
    except HTTPException as e:
        return schemas.APIErrorResponse(
            message="Failed to create appointment", error=str(e.detail)
        )


@router.get("/", response_model=schemas.APIResponse[List[schemas.Appointment]])
def read_appointments(
    day: date = Query(..., description="The day to get appointments for (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    try:
        appointments = crud.get_appointments_for_day(
            db=db, day=day, skip=skip, limit=limit
        )
        return schemas.APIResponse(
            message="Appointments retrieved successfully", data=appointments
        )
    except Exception as e:
        return schemas.APIErrorResponse(
            message="Failed to retrieve appointments", error=str(e)
        )


@router.delete(
    "/{appointment_id}", response_model=schemas.APIResponse[schemas.Appointment]
)
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):
    try:
        canceled_appointment = crud.cancel_appointment(
            db=db, appointment_id=appointment_id
        )
        return schemas.APIResponse(
            message="Appointment canceled successfully", data=canceled_appointment
        )
    except HTTPException as e:
        return schemas.APIErrorResponse(
            message="Failed to cancel appointment", error=str(e.detail)
        )
