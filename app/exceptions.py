"""Exceptions module."""

from fastapi import HTTPException


class UserAlreadyExists(HTTPException):
    def __init__(self, phone: str):
        super().__init__(
            status_code=400, detail=f"User with phone {phone} already exists"
        )


class UserNotFound(HTTPException):
    def __init__(self, phone: str):
        super().__init__(status_code=404, detail=f"User with phone {phone} not found")


class ServiceAccountAlreadyExists(HTTPException):
    def __init__(self, phone: str):
        super().__init__(
            status_code=400, detail=f"Service account with phone {phone} already exists"
        )


class ServiceAccountNotFound(HTTPException):
    def __init__(self, phone: str):
        super().__init__(
            status_code=404, detail=f"Service account with phone {phone} not found"
        )


class AppointmentAlreadyExists(HTTPException):
    def __init__(self, phone: str):
        super().__init__(
            status_code=400, detail=f"Appointment with phone {phone} already exists"
        )


class AppointmentNotFound(HTTPException):
    def __init__(self, phone: str):
        super().__init__(
            status_code=404, detail=f"Appointment with phone {phone} not found"
        )
