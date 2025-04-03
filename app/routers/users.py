"""
User routers.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.backend.session import get_db
from app.schemas import (
    User,
    UserCreate,
    UserUpdate,
    UserWithAppointments,
    APIResponse,
)
from app.services import (
    UserService,
)
from app.exceptions import UserAlreadyExists, UserNotFound


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
    try:
        db_user = UserService.create_user(db=db, user=user)
        return APIResponse(message="User created successfully", data=db_user.to_dict())
    except UserAlreadyExists as e:
        raise e


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
    "/{phone}",
    response_model=APIResponse[UserWithAppointments],
    status_code=status.HTTP_200_OK,
)
async def read_user(phone: str, db: Session = Depends(get_db)):
    try:
        user = UserService.get_user(db=db, phone=phone)
        return APIResponse(
            message=f"User with phone {phone} retrieved successfully",
            data=user.to_dict(),
        )
    except UserNotFound as e:
        raise e


@router.put(
    "/{phone}",
    response_model=APIResponse[User],
    status_code=status.HTTP_200_OK,
)
async def update_user(phone: str, user: UserUpdate, db: Session = Depends(get_db)):
    try:
        updated_user = UserService.update_user(db=db, phone=phone, user=user)
        return APIResponse(
            message=f"User with phone {phone} updated successfully",
            data=updated_user.to_dict(),
        )
    except UserNotFound as e:
        raise e


@router.delete(
    "/{phone}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(phone: str, db: Session = Depends(get_db)):
    try:
        UserService.delete_user(db=db, phone=phone)
        return None
    except UserNotFound as e:
        raise e
