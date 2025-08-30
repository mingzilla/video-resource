from typing import AsyncGenerator

from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from github_mingzilla.api_link.core.config import DatabaseConfig


class Database:
    """Async database connection and session management with static methods."""

    db_engine = create_async_engine(DatabaseConfig.get_async_url(), pool_size=20, max_overflow=30, pool_pre_ping=True, echo=False)  # Set to True for SQL debugging
    db_local_session = async_sessionmaker(autocommit=False, autoflush=False, bind=db_engine, class_=AsyncSession)
    entity_base = declarative_base(metadata=MetaData(naming_convention={"ix": "ix_%(column_0_label)s", "uq": "uq_%(table_name)s_%(column_0_name)s", "ck": "ck_%(table_name)s_%(constraint_name)s", "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s", "pk": "pk_%(table_name)s"}))

    @staticmethod
    async def get_session() -> AsyncGenerator[AsyncSession, None]:
        """Create async database session with proper cleanup."""
        async with Database.db_local_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    @staticmethod
    async def test_connection() -> bool:
        """Test async database connectivity."""
        try:
            async with Database.db_engine.begin() as connection:
                result = await connection.execute(text("SELECT 1"))
                row = result.fetchone()
                return row[0] == 1
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False
