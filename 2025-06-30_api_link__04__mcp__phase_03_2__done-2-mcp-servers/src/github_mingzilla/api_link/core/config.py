import os

from dotenv import load_dotenv

load_dotenv()


class DatabaseConfig:
    """Database configuration management following style guide requirements."""

    @staticmethod
    def get_host() -> str:
        return os.getenv("DB_HOST", "localhost")

    @staticmethod
    def get_port() -> int:
        return int(os.getenv("DB_PORT", "11001"))

    @staticmethod
    def get_database() -> str:
        return os.getenv("DB_DATABASE", "api_link")

    @staticmethod
    def get_username() -> str:
        return os.getenv("DB_USERNAME", "root")

    @staticmethod
    def get_password() -> str:
        return os.getenv("DB_PASSWORD", "test1234")

    @staticmethod
    def get_url() -> str:
        """Construct database URL for SQLAlchemy connection (sync)."""
        host = DatabaseConfig.get_host()
        port = DatabaseConfig.get_port()
        database = DatabaseConfig.get_database()
        username = DatabaseConfig.get_username()
        password = DatabaseConfig.get_password()

        return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}?charset=utf8mb4"

    @staticmethod
    def get_async_url() -> str:
        """Construct async database URL for SQLAlchemy async connection."""
        host = DatabaseConfig.get_host()
        port = DatabaseConfig.get_port()
        database = DatabaseConfig.get_database()
        username = DatabaseConfig.get_username()
        password = DatabaseConfig.get_password()

        return f"mysql+aiomysql://{username}:{password}@{host}:{port}/{database}?charset=utf8mb4"
