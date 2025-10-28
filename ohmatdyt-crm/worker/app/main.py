import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    APP_ENV: str = "development"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"
    CORS_ORIGINS: str = "http://localhost:3000"
    DATABASE_URL: str = "postgresql+psycopg://ohm_user:change_me@db:5432/ohm_db"
    REDIS_URL: str = "redis://redis:6379/0"
    MEDIA_ROOT: str = "/var/app/media"
    STATIC_ROOT: str = "/var/app/static"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

app = FastAPI(
    title="Ohmatdyt CRM API",
    description="CRM system for Ohmatdyt hospital",
    version="0.1.0",
    docs_url="/docs" if settings.APP_ENV == "development" else None,
    redoc_url="/redoc" if settings.APP_ENV == "development" else None,
)

# CORS configuration
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Ohmatdyt CRM API",
        "version": "0.1.0",
        "environment": settings.APP_ENV
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Add actual DB check
        "redis": "connected",  # TODO: Add actual Redis check
        "media_path": os.path.exists(settings.MEDIA_ROOT),
        "static_path": os.path.exists(settings.STATIC_ROOT),
    }

@app.get("/config")
async def config_check():
    """Configuration check endpoint (dev only)"""
    if settings.APP_ENV != "development":
        return {"error": "Not available in production"}
    
    return {
        "APP_ENV": settings.APP_ENV,
        "DATABASE_URL": settings.DATABASE_URL[:30] + "...",  # Truncate for security
        "REDIS_URL": settings.REDIS_URL,
        "MEDIA_ROOT": settings.MEDIA_ROOT,
        "STATIC_ROOT": settings.STATIC_ROOT,
        "CORS_ORIGINS": settings.CORS_ORIGINS,
        "ALLOWED_HOSTS": settings.ALLOWED_HOSTS,
    }

# Additional routes will be added here as the project develops