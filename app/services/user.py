"""
User service.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional, List

from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User


class UserService:
    """Service class containing user-related business logic"""

    @staticmethod
    def get_user(db: Session, user_id: int) -> User:
        """Retrieve a single user by ID.

        Parameters:
        -----------
        db: Session
            Database session
        user_id: int
            ID of user to retrieve

        Returns:
        --------
        User
            The User object if found

        Raises:
        --------
        HTTPException: 404 if user not found
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=404, detail=f"User with id {user_id} not found"
            )
        return user

    @staticmethod
    def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
        """Find a user by their phone number

        Parameters:
        -----------
        db: Session
            Database session
        phone: str
            Phone number of user to retrieve

        Returns:
        --------
        User | None
            The User object if found, otherwise None
        """
        return db.query(User).filter(User.phone == phone).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Retrieve paginated list of all regular users

        Parameters:
        -----------
        db: Session
            Database session
        skip: int
            Number of users to skip
        limit: int
            Number of users to retrieve

        Returns:
        --------
        List[User]
        """
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """Create a new user with phone number validation.

        Parameters:
        -----------
        db: Session
            Database session
        user: UserCreate
            User to create

        Returns:
        --------
        User
            The created User object

        Raises:
        --------
        HTTPException: 400 if user already exists
        """
        existing_user = UserService.get_user_by_phone(db, user.phone)
        if existing_user:
            raise HTTPException(
                status_code=400, detail=f"User with phone {user.phone} already exists"
            )

        db_user = User(**user.model_dump())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update_user(db: Session, user_id: int, user: UserUpdate) -> User:
        """Update user information with partial data.

        Parameters:
        -----------
        db: Session
            Database session
        user_id: int
            ID of user to update
        user: UserUpdate
            User data to update

        Returns:
        --------
        User
            The updated User object
        """
        db_user = UserService.get_user(db, user_id)
        user_data = user.model_dump(exclude_unset=True)
        for key, value in user_data.items():
            if key != "phone" and value is not None:
                setattr(db_user, key, value)

        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> dict:
        """Delete a user and return success status

        Parameters:
        -----------
        db: Session
            Database session
        user_id: int
            ID of user to delete

        Returns:
        --------
        dict
            Success status
        """
        db_user = UserService.get_user(db, user_id)
        db.delete(db_user)
        db.commit()
        return {"success": True, "message": f"User with id {user_id} deleted"}
