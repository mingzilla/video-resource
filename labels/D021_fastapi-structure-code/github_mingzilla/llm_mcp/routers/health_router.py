"""
FastAPI router for health endpoints.

Handles HTTP concerns for health check functionality, delegating business logic to HealthService.
"""

from fastapi import APIRouter, HTTPException

from github_mingzilla.llm_mcp.services.health_service import health_service

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    try:
        health_status = await health_service.get_comprehensive_health_status()

        return health_status

    except Exception as e:
        # Return minimal health status on service failure
        return {"status": "unhealthy", "error": f"Health service error: {str(e)}", "components": {}}


@router.get("/health/basic")
async def basic_health_check():
    """Basic health check endpoint (faster response)."""
    try:
        health_status = await health_service.get_basic_health_status()

        return health_status

    except Exception as e:
        return {"status": "unhealthy", "error": f"Basic health check error: {str(e)}", "basic_check": True}


@router.get("/health/{component}")
async def component_health_check(component: str):
    """Get health status for a specific component."""
    try:
        component_status = await health_service.get_component_health(component)

        return component_status

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Component health check error: {str(e)}")


@router.get("/health/summary")
async def health_summary():
    """Get health service summary and available endpoints."""
    try:
        summary = health_service.get_health_summary()

        return summary

    except Exception as e:
        return {"service": "health_service", "status": "error", "error": str(e)}


# Module-level singleton instance
health_router = router
