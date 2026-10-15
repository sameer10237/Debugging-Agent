"""FastAPI application entry point with WebSocket and error handling."""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from app.config import settings
from app.database import init_db, close_db
from app.api import auth, health, projects, executions, simulation
from app.exceptions import AppException, exception_handler, validation_exception_handler, generic_exception_handler, ErrorLoggingMiddleware
from app.websocket_manager import get_ws_manager
import logging

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    logger.info("Starting up application...")
    await init_db()
    yield
    # Shutdown
    logger.info("Shutting down application...")
    await close_db()


# Create FastAPI app
app = FastAPI(
    title="AI Debugging Agent",
    description="Multi-agent system for autonomous software debugging",
    version="0.1.0",
    lifespan=lifespan,
)

# Add error handlers
app.add_exception_handler(AppException, exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Add middleware
app.add_middleware(ErrorLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(projects.router, prefix="/api", tags=["projects"])
app.include_router(executions.router, prefix="/api", tags=["executions"])
app.include_router(simulation.router, prefix="/api", tags=["simulation"])


# WebSocket endpoint for real-time updates
@app.websocket("/ws/executions/{execution_id}")
async def websocket_endpoint(execution_id: str, websocket: WebSocket):
    """WebSocket endpoint for real-time execution updates."""
    ws_manager = get_ws_manager()
    
    try:
        await ws_manager.connect(execution_id, websocket)
        
        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            logger.debug(f"WebSocket message from {execution_id}: {data}")
            # Echo or process message if needed
            
    except WebSocketDisconnect:
        ws_manager.disconnect(execution_id, websocket)
        logger.info(f"WebSocket disconnected for execution {execution_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {execution_id}: {str(e)}")
        ws_manager.disconnect(execution_id, websocket)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "AI Debugging Agent",
        "version": "0.1.0",
        "status": "running",
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
