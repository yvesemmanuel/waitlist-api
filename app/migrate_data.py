"""
Data migration script to convert the existing service/provider model to the new service account model.

This script:
1. Creates service accounts for each provider in the system
2. Updates all appointments to use the new service account IDs
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import User, UserType, Appointment

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_services_and_providers():
    """Migrate existing services and providers to the new service account model."""
    # Create a database session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Step 1: Check if we already have service accounts
        service_accounts = db.query(User).filter(User.is_service_account == True).all()
        if service_accounts:
            logger.warning(
                "Service accounts already exist. Migration may have already been run."
            )
            return

        # Step 2: Fetch all services and providers
        # Note: We'll use raw SQL queries to access old tables that might no longer be in the model
        try:
            services = db.execute(text("SELECT * FROM services")).fetchall()
            providers = db.execute(text("SELECT * FROM service_providers")).fetchall()

            logger.info(
                f"Found {len(services)} services and {len(providers)} providers to migrate"
            )
        except Exception as e:
            logger.error(f"Error fetching old tables: {str(e)}")
            logger.info(
                "This might be a fresh installation without old tables. Skipping migration."
            )
            return

        # Step 3: Create service accounts for each provider
        service_provider_mapping = {}  # Maps (service_id, provider_id) to new service_account_id

        for provider in providers:
            # Find the service for this provider
            service = next((s for s in services if s.id == provider.service_id), None)
            if not service:
                logger.warning(f"Could not find service for provider {provider.id}")
                continue

            # Create new service account
            name = f"{service.name} - {provider.name}"
            phone = (
                provider.phone or f"+00000000{provider.id}"
            )  # Placeholder if no phone

            new_service_account = User(
                name=name,
                phone=phone,
                email=provider.email,
                user_type=UserType.SERVICE,
                is_service_account=True,
                description=service.description,
            )

            db.add(new_service_account)
            db.flush()  # to get the new ID

            # Record the mapping
            service_provider_mapping[(service.id, provider.id)] = new_service_account.id

            logger.info(
                f"Created service account '{name}' with ID {new_service_account.id}"
            )

        # Step 4: Update appointments to use the new service accounts
        try:
            # First, add the new service_account_id column if it doesn't exist
            db.execute(
                text(
                    "ALTER TABLE appointments ADD COLUMN service_account_id INTEGER REFERENCES users(id)"
                )
            )
            logger.info("Added service_account_id column to appointments table")
        except Exception as e:
            logger.info(f"Column service_account_id might already exist: {str(e)}")

        # Get all appointments
        appointments = db.query(Appointment).all()

        for appointment in appointments:
            # Get the old service_id and provider_id using raw SQL
            # since these columns might not be in the model anymore
            try:
                old_data = db.execute(
                    text(
                        f"SELECT service_id, provider_id FROM appointments WHERE id = {appointment.id}"
                    )
                ).fetchone()

                if old_data:
                    old_service_id = old_data.service_id
                    old_provider_id = old_data.provider_id

                    # Find the corresponding service account
                    if (old_service_id, old_provider_id) in service_provider_mapping:
                        new_service_account_id = service_provider_mapping[
                            (old_service_id, old_provider_id)
                        ]

                        # Update the appointment
                        appointment.service_account_id = new_service_account_id
                        logger.info(
                            f"Updated appointment {appointment.id} to use service account {new_service_account_id}"
                        )
                    else:
                        logger.warning(
                            f"Could not find service account for appointment {appointment.id}"
                        )
            except Exception as e:
                logger.warning(f"Error updating appointment {appointment.id}: {str(e)}")

        # Step 5: Drop old columns and tables if they exist
        try:
            # Drop old columns from appointments table
            db.execute(text("ALTER TABLE appointments DROP COLUMN service_id"))
            db.execute(text("ALTER TABLE appointments DROP COLUMN provider_id"))
            logger.info("Dropped old columns from appointments table")

            # Drop old tables
            db.execute(text("DROP TABLE service_providers"))
            db.execute(text("DROP TABLE services"))
            logger.info("Dropped old tables")
        except Exception as e:
            logger.warning(f"Error dropping old schema elements: {str(e)}")

        # Commit all changes
        db.commit()
        logger.info("Migration completed successfully")

    except Exception as e:
        db.rollback()
        logger.error(f"Migration failed: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate_services_and_providers()
    logger.info("Migration script completed.")
