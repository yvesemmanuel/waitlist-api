"""
Person schemas.
"""

import re
from typing import Optional
from pydantic import BaseModel, field_validator, EmailStr


class PersonBase(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None

    @field_validator("phone")
    def validate_phone(cls, v):
        if not re.match(r"^\+\d{1,3}\d{6,14}$", v):
            raise ValueError(
                "Phone must be in the international format +[country_code][number]"
            )
        return v
