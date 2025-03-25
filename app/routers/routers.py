"""
Routers for the application.
"""

from fastapi import APIRouter

from app.routers.users import router as users_router
from app.routers.service_accounts import router as service_accounts_router
from app.routers.appointments import router as appointments_router


router = APIRouter()
router.include_router(users_router)
router.include_router(service_accounts_router)
router.include_router(appointments_router)


__all__ = ["router"]
