"""
User service.
"""

from sqlalchemy.orm import Session
from typing import Optional, List

from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User
from app.exceptions import UserAlreadyExists, UserNotFound


class UserService:
    """Service class containing user-related business logic"""

    @staticmethod
    def get_user(db: Session, phone: str) -> Optional[User]:
        """Retrieve a single user by phone number.

        Parameters:
        -----------
        db: Session
            Database session
        phone: str
            Phone number of user to retrieve

        Returns:
        --------
        User
            The User object if found

        Raises:
        --------
        UserNotFound: if user not found
        """
        user = db.query(User).filter(User.phone == phone).first()
        if not user:
            raise UserNotFound(phone)
        return user

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
        UserAlreadyExists: if user already exists
        """
        try:
            existing_user = UserService.get_user(db, user.phone)
            if existing_user:
                raise UserAlreadyExists(user.phone)
        except UserNotFound:
            pass

        db_user = User(**user.model_dump())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update_user(db: Session, phone: str, user: UserUpdate) -> Optional[User]:
        """Update user information with partial data.

        Parameters:
        -----------
        db: Session
            Database session
        phone: str
            Phone number of user to update
        user: UserUpdate
            User data to update

        Returns:
        --------
        User
            The updated User object

        Raises:
        --------
        UserNotFound: if user not found
        """
        db_user = UserService.get_user(db, phone)
        user_data = user.model_dump(exclude_unset=True)
        for key, value in user_data.items():
            if key != "phone" and value is not None:
                setattr(db_user, key, value)

        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(db: Session, phone: str) -> None:
        """Delete a user and return success status

        Parameters:
        -----------
        db: Session
            Database session
        phone: str
            Phone number of user to delete

        Returns:
        --------
        None

        Raises:
        --------
        UserNotFound: if user not found
        """
        db_user = UserService.get_user(db, phone)
        db.delete(db_user)
        db.commit()
