from pydantic_settings import BaseSettings
from pydantic import model_validator, Field
from typing import Optional
from pathlib import Path
import os


# Find .env file - check parent directory (project root) and current directory
def find_env_file():
    current_dir = Path(__file__).parent.parent  # backend/
    project_root = current_dir.parent  # commitment_broker/
    
    # Check project root first
    env_path = project_root / ".env"
    if env_path.exists():
        return str(env_path)
    
    # Fall back to backend directory
    env_path = current_dir / ".env"
    if env_path.exists():
        return str(env_path)
    
    # Return relative path for pydantic to search
    return ".env"


def get_default_database_url():
    """Construct default DATABASE_URL from environment or defaults."""
    postgres_user = os.getenv("POSTGRES_USER", "postgres")
    postgres_password = os.getenv("POSTGRES_PASSWORD", "postgres")
    postgres_db = os.getenv("POSTGRES_DB", "commitment_broker")
    return f"postgresql://{postgres_user}:{postgres_password}@localhost:5432/{postgres_db}"


class Settings(BaseSettings):
    database_url: str = Field(default_factory=get_default_database_url)
    gemini_api_key: str = ""
    opik_api_key: Optional[str] = None
    opik_workspace: Optional[str] = None
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    allowed_origins: Optional[str] = None  # Comma-separated list of allowed origins

    @model_validator(mode="before")
    @classmethod
    def set_database_url_if_missing(cls, values):
        """Set default DATABASE_URL if not provided."""
        if isinstance(values, dict):
            if not values.get("database_url"):
                values["database_url"] = os.getenv("DATABASE_URL") or get_default_database_url()
        return values

    class Config:
        env_file = find_env_file()
        case_sensitive = False
        env_file_encoding = "utf-8"


settings = Settings()
