from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import logging
from contextlib import asynccontextmanager
import asyncio
import json
from typing import List

from .config import settings
from .database import engine, Base
from .api.v1.api import api_router
from .core.logging import setup_logging
from .core.exceptions import setup_exception_handlers
from .services.model_registry import ModelRegistry
from .utils.kafka_client import KafkaClient

# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected clients
                self.disconnect(connection)

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting fraud detection API service...")
    
    # Initialize database
    Base.metadata.create_all(bind=engine)
    
    # Initialize model registry
    model_registry = ModelRegistry()
    await model_registry.initialize()
    app.state.model_registry = model_registry
    
    # Initialize Kafka client for real-time updates
    kafka_client = KafkaClient()
    app.state.kafka_client = kafka_client
    
    # Start background tasks
    asyncio.create_task(consume_alerts())
    
    logger.info("Fraud detection API service started successfully")
    yield
    
    # Shutdown
    logger.info("Shutting down fraud detection API service...")
    await kafka_client.close()

app = FastAPI(
    title="Fraud Detection API",
    description="Real-time fraud detection system with ML-powered scoring",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Exception handlers
setup_exception_handlers(app)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# WebSocket endpoint for real-time alerts
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for heartbeat
            await manager.send_personal_message(f"Message received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Background task to consume alerts and broadcast to WebSocket clients
async def consume_alerts():
    """Consume high-priority alerts from Kafka and broadcast to WebSocket clients"""
    try:
        kafka_client = app.state.kafka_client
        async for message in kafka_client.consume("alerts"):
            alert_data = json.loads(message.value)
            if alert_data.get("severity") == "HIGH":
                await manager.broadcast(json.dumps(alert_data))
    except Exception as e:
        logging.getLogger(__name__).error(f"Error consuming alerts: {e}")

# Health check endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "fraud-detection-api"}

@app.get("/ready")
async def readiness_check():
    """Check if all dependencies are ready"""
    checks = {
        "database": False,
        "redis": False,
        "kafka": False,
        "model_registry": False
    }
    
    try:
        # Check database
        from .database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        checks["database"] = True
    except:
        pass
    
    # Add other dependency checks...
    
    all_ready = all(checks.values())
    status_code = 200 if all_ready else 503
    
    return {"ready": all_ready, "checks": checks}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
