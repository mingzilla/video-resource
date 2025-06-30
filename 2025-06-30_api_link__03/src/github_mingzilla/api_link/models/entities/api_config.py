"""
ApiConfig entity model.
"""

# Standard Library
# Python Standard Library
from datetime import datetime
from typing import Any, Dict, Optional

# Third Party
from pydantic import BaseModel, Field  # Added field_validator for Pydantic v2
from sqlalchemy import JSON, Column, DateTime, Integer, String, Text  # Added Text for longer strings
from sqlalchemy.sql import func  # For server_default timestamp

# First Party
from github_mingzilla.api_link.core.database import Database


class ApiConfigBase(BaseModel):
    """Base Pydantic model for ApiConfig, used for request/response validation."""

    name: str = Field(..., max_length=255, description="Unique name for the API configuration")
    description: Optional[str] = Field(default=None, description="Detailed description of the API configuration")
    endpoint: str = Field(..., max_length=2048, description="The full URL endpoint for the API request")
    method: str = Field(..., max_length=10, description="HTTP method (e.g., GET, POST, PUT, DELETE)")
    headers: Optional[Dict[str, Any]] = Field(default=None, description="JSON object storing request headers as key-value pairs")
    body_template: Optional[str] = Field(default=None, description="Template for the request body, can contain placeholders")
    params: Optional[Dict[str, Any]] = Field(default=None, description="JSON object or string storing query parameters template")

    # Pydantic V2 model_config
    model_config = {"from_attributes": True}  # Replaces orm_mode = True


class ApiConfigCreate(ApiConfigBase):
    """Pydantic model for creating an ApiConfig."""

    pass


class ApiConfigUpdate(ApiConfigBase):
    """Pydantic model for updating an ApiConfig. All fields are optional."""

    name: Optional[str] = Field(default=None, max_length=255)
    endpoint: Optional[str] = Field(default=None, max_length=2048)
    method: Optional[str] = Field(default=None, max_length=10)
    # headers, body_template, params, description remain Optional as in ApiConfigBase


class ApiConfig(ApiConfigBase):
    """Pydantic model for ApiConfig as stored in DB, includes ID and timestamps."""

    id: int = Field(..., description="Primary key for the API configuration")
    created_at: datetime = Field(..., description="Timestamp of creation")
    updated_at: datetime = Field(..., description="Timestamp of last update")

    # Pydantic V2 model_config
    model_config = {"from_attributes": True}


# SQLAlchemy entity
class ApiConfigEntity(Database.entity_base):
    """SQLAlchemy model for the api_config table."""

    __tablename__ = "api_config"

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name: str = Column(String(255), unique=True, index=True, nullable=False)
    description: Optional[str] = Column(Text, nullable=True)  # Using Text for potentially longer descriptions
    endpoint: str = Column(String(2048), nullable=False)
    method: str = Column(String(10), nullable=False)
    headers: Optional[Dict[str, Any]] = Column(JSON, nullable=True)
    body_template: Optional[str] = Column(Text, nullable=True)  # Using Text for potentially longer templates
    params: Optional[Dict[str, Any]] = Column(JSON, nullable=True)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
