"""Data access layer for PostgreSQL target database operations.

Following 3-tier architecture pattern:
- Repository layer handles database access only
- No business logic - pure data operations
- Returns data structures for service layer processing

Implements PostgreSQL with pg_trgm for lexical search capabilities.
"""

import asyncio
import psycopg
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from contextlib import asynccontextmanager

from psycopg_pool import AsyncConnectionPool

from shared_utils.external.services.singleton_manager import ClosableService, singleton_manager

logger = logging.getLogger(__name__)


@dataclass
class CompanyRecord:
    """Data structure for company record for PostgreSQL insertion."""
    company_number: str
    company_name: Optional[str]
    active: Optional[bool]
    standardised_city: Optional[str]


class _TargetPgRepository(ClosableService):
    """Data access for PostgreSQL target database operations."""

    def __init__(self):
        self._conninfo: Optional[str] = None
        self.pool: Optional[AsyncConnectionPool] = None

    def initialize(self, connection_params: Dict[str, Any]) -> None:
        """Initialize the repository with PostgreSQL connection parameters.

        Args:
            connection_params: PostgreSQL connection parameters dict
        """
        self._conninfo = (
            f"host={connection_params['host']} port={connection_params['port']} "
            f"dbname={connection_params['dbname']} user={connection_params['user']} "
            f"password={connection_params['password']}"
        )
        logger.info(f"Initialized target PostgreSQL repository for async connection")

    async def create_pool(self):
        """Creates and initializes the asynchronous connection pool."""
        if not self.pool and self._conninfo:
            self.pool = AsyncConnectionPool(self._conninfo, min_size=2, max_size=10)
            await self.pool.open()

    async def close_pool(self):
        """Closes the asynchronous connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    @asynccontextmanager
    async def get_connection(self):
        """Get async PostgreSQL connection from pool with automatic cleanup."""
        if not self.pool:
            await self.create_pool()

        if not self.pool:
            raise ValueError("Repository not initialized or pool creation failed - call initialize() and create_pool() first")

        conn = None
        try:
            async with self.pool.connection() as conn:
                yield conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    async def create_companies_table(self) -> None:
        """Create companies table optimized for lexical search (async)."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS companies (
            id SERIAL PRIMARY KEY,
            company_number TEXT NOT NULL UNIQUE,
            company_name TEXT,
            active BOOLEAN,
            city TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        create_indexes_sql = [
            """
            CREATE INDEX IF NOT EXISTS idx_company_name_gin 
            ON companies USING gin (company_name gin_trgm_ops)
            """,
            "CREATE INDEX IF NOT EXISTS idx_company_city ON companies (city)",
            "CREATE INDEX IF NOT EXISTS idx_company_active ON companies (active)",
            "CREATE INDEX IF NOT EXISTS idx_company_number ON companies (company_number)"
        ]

        async with self.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
                await cursor.execute(create_table_sql)
                logger.info("Companies table created successfully")

                for index_sql in create_indexes_sql:
                    await cursor.execute(index_sql)
                
                logger.info("Trigram and supporting indexes created successfully")
                await conn.commit()
    
    async def validate_table_structure(self) -> List[str]:
        """Validate that the companies table has correct structure (async)."""
        errors = []
        try:
            async with self.get_connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'companies')")
                    table_exists = (await cursor.fetchone())[0]
                    if not table_exists:
                        errors.append("Companies table does not exist")
                        return errors

                    await cursor.execute("SELECT EXISTS (SELECT FROM pg_extension WHERE extname = 'pg_trgm')")
                    extension_exists = (await cursor.fetchone())[0]
                    if not extension_exists:
                        errors.append("pg_trgm extension is not installed")

                    await cursor.execute("SELECT EXISTS (SELECT FROM pg_indexes WHERE indexname = 'idx_company_name_gin')")
                    index_exists = (await cursor.fetchone())[0]
                    if not index_exists:
                        errors.append("Trigram index idx_company_name_gin does not exist")
        except Exception as e:
            errors.append(f"Error validating table structure: {e}")
        return errors

    async def clear_companies_table(self) -> int:
        """Clear all data from companies table (async)."""
        async with self.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM companies")
                deleted_count = cursor.rowcount
                await conn.commit()
                logger.info(f"Cleared {deleted_count} rows from companies table")
                return deleted_count

    async def insert_company_batch(self, companies: List[CompanyRecord], normalized_cities: List[str]) -> int:
        """Insert a batch of companies into PostgreSQL (async)."""
        if len(companies) != len(normalized_cities):
            raise ValueError("Companies and normalized_cities lists must have same length")

        insert_sql = """
        INSERT INTO companies (company_number, company_name, active, city)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (company_number) DO UPDATE SET
            company_name = EXCLUDED.company_name,
            active = EXCLUDED.active,
            city = EXCLUDED.city
        """
        insert_data = [(c.company_number, c.company_name, c.active, city) for c, city in zip(companies, normalized_cities)]

        async with self.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.executemany(insert_sql, insert_data)
                inserted_count = cursor.rowcount
                await conn.commit()
                return inserted_count

    async def get_companies_count(self) -> int:
        """Get total count of companies in the table (async)."""
        async with self.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT COUNT(*) FROM companies")
                count = (await cursor.fetchone())[0]
                return count

    async def disconnect(self) -> None:
        """Alias for close_pool to satisfy ClosableService interface."""
        await self.close_pool()

