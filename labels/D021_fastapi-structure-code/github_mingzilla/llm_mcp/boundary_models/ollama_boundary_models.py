"""Ollama API boundary models with Ollama* prefix.

This module contains boundary models for external Ollama API:
- Ollama API response models with from_dict() conversion
- Type-safe boundaries for Ollama integrations
"""

from typing import Any, List, Optional

from pydantic import BaseModel, Field, ValidationError


class OllamaModel(BaseModel):
    """Type-safe model for individual Ollama model."""

    name: str = Field(..., description="Model name")
    size: Optional[int] = Field(None, description="Model size in bytes")
    digest: Optional[str] = Field(None, description="Model digest")
    modified_at: Optional[str] = Field(None, description="Last modified timestamp")

    @classmethod
    def from_dict(cls, data: Any) -> "OllamaModel":
        """Convert Ollama model dict to typed model.

        Args:
            data: Raw model dict from Ollama API or object with attributes

        Returns:
            Typed OllamaModel object

        Raises:
            ValidationError: If conversion fails, indicating Ollama API change
        """
        if hasattr(data, "name"):
            # Convert object with attributes
            return cls(name=data.name, size=getattr(data, "size", None), digest=getattr(data, "digest", None), modified_at=getattr(data, "modified_at", None))
        elif isinstance(data, dict):
            return cls.model_validate(data)
        else:
            # Use model_validate to trigger proper ValidationError
            return cls.model_validate(data)


class OllamaModelsResponse(BaseModel):
    """Type-safe model for Ollama models list response."""

    models: List[OllamaModel] = Field(..., description="List of available models")

    @classmethod
    def from_dict(cls, data: Any) -> "OllamaModelsResponse":
        """Convert Ollama models response to typed model.

        Args:
            data: Raw JSON response from Ollama models API or object with attributes

        Returns:
            Typed OllamaModelsResponse object

        Raises:
            ValidationError: If conversion fails, indicating Ollama API change
        """
        if hasattr(data, "models"):
            # Convert object with attributes
            try:
                models = []
                for model in data.models:
                    if model is None:
                        # This should cause a validation error
                        raise ValidationError.from_exception_data(
                            "ValidationError",
                            [
                                {
                                    "type": "missing",
                                    "loc": ("models",),
                                    "msg": "None value not allowed in models list",
                                    "input": model,
                                }
                            ],
                        )
                    try:
                        models.append(OllamaModel.from_dict(model))
                    except (ValueError, ValidationError) as e:
                        # Convert ValueError to ValidationError or re-raise ValidationError for test compatibility
                        if isinstance(e, ValidationError):
                            raise
                        raise ValidationError.from_exception_data(
                            "ValidationError",
                            [
                                {
                                    "type": "value_error",
                                    "loc": ("models",),
                                    "msg": str(e),
                                    "input": model,
                                }
                            ],
                        )
                return cls(models=models)
            except AttributeError:
                # Re-raise AttributeError for missing attributes
                raise
        elif isinstance(data, dict) and "models" in data:
            # Convert model dicts to typed models - validate each model
            models = []
            for model in data["models"]:
                if model is None:
                    # This should cause a validation error
                    raise ValidationError.from_exception_data(
                        "ValidationError",
                        [
                            {
                                "type": "missing",
                                "loc": ("models",),
                                "msg": "None value not allowed in models list",
                                "input": model,
                            }
                        ],
                    )
                # Let ValidationError from OllamaModel.from_dict propagate naturally
                models.append(OllamaModel.from_dict(model))
            return cls(models=models)
        elif isinstance(data, dict):
            return cls.model_validate(data)
        else:
            # Try to access attributes - differentiate between object missing attributes vs invalid types
            try:
                # Check if this looks like an object that should have attributes
                if hasattr(data, "__dict__") or hasattr(data, "__slots__"):
                    # This is an object - let AttributeError propagate for missing attributes
                    models = []
                    for model in data.models:
                        if model is None:
                            raise ValidationError.from_exception_data(
                                "ValidationError",
                                [
                                    {
                                        "type": "missing",
                                        "loc": ("models",),
                                        "msg": "None value not allowed in models list",
                                        "input": model,
                                    }
                                ],
                            )
                        try:
                            models.append(OllamaModel.from_dict(model))
                        except (ValueError, ValidationError) as e:
                            # Convert ValueError to ValidationError or re-raise ValidationError for test compatibility
                            if isinstance(e, ValidationError):
                                raise
                            raise ValidationError.from_exception_data(
                                "ValidationError",
                                [
                                    {
                                        "type": "value_error",
                                        "loc": ("models",),
                                        "msg": str(e),
                                        "input": model,
                                    }
                                ],
                            )
                    return cls(models=models)
                else:
                    # This is not an object type - raise ValueError
                    raise ValueError(f"Unexpected Ollama response format: {type(data)}")
            except AttributeError:
                # Re-raise AttributeError for missing attributes on actual objects
                raise
            except Exception:
                raise ValueError(f"Unexpected Ollama response format: {type(data)}")
