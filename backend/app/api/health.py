"""Health check endpoints."""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """Check if the service is healthy."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "debugging-agent-api"
    }


@router.get("/ready")
async def readiness_check():
    """Check if the service is ready to accept requests."""
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat(),
    }
