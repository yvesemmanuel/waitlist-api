"""
Service account routers.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.schemas import (
    ServiceAccount,
    ServiceAccountCreate,
    ServiceAccountUpdate,
    ServiceAccountWithAppointments,
    APIResponse,
)
from app.services import (
    ServiceAccountService,
    AppointmentService,
)

router = APIRouter(
    prefix="/service-accounts",
    tags=["service-accounts"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=APIResponse[ServiceAccount],
    status_code=status.HTTP_201_CREATED,
)
async def create_service_account(
    service_account: ServiceAccountCreate, db: Session = Depends(get_db)
):
    db_service_account = ServiceAccountService.create_service_account(
        db=db, service_account=service_account
    )
    return APIResponse(
        message="Service account created successfully",
        data=db_service_account.to_dict(),
    )


@router.get(
    "/",
    response_model=APIResponse[List[ServiceAccount]],
    status_code=status.HTTP_200_OK,
)
async def read_service_accounts(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    service_accounts = ServiceAccountService.get_service_accounts(
        db=db, skip=skip, limit=limit
    )
    return APIResponse(
        message="Service accounts retrieved successfully",
        data=[account.to_dict() for account in service_accounts],
    )


@router.get(
    "/{service_account_id}",
    response_model=APIResponse[ServiceAccountWithAppointments],
    status_code=status.HTTP_200_OK,
)
async def read_service_account(service_account_id: int, db: Session = Depends(get_db)):
    service_account = ServiceAccountService.get_service_account(
        db=db, service_account_id=service_account_id
    )
    service_appointments = AppointmentService.get_service_account_appointments(
        db=db, service_account_id=service_account_id
    )

    service_data = service_account.to_dict()
    service_data["appointments"] = [
        appointment.to_dict() for appointment in service_appointments
    ]

    return APIResponse(
        message=f"Service account with id {service_account_id} retrieved successfully",
        data=service_data,
    )


@router.put(
    "/{service_account_id}",
    response_model=APIResponse[ServiceAccount],
    status_code=status.HTTP_200_OK,
)
async def update_service_account(
    service_account_id: int,
    service_account: ServiceAccountUpdate,
    db: Session = Depends(get_db),
):
    updated_account = ServiceAccountService.update_service_account(
        db=db, service_account_id=service_account_id, service_account=service_account
    )
    return APIResponse(
        message=f"Service account with id {service_account_id} updated successfully",
        data=updated_account.to_dict(),
    )


@router.delete(
    "/{service_account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_service_account(
    service_account_id: int, db: Session = Depends(get_db)
):
    ServiceAccountService.delete_service_account(
        db=db, service_account_id=service_account_id
    )
    return None
