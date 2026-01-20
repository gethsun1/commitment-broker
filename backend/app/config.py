from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str
    gemini_api_key: str
    opik_api_key: Optional[str] = None
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
