"""
API v1 router configuration.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health, scoring, decisions, models, alerts, drift

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(scoring.router, prefix="/scoring", tags=["scoring"])
api_router.include_router(decisions.router, prefix="/decisions", tags=["decisions"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(drift.router, prefix="/drift", tags=["drift"])
