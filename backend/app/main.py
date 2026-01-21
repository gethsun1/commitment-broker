from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import opik
import os
import sys

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
        # Disable interactive prompts for non-interactive environments
        config_params["disable_cloud"] = False
        # Set workspace from env if available but not in settings
        if not config_params.get("workspace"):
            config_params["workspace"] = os.getenv("OPIK_WORKSPACE")
        opik.configure(**config_params)
    else:
        # Try to configure from environment variables or config file
        # This allows Opik to work if OPIK_API_KEY and OPIK_WORKSPACE are set in env
        # Only configure if we have both API key and workspace to avoid interactive prompts
        opik_api_key = os.getenv("OPIK_API_KEY")
        opik_workspace = os.getenv("OPIK_WORKSPACE")
        if opik_api_key and opik_workspace:
            opik.configure(api_key=opik_api_key, workspace=opik_workspace)
        elif opik_api_key:
            # If only API key is set, skip Opik configuration to avoid interactive prompts
            # User should set OPIK_WORKSPACE in .env file to enable Opik
            print("⚠️  Opik API key found but workspace not set. Skipping Opik configuration.")
            print("   To enable Opik, add OPIK_WORKSPACE to your .env file.")
except (EOFError, KeyboardInterrupt, Exception) as e:
    # Gracefully handle Opik configuration errors
    # This allows the app to start even if Opik fails to configure
    print(f"⚠️  Opik configuration skipped: {e}")
    print("   The app will continue without Opik observability.")

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Commitment Broker API",
    description="AI agent system for financial goal commitment tracking",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Commitment Broker API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
