from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from github_mingzilla.api_link.core.database import Database
from github_mingzilla.api_link.core.repo_util import RepoUtil
from github_mingzilla.api_link.models.entities.api_config import ApiConfig, ApiConfigCreate, ApiConfigEntity, ApiConfigUpdate

router = APIRouter(
    prefix="/api_configs",
    tags=["ApiConfigs"],
    responses={404: {"description": "Not found"}},
)


async def get_db_session() -> AsyncSession:
    async for session in Database.get_session():
        yield session


@router.post("/", response_model=ApiConfig, status_code=status.HTTP_201_CREATED)
async def create_api_config(api_config_create: ApiConfigCreate, db: AsyncSession = Depends(get_db_session)) -> ApiConfigEntity:
    created_api_config = await RepoUtil.create_entity(db, ApiConfigEntity, api_config_create)
    return created_api_config


@router.get("/{api_config_id}", response_model=ApiConfig)
async def get_api_config(api_config_id: int, db: AsyncSession = Depends(get_db_session)) -> Optional[ApiConfigEntity]:
    """Get API configuration by ID."""
    db_api_config = await RepoUtil.get_by_id(db, ApiConfigEntity, api_config_id)
    if db_api_config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ApiConfig not found")
    return db_api_config


@router.get("/", response_model=List[ApiConfig])
async def get_all_api_configs(db: AsyncSession = Depends(get_db_session), limit: int = 100, offset: int = 0) -> List[ApiConfigEntity]:
    """Get all API configurations with pagination."""
    api_configs = await RepoUtil.get_limited(db, ApiConfigEntity, limit, offset)
    return api_configs


@router.put("/{api_config_id}", response_model=ApiConfig)
async def update_api_config(api_config_id: int, api_config_update: ApiConfigUpdate, db: AsyncSession = Depends(get_db_session)) -> Optional[ApiConfigEntity]:
    """Update an existing API configuration."""
    updated_api_config = await RepoUtil.merge_entity(db, ApiConfigEntity, api_config_id, api_config_update)
    if updated_api_config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ApiConfig with id {api_config_id} not found for update")
    return updated_api_config


@router.delete("/{api_config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_config(api_config_id: int, db: AsyncSession = Depends(get_db_session)) -> None:
    """Delete an API configuration by ID."""
    deleted_api_config = await RepoUtil.delete(db, ApiConfigEntity, api_config_id)
    if deleted_api_config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ApiConfig with id {api_config_id} not found for deletion")
    return None
