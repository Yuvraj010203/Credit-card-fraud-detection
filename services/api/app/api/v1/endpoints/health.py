"""
Health check endpoints.
"""

from fastapi import APIRouter, Depends
from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "fraud-detection-api",
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    # Add checks for database, Redis, Kafka connectivity
    return {
        "status": "ready",
        "checks": {
            "database": "ok",
            "redis": "ok",
            "kafka": "ok"
        }
    }
