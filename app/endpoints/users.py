from fastapi import APIRouter, Depends, HTTPException, status
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
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = crud.create_user(db=db, user=user)
        return schemas.APIResponse(message="User created successfully", data=db_user)
    except HTTPException as e:
        return schemas.APIErrorResponse(
            message="Failed to create user", error=str(e.detail)
        )


@router.get("/{user_id}", response_model=schemas.APIResponse[schemas.UserResponse])
def read_user(user_id: int, db: Session = Depends(get_db)):
    try:
        db_user = crud.get_user(db, user_id=user_id)
        if db_user is None:
            return schemas.APIErrorResponse(
                message="User not found",
                error="User with the specified ID does not exist",
            )
        return schemas.APIResponse(message="User retrieved successfully", data=db_user)
    except Exception as e:
        return schemas.APIErrorResponse(message="Failed to retrieve user", error=str(e))


@router.put("/{user_id}", response_model=schemas.APIResponse[schemas.User])
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    try:
        updated_user = crud.update_user(db=db, user_id=user_id, user=user)
        return schemas.APIResponse(
            message="User updated successfully", data=updated_user
        )
    except HTTPException as e:
        return schemas.APIErrorResponse(
            message="Failed to update user", error=str(e.detail)
        )


@router.delete("/{user_id}", response_model=schemas.APIResponse[dict])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        crud.delete_user(db=db, user_id=user_id)
        return schemas.APIResponse(
            message="User deleted successfully", data={"user_id": user_id}
        )
    except HTTPException as e:
        return schemas.APIErrorResponse(
            message="Failed to delete user", error=str(e.detail)
        )
