from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import webhooks, worker
from app.routers.auth_simple import router as auth_router
from app.routers.api_simple import router as api_router
from app.services.workflow_engine import workflow_engine
from app.config import settings
from app.middleware.error_handler import error_handling_middleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager to initialize and cleanup resources
    """
    logger.info("🚀 Starting HubSpot Operations Orchestrator AI Service...")
    
    # Initialize workflow engine and connect to Redis
    try:
        await workflow_engine.initialize()
        logger.info("✅ Workflow engine initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize workflow engine: {e}")
        raise
    
    yield  # Application runs here
    
    # Cleanup
    logger.info("🛑 Shutting down HubSpot Operations Orchestrator AI Service...")

app = FastAPI(
    title="HubSpot Operations Orchestrator - AI Service",
    version="1.0.0",
    lifespan=lifespan
)

# Add error handling middleware
app.middleware("http")(error_handling_middleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhooks.router, prefix="/webhooks")
app.include_router(worker.router, prefix="/worker")
app.include_router(auth_router)
app.include_router(api_router)

# Include logging router
try:
    from app.services.logging_service import router as logging_router
    app.include_router(logging_router)
except ImportError:
    logger.warning("Logging service not available, skipping routes")
except Exception as e:
    logger.warning(f"Logging routes not available: {e}")

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify that the service is running.
    """
    health_status = {
        "status": "ok",
        "service": "HubSpot Operations Orchestrator AI Service",
        "version": "1.0.0",
    }
    
    # Check Redis connection
    try:
        redis_ok = await workflow_engine.redis_service.ping()
        health_status["redis"] = "connected" if redis_ok else "disconnected"
    except Exception as e:
        health_status["redis"] = f"error: {str(e)}"
    
    return health_status

@app.get("/", tags=["Root"])
async def read_root():
    """
    Root endpoint of the AI service.
    """
    return {"message": "Welcome to the HubSpot Operations Orchestrator AI Service"}

