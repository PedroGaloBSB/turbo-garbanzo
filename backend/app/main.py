# Main FastAPI Application
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
import asyncio

from app.core.config import settings
from app.api.routes import router
from app.workers.task_queue import task_queue
from app.core.security import rate_limit_exceeded_handler

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Open-source PDF manipulation tool with Google Drive integration",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, rate_limit_exceeded_handler)

# Include API routes
app.include_router(router, prefix=settings.API_V1_PREFIX)

@app.on_event("startup")
async def startup_event():
    """Start background tasks on startup"""
    # Start task queue workers
    for _ in range(settings.MAX_CONCURRENT_TASKS):
        asyncio.create_task(task_queue.start_worker())
    
    print(f"🚀 {settings.APP_NAME} started!")
    print(f"📁 Upload directory: {settings.UPLOAD_DIR}")
    print(f"📁 Output directory: {settings.OUTPUT_DIR}")
    print(f"🔒 Max concurrent tasks: {settings.MAX_CONCURRENT_TASKS}")
    print(f"⏱️  Rate limit: {settings.RATE_LIMIT_PER_MINUTE} requests/minute")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 Shutting down...")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": "2.0.0",
        "description": "Open-source PDF manipulation tool",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ocr_available": task_queue.ocr_service.is_available()
    }

# Apply rate limiting to all routes
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    try:
        response = await limiter(request)(call_next)
        return response
    except Exception:
        return await call_next(request)
