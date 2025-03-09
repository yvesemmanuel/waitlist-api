from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=schemas.APIResponse[schemas.User],
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.create_user(db=db, user=user)
    return schemas.APIResponse(
        message="User created successfully", data=db_user.to_dict()
    )


@router.get(
    "/",
    response_model=schemas.APIResponse[List[schemas.User]],
    status_code=status.HTTP_200_OK,
)
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db=db, skip=skip, limit=limit)
    return schemas.APIResponse(
        message="Users retrieved successfully",
        data=[user.to_dict() for user in users],
    )


@router.get(
    "/{user_id}",
    response_model=schemas.APIResponse[schemas.UserWithAppointments],
    status_code=status.HTTP_200_OK,
)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db=db, user_id=user_id)
    user_appointments = crud.get_user_appointments(db=db, user_id=user_id)

    user_data = user.to_dict()
    user_data["appointments"] = [
        appointment.to_dict() for appointment in user_appointments
    ]

    return schemas.APIResponse(
        message=f"User with id {user_id} retrieved successfully", data=user_data
    )


@router.put(
    "/{user_id}",
    response_model=schemas.APIResponse[schemas.User],
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)
):
    updated_user = crud.update_user(db=db, user_id=user_id, user=user)
    return schemas.APIResponse(
        message=f"User with id {user_id} updated successfully",
        data=updated_user.to_dict(),
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    crud.delete_user(db=db, user_id=user_id)
    return None
