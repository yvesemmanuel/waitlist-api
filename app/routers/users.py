"""
User routers.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.schemas import (
    User,
    UserCreate,
    UserUpdate,
    UserWithAppointments,
    APIResponse,
)
from app.services import (
    AppointmentService,
    UserService,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=APIResponse[User],
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = UserService.create_user(db=db, user=user)
    return APIResponse(message="User created successfully", data=db_user.to_dict())


@router.get(
    "/",
    response_model=APIResponse[List[User]],
    status_code=status.HTTP_200_OK,
)
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = UserService.get_users(db=db, skip=skip, limit=limit)
    return APIResponse(
        message="Users retrieved successfully",
        data=[user.to_dict() for user in users],
    )


@router.get(
    "/{user_id}",
    response_model=APIResponse[UserWithAppointments],
    status_code=status.HTTP_200_OK,
)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    user = UserService.get_user(db=db, user_id=user_id)
    user_appointments = AppointmentService.get_user_appointments(db=db, user_id=user_id)

    user_data = user.to_dict()
    user_data["appointments"] = [
        appointment.to_dict() for appointment in user_appointments
    ]

    return APIResponse(
        message=f"User with id {user_id} retrieved successfully", data=user_data
    )


@router.put(
    "/{user_id}",
    response_model=APIResponse[User],
    status_code=status.HTTP_200_OK,
)
async def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    updated_user = UserService.update_user(db=db, user_id=user_id, user=user)
    return APIResponse(
        message=f"User with id {user_id} updated successfully",
        data=updated_user.to_dict(),
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    UserService.delete_user(db=db, user_id=user_id)
    return None
