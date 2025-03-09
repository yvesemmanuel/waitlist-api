from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/service-accounts",
    tags=["service-accounts"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=schemas.APIResponse[schemas.ServiceAccount],
    status_code=status.HTTP_201_CREATED,
)
async def create_service_account(
    service_account: schemas.ServiceAccountCreate, db: Session = Depends(get_db)
):
    db_service_account = crud.create_service_account(
        db=db, service_account=service_account
    )
    return schemas.APIResponse(
        message="Service account created successfully",
        data=db_service_account.to_dict(),
    )


@router.get(
    "/",
    response_model=schemas.APIResponse[List[schemas.ServiceAccount]],
    status_code=status.HTTP_200_OK,
)
async def read_service_accounts(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    service_accounts = crud.get_service_accounts(db=db, skip=skip, limit=limit)
    return schemas.APIResponse(
        message="Service accounts retrieved successfully",
        data=[account.to_dict() for account in service_accounts],
    )


@router.get(
    "/{service_account_id}",
    response_model=schemas.APIResponse[schemas.ServiceAccountWithAppointments],
    status_code=status.HTTP_200_OK,
)
async def read_service_account(service_account_id: int, db: Session = Depends(get_db)):
    service_account = crud.get_service_account(
        db=db, service_account_id=service_account_id
    )
    service_appointments = crud.get_service_account_appointments(
        db=db, service_account_id=service_account_id
    )

    service_data = service_account.to_dict()
    service_data["appointments"] = [
        appointment.to_dict() for appointment in service_appointments
    ]

    return schemas.APIResponse(
        message=f"Service account with id {service_account_id} retrieved successfully",
        data=service_data,
    )


@router.put(
    "/{service_account_id}",
    response_model=schemas.APIResponse[schemas.ServiceAccount],
    status_code=status.HTTP_200_OK,
)
async def update_service_account(
    service_account_id: int,
    service_account: schemas.ServiceAccountUpdate,
    db: Session = Depends(get_db),
):
    updated_account = crud.update_service_account(
        db=db, service_account_id=service_account_id, service_account=service_account
    )
    return schemas.APIResponse(
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
    crud.delete_service_account(db=db, service_account_id=service_account_id)
    return None
