from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import opik

from app.database import engine, Base
from app.api.routes import router
from app.config import settings

# Configure Opik before app creation
if settings.opik_api_key:
    opik.configure(api_key=settings.opik_api_key)
else:
    # Configure without API key for local development
    opik.configure(use_local=False)

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
