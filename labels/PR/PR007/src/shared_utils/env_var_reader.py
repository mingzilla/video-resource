import os
import re
from pathlib import Path
from typing import Optional, Union, List

from dotenv import load_dotenv


class EnvVarReader:

    @staticmethod
    def load_dotenv():
        load_dotenv(override=False)

    @staticmethod
    def get_runtime_env() -> str:
        name = "RUNTIME_ENV"
        v = os.getenv(name)
        if v is None:
            raise ValueError('scripts_sh/*.sh is missing: export RUNTIME_ENV="${RUNTIME_ENV:-DEV}", which can be overridden with PROD in docker-compose.yml files')
        if v == "DEV": return v
        if v == "PROD": return v
        raise ValueError('RUNTIME_ENV has to be "DEV" or "PROD"')

    @staticmethod
    def get_str_by_env(name: str, prod_fallback: str, dev_fallback: str) -> str:
        env_v = EnvVarReader.get_runtime_env()
        fallback = dev_fallback if env_v == "DEV" else prod_fallback
        return EnvVarReader.get_str(name, fallback)

    @staticmethod
    def get_int_by_env(name: str, prod_fallback: int, dev_fallback: int) -> int:
        env_v = EnvVarReader.get_runtime_env()
        fallback = dev_fallback if env_v == "DEV" else prod_fallback
        return EnvVarReader.get_int(name, f"{fallback}")

    @staticmethod
    def get_str(name: str, fallback: str) -> str:
        return os.getenv(name, fallback)

    @staticmethod
    def get_int(name: str, fallback: str) -> Optional[int]:
        v = os.getenv(name, fallback)

        try:
            if v is None:
                return None
            return int(v)
        except ValueError:
            raise ValueError(f"{name} must be integer, got: {v}")

    @staticmethod
    def get_bool(name: str, fallback: str) -> bool:
        v = os.getenv(name, fallback)
        return v.lower() in ('true', '1', 'yes', 'on')

    @staticmethod
    def number_range(name: str, v: Union[int, float], v_min: Union[int, float], v_max: Union[int, float]):
        if v < v_min or v > v_max:
            raise ValueError(f"{name} must be between {v_min} and {v_max} (inclusive), got: {v}")
