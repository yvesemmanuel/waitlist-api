"""
Response schemas.
"""

from typing import Optional, Any, Generic, TypeVar
from pydantic import BaseModel


T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str
    data: Optional[T] = None
    error: Optional[str] = None


class APIErrorResponse(BaseModel):
    success: bool = False
    message: str = "An error occurred"
    error: str
    data: Optional[Any] = None
