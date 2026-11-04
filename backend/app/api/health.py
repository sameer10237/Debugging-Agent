"""Health check endpoints."""

from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()


@router.get("/health")
async def health_check():
    """Check if the service is healthy."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "debugging-agent-api"
    }


@router.get("/ready")
async def readiness_check():
    """Check if the service is ready to accept requests."""
    return {
        "ready": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
