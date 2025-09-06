"""Static utility class for environment variable reading and validation.

Key Design Principles:
- Static utility class - NO INSTANTIATION ALLOWED
- Environment variable validation at entry point (first line of main.py)
- Fail-fast principle - any config error stops the system immediately
- Explicit parameters - NO default values in method signatures
- Two-line usage pattern: read then validate
- Uses load_dotenv(override=False) to respect priority hierarchy: existing envvar > .env > fallback

Usage Example:
    EnvVarReader.load_dotenv()
    
    # Two-line pattern: read then validate
    batch_size: int = EnvVarReader.get_int("BATCH_SIZE", "10") 
    EnvVarReader.number_min("BATCH_SIZE", batch_size, 1)
    EnvVarReader.number_max("BATCH_SIZE", batch_size, 100)
"""

import os
import re
from pathlib import Path
from typing import Optional, Union, List

from dotenv import load_dotenv


class EnvVarReader:
    """Static utility for environment variable reading and validation.
    
    CRITICAL: This is a static utility class. Do not instantiate.
    """

    def __init__(self):
        raise RuntimeError("EnvVarReader is a static utility class - do not instantiate. Use EnvVarReader.method_name() directly.")

    @staticmethod
    def load_dotenv():
        """Load environment variables with guaranteed override=False priority."""
        load_dotenv(override=False)

    # === CORE READING METHODS ===

    @staticmethod
    def get_str(name: str, fallback: str) -> str:
        """Read string environment variable with explicit fallback.
        
        Args:
            name: Environment variable name
            fallback: Explicit fallback value (cannot be None)
            
        Returns:
            String value from env var or fallback
        """
        return os.getenv(name, fallback)

    @staticmethod
    def get_int(name: str, fallback: str) -> Optional[int]:
        """Read integer environment variable with explicit fallback.
        
        Args:
            name: Environment variable name  
            fallback: Explicit fallback value as string, or None for no fallback
            
        Returns:
            Integer value or None if fallback was None
            
        Raises:
            ValueError: If value cannot be converted to integer
        """
        v = os.getenv(name, fallback)

        try:
            if v is None:
                return None
            return int(v)
        except ValueError:
            raise ValueError(f"{name} must be integer, got: {v}")

    @staticmethod
    def get_float(name: str, fallback: str) -> Optional[float]:
        """Read float environment variable with explicit fallback.
        
        Args:
            name: Environment variable name
            fallback: Explicit fallback value as string, or None for no fallback
            
        Returns:
            Float value or None if fallback was None
            
        Raises:
            ValueError: If value cannot be converted to float
        """
        v = os.getenv(name, fallback)

        try:
            if v is None:
                return None
            return float(v)
        except ValueError:
            raise ValueError(f"{name} must be float, got: {v}")

    @staticmethod
    def get_bool(name: str, fallback: str) -> bool:
        """Read boolean environment variable with explicit fallback.
        
        Args:
            name: Environment variable name
            fallback: Explicit fallback value as string
            
        Returns:
            Boolean value (true/1/yes/on are True, everything else is False)
        """
        v = os.getenv(name, fallback)
        return v.lower() in ('true', '1', 'yes', 'on')

    # === STRING VALIDATION METHODS ===

    @staticmethod
    def str_min_length(name: str, v: str, v_min_length: int):
        """Validate string minimum length.
        
        Args:
            name: Field name for error messages
            v: String value to validate
            v_min_length: Minimum required length
            
        Raises:
            ValueError: If string is shorter than minimum
        """
        if len(v) < v_min_length:
            raise ValueError(f"{name} must be at least {v_min_length} characters, got: {len(v)}")

    @staticmethod
    def str_max_length(name: str, v: str, v_max_length: int):
        """Validate string maximum length.
        
        Args:
            name: Field name for error messages
            v: String value to validate
            v_max_length: Maximum allowed length
            
        Raises:
            ValueError: If string is longer than maximum
        """
        if len(v) > v_max_length:
            raise ValueError(f"{name} must be at most {v_max_length} characters, got: {len(v)}")

    @staticmethod
    def str_allowed_values(name: str, v: str, v_allowed_values: List[str]):
        """Validate string is in allowed values list.
        
        Args:
            name: Field name for error messages
            v: String value to validate
            v_allowed_values: List of allowed values
            
        Raises:
            ValueError: If value is not in allowed list
        """
        if v not in v_allowed_values:
            raise ValueError(f"{name} must be one of {v_allowed_values}, got: {v}")

    @staticmethod
    def str_regex_match(name: str, v: str, v_pattern: str):
        """Validate string matches regex pattern.
        
        Args:
            name: Field name for error messages
            v: String value to validate
            v_pattern: Regex pattern to match
            
        Raises:
            ValueError: If string doesn't match pattern
        """
        if not re.match(v_pattern, v):
            raise ValueError(f"{name} must match pattern '{v_pattern}', got: {v}")

    # === NUMERIC VALIDATION METHODS ===

    @staticmethod
    def number_min(name: str, v: Union[int, float], v_min: Union[int, float]):
        """Validate number minimum value.
        
        Args:
            name: Field name for error messages
            v: Numeric value to validate
            v_min: Minimum allowed value
            
        Raises:
            ValueError: If number is less than minimum
        """
        if v < v_min:
            raise ValueError(f"{name} must be >= {v_min}, got: {v}")

    @staticmethod
    def number_max(name: str, v: Union[int, float], v_max: Union[int, float]):
        """Validate number maximum value.
        
        Args:
            name: Field name for error messages
            v: Numeric value to validate  
            v_max: Maximum allowed value
            
        Raises:
            ValueError: If number is greater than maximum
        """
        if v > v_max:
            raise ValueError(f"{name} must be <= {v_max}, got: {v}")

    # === PATH VALIDATION METHODS ===

    @staticmethod
    def path_must_exist(name: str, v: str):
        """Validate path exists on filesystem.
        
        Args:
            name: Field name for error messages
            v: Path string to validate
            
        Raises:
            ValueError: If path does not exist
        """
        path = Path(v)
        if not path.exists():
            raise ValueError(f"{name} path does not exist: {v}")

    @staticmethod
    def path_must_be_file(name: str, v: str):
        """Validate path exists and is a file.
        
        Args:
            name: Field name for error messages
            v: Path string to validate
            
        Raises:
            ValueError: If path doesn't exist or is not a file
        """
        path = Path(v)
        if not path.exists():
            raise ValueError(f"{name} path does not exist: {v}")
        if not path.is_file():
            raise ValueError(f"{name} path is not a file: {v}")

    @staticmethod
    def path_must_be_directory(name: str, v: str):
        """Validate path exists and is a directory.
        
        Args:
            name: Field name for error messages
            v: Path string to validate
            
        Raises:
            ValueError: If path doesn't exist or is not a directory
        """
        path = Path(v)
        if not path.exists():
            raise ValueError(f"{name} path does not exist: {v}")
        if not path.is_dir():
            raise ValueError(f"{name} path is not a directory: {v}")

    # === URL VALIDATION METHODS ===

    @staticmethod
    def url_basic_format(name: str, v: str):
        """Validate basic URL format (http/https protocol).
        
        Args:
            name: Field name for error messages
            v: URL string to validate
            
        Raises:
            ValueError: If URL format is invalid
        """
        if not v.startswith(('http://', 'https://')):
            raise ValueError(f"{name} must start with http:// or https://, got: {v}")
        
        # Basic format check - no spaces, has domain-like structure
        if ' ' in v:
            raise ValueError(f"{name} URL cannot contain spaces, got: {v}")
        
        # Must have something after protocol
        protocol_removed = v.replace('http://', '').replace('https://', '')
        if len(protocol_removed) < 3:
            raise ValueError(f"{name} URL must have domain after protocol, got: {v}")
