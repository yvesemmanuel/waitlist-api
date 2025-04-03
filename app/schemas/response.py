"""
Response schemas.
"""

from typing import Optional, Generic, TypeVar
from pydantic import BaseModel


T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str
    data: Optional[T] = None
