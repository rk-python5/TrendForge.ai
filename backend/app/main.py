"""
FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.redis_client import init_redis, close_redis
from app.routers import posts, generate, trends, publish, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup
    try:
        await init_redis()
        print("✅ Redis connected")
    except Exception as e:
        print(f"⚠️  Redis not available (optional): {e}")
    
    yield
    
    # Shutdown
    await close_redis()
    print("👋 Shutdown complete")


app = FastAPI(
    title="TrendForge AI",
    description="AI-powered LinkedIn content generation platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(posts.router, prefix="/api", tags=["Posts"])
app.include_router(generate.router, prefix="/api", tags=["Generation"])
app.include_router(trends.router, prefix="/api", tags=["Trends"])
app.include_router(publish.router, prefix="/api", tags=["Publishing"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "TrendForge AI"}
