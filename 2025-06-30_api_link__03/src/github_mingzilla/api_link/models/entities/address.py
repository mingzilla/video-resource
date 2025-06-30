"""
Address entity model.
"""

# Third Party
from pydantic import BaseModel, Field


class Address(BaseModel):
    """Address model with validation."""

    line1: str = Field(..., description="First line of the address")
