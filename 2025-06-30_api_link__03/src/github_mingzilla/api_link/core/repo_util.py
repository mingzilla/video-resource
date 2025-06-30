# Standard Library
from typing import List, Optional, Type, TypeVar

# Third Party
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class RepoUtil:
    """Async base database service implementing common CRUD operations following style guide."""

    @staticmethod
    async def create(session: AsyncSession, entity: T) -> T:
        """Create a new entity in the database."""
        session.add(entity)
        await session.flush()
        await session.refresh(entity)
        return entity

    @staticmethod
    async def create_entity(session: AsyncSession, entity_class: Type[T], model: BaseModel) -> T:
        """Create a new entity from a Pydantic model."""
        return await RepoUtil.create(session, entity_class(**model.model_dump()))

    @staticmethod
    async def update(session: AsyncSession, entity: T) -> T:
        """Update an existing entity."""
        await session.merge(entity)
        await session.flush()
        await session.refresh(entity)
        return entity

    @staticmethod
    async def merge_entity(session: AsyncSession, entity_class: Type[T], entity_id: int, model: BaseModel) -> Optional[T]:
        """Update an entity with partial data from a Pydantic model.

        Args:
            session: Async database session
            entity_class: SQLAlchemy entity class
            entity_id: ID of the entity to update
            model: Pydantic BaseModel instance containing partial update data

        Returns:
            Updated entity or None if entity not found
        """
        entity = await RepoUtil.get_by_id(session, entity_class, entity_id)
        if entity:
            update_dict = model.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(entity, key, value)
            await session.flush()
            await session.refresh(entity)
            return entity
        return None

    @staticmethod
    async def get_by_id(session: AsyncSession, entity_class: Type[T], entity_id: int) -> Optional[T]:
        """Retrieve entity by ID."""
        stmt = select(entity_class).where(entity_class.id == entity_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(session: AsyncSession, entity_class: Type[T]) -> List[T]:
        """Retrieve all entities of a given type."""
        stmt = select(entity_class)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_limited(session: AsyncSession, entity_class: Type[T], limit: int, offset: int) -> List[T]:
        """Retrieve all entities with pagination."""
        stmt = select(entity_class).offset(offset).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def delete(session: AsyncSession, entity_class: Type[T], entity_id: int) -> Optional[T]:
        """Delete an entity by ID and return the deleted entity."""
        entity = await RepoUtil.get_by_id(session, entity_class, entity_id)
        if entity:
            await session.delete(entity)
            await session.flush()
            return entity
        return None
