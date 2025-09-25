"""Lexical search service using PostgreSQL with pg_trgm.

This module provides lexical search functionality that mirrors the API
interface of the vector similarity search, but uses PostgreSQL trigram
matching for text-based company searches.
"""

import time
from logging import Logger
from typing import Dict, List, Optional, Any

from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from pydantic import BaseModel, Field

from m_002__api.py_args import PyArgs002
from shared_utils.external.search_filtering.filter_attribute_util import FilterAttributeUtil


# Request/Response models (identical to vector search API)
class SearchRequest(BaseModel):
    """Lexical search request with filters."""
    query: str = Field(..., min_length=1, max_length=500, description="Search query text")
    limit: Optional[int] = Field(10, ge=1, le=500, description="Maximum results to return")
    min_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum similarity score")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filter conditions")


class SearchResponse(BaseModel):
    """Search response with results and metadata."""
    success: bool = Field(..., description="Whether search completed successfully")
    query: str = Field(..., description="Original search query")
    results: List[Dict[str, Any]] = Field(..., description="Search results")
    metadata: Dict[str, Any] = Field(..., description="Timing and performance metadata")
    error: Optional[str] = Field(None, description="Error message if search failed")


class LexicalSearchService:
    """PostgreSQL-based lexical search service using pg_trgm extension."""

    def __init__(self, config: PyArgs002):
        """Initialize lexical search service.

        Args:
            config: Configuration parameters including database connection
        """
        self.config = config
        # Construct the connection string for psycopg
        self.conninfo = (
            f"host={config.db_host} port={config.db_port} "
            f"dbname={config.db_name} user={config.db_user} "
            f"password={config.db_password}"
        )
        self.pool: Optional[AsyncConnectionPool] = None

    async def handle_api_search(self, request: SearchRequest) -> SearchResponse:
        """Handle search API request using PostgreSQL lexical search."""
        start_time = time.time()
        if not self.pool:
            return SearchResponse(success=False, query=request.query, results=[], metadata={"total_time_ms": 0}, error="Connection pool not initialized")

        try:
            async with self.pool.connection() as conn:
                conn.row_factory = dict_row
                async with conn.cursor() as cur:
                    base_query = """
                    SELECT
                        company_number,
                        company_name,
                        city,
                        active,
                        similarity(company_name, %(query)s) as score
                    FROM companies
                    WHERE similarity(company_name, %(query)s) >= %(min_score)s
                    """
                    min_score = request.min_score if request.min_score is not None else 0.1
                    query_params = {"query": request.query, "min_score": min_score}

                    filter_conditions = []
                    if request.filters:
                        for key, value in request.filters.items():
                            if key == "active":
                                filter_conditions.append(f"active = %(active_filter)s")
                                query_params["active_filter"] = bool(value)
                            elif key == "city":
                                # Use exact match with normalized city data
                                normalized_city = FilterAttributeUtil.normalize_text(value)
                                if normalized_city:
                                    filter_conditions.append(f"city = %(filter_city)s")
                                    query_params["filter_city"] = normalized_city
                            elif key == "company_number":
                                # Use exact match for company_number
                                filter_conditions.append(f"company_number = %(filter_company_number)s")
                                query_params["filter_company_number"] = str(value)

                    if filter_conditions:
                        base_query += " AND " + " AND ".join(filter_conditions)

                    base_query += " ORDER BY score DESC LIMIT %(limit)s"
                    query_params["limit"] = request.limit or 10

                    query_start = time.time()
                    await cur.execute(base_query, query_params)
                    rows = await cur.fetchall()
                    query_time = time.time() - query_start

                    results = []
                    for r in rows:
                        row_dict = dict(r)
                        score = row_dict.pop("score")
                        results.append({"score": score, "payload": row_dict})

            total_time = time.time() - start_time
            return SearchResponse(
                success=True,
                query=request.query,
                results=results,
                metadata={
                    "total_time_ms": round(total_time * 1000, 2),
                    "query_time_ms": round(query_time * 1000, 2),
                    "result_count": len(results),
                    "requested_limit": request.limit or 10,
                    "min_score": min_score,
                    "search_type": "lexical_pg_trgm"
                }
            )

        except Exception as e:
            total_time = time.time() - start_time
            return SearchResponse(
                success=False,
                query=request.query,
                results=[],
                metadata={
                    "total_time_ms": round(total_time * 1000, 2),
                    "error_time_ms": round(total_time * 1000, 2),
                    "result_count": 0,
                    "search_type": "lexical_pg_trgm"
                },
                error=str(e)
            )