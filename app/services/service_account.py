"""
Service account service.
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.schemas.service_account import ServiceAccountCreate, ServiceAccountUpdate
from app.models.service_account import ServiceAccount
from app.exceptions import ServiceAccountAlreadyExists, ServiceAccountNotFound


class ServiceAccountService:
    """Service class containing service account-related business logic"""

    @staticmethod
    def get_service_account(db: Session, phone: str) -> Optional[ServiceAccount]:
        """Retrieve a single service account by phone number.

        Parameters:
        -----------
        db: Session
            Database session
        phone: str
            Phone number of service account to retrieve

        Returns:
        --------
        ServiceAccount
            The ServiceAccount object if found

        Raises:
        --------
        ServiceAccountNotFound: if service account not found
        """
        service_account = (
            db.query(ServiceAccount).filter(ServiceAccount.phone == phone).first()
        )
        if not service_account:
            raise ServiceAccountNotFound(phone)
        return service_account

    @staticmethod
    def get_service_accounts(
        db: Session, skip: int = 0, limit: int = 100
    ) -> List[ServiceAccount]:
        """Retrieve paginated list of all service accounts

        Parameters:
        -----------
        db: Session
            Database session
        skip: int
            Number of service accounts to skip
        limit: int
            Number of service accounts to retrieve

        Returns:
        --------
        List[ServiceAccount]
            The list of ServiceAccount objects
        """
        return db.query(ServiceAccount).offset(skip).limit(limit).all()

    @staticmethod
    def create_service_account(
        db: Session, service_account: ServiceAccountCreate
    ) -> ServiceAccount:
        """Create a new service account with phone number validation.

        Parameters:
        -----------
        db: Session
            Database session
        service_account: ServiceAccountCreate
            Service account to create

        Returns:
        --------
        ServiceAccount
            The created ServiceAccount object

        Raises:
        --------
        ServiceAccountAlreadyExists: if service account already exists
        """
        try:
            existing_account = ServiceAccountService.get_service_account(
                db, service_account.phone
            )
            if existing_account:
                raise ServiceAccountAlreadyExists(service_account.phone)
        except ServiceAccountNotFound:
            pass

        db_service_account = ServiceAccount(**service_account.model_dump())
        db.add(db_service_account)
        db.commit()
        db.refresh(db_service_account)
        return db_service_account

    @staticmethod
    def update_service_account(
        db: Session,
        phone: str,
        service_account: ServiceAccountUpdate,
    ) -> ServiceAccount:
        """Update service account information with partial data.

        Parameters:
        -----------
        db: Session
            Database session
        phone: str
            Phone number of service account to update
        service_account: ServiceAccountUpdate
            Service account data to update

        Returns:
        --------
        ServiceAccount
            The updated ServiceAccount object
        """
        db_service_account = ServiceAccountService.get_service_account(db, phone)
        service_account_data = service_account.model_dump(exclude_unset=True)
        for key, value in service_account_data.items():
            if key != "phone" and value is not None:
                setattr(db_service_account, key, value)

        db.commit()
        db.refresh(db_service_account)
        return db_service_account

    @staticmethod
    def delete_service_account(db: Session, phone: str) -> dict:
        """Delete a service account and return success status

        Parameters:
        -----------
        db: Session
            Database session
        phone: str
            Phone number of service account to delete

        Raises:
        --------
        ServiceAccountNotFound: if service account not found
        """
        db_service_account = ServiceAccountService.get_service_account(db, phone)
        db.delete(db_service_account)
        db.commit()
        return {
            "success": True,
            "message": f"Service account with phone {phone} deleted",
        }
