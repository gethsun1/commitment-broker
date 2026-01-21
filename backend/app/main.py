from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import opik
import os
import sys
import traceback

from app.database import engine, Base
from app.api.routes import router
from app.config import settings

# Configure Opik before app creation
# Opik will use environment variables if available, or config file
# See: https://www.comet.com/docs/opik/python-sdk-reference/configure
try:
    if settings.opik_api_key:
        config_params = {"api_key": settings.opik_api_key}
        if settings.opik_workspace:
            config_params["workspace"] = settings.opik_workspace
        # Set workspace from env if available but not in settings
        if not config_params.get("workspace"):
            config_params["workspace"] = os.getenv("OPIK_WORKSPACE")
        # Only include workspace if we have it to avoid errors
        if config_params.get("workspace"):
            opik.configure(api_key=config_params["api_key"], workspace=config_params["workspace"])
        else:
            opik.configure(api_key=config_params["api_key"])
    else:
        # Try to configure from environment variables or config file
        # This allows Opik to work if OPIK_API_KEY and OPIK_WORKSPACE are set in env
        # Only configure if we have both API key and workspace to avoid interactive prompts
        opik_api_key = os.getenv("OPIK_API_KEY")
        opik_workspace = os.getenv("OPIK_WORKSPACE")
        if opik_api_key and opik_workspace:
            opik.configure(api_key=opik_api_key, workspace=opik_workspace)
        elif opik_api_key:
            # If only API key is set, try to configure with just API key
            # Some Opik versions may work without workspace
            try:
                opik.configure(api_key=opik_api_key)
            except Exception:
                print("⚠️  Opik API key found but workspace not set. Skipping Opik configuration.")
                print("   To enable Opik, add OPIK_WORKSPACE to your environment variables.")
except (EOFError, KeyboardInterrupt, Exception) as e:
    # Gracefully handle Opik configuration errors
    # This allows the app to start even if Opik fails to configure
    print(f"⚠️  Opik configuration skipped: {e}")
    print("   The app will continue without Opik observability.")

# Create database tables (with error handling for deployment)
# This allows the app to start even if database isn't immediately available
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified successfully")
except Exception as db_error:
    print(f"⚠️  Database initialization warning: {db_error}")
    print("   Tables will be created on first database connection.")
    print("   Make sure DATABASE_URL is set correctly in your environment variables.")

app = FastAPI(
    title="Commitment Broker API",
    description="AI agent system for financial goal commitment tracking",
    version="1.0.0"
)

# Build allowed origins list
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",  # Alternative port
    "https://commitmentbroker.vercel.app",  # Vercel production
]

# Add environment variable origins if provided
if settings.allowed_origins:
    allowed_origins.extend([origin.strip() for origin in settings.allowed_origins.split(",")])

# Vercel preview deployments use pattern: https://*-*.vercel.app
# Use regex to allow all Vercel preview deployments
vercel_preview_regex = r"https://.*\.vercel\.app"

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=vercel_preview_regex,  # Allow all Vercel preview deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers to ensure CORS headers are sent even on errors
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with CORS headers."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all exceptions with CORS headers."""
    print(f"⚠️  Unhandled exception: {exc}")
    print(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Commitment Broker API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
