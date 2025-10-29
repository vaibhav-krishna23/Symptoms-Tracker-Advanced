"""Initialization or Placeholder File."""
# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: Optional[str] = None
    FERNET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_API_BASE: str = "https://generativelanguage.googleapis.com/v1beta"
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    ENV: str = "development"
    API_BASE: str = "http://localhost:8000"
    MCP_SERVER_HOST: str = "localhost"
    MCP_SERVER_PORT: int = 8001
    LANGGRAPH_CHECKPOINT_DB: str = "checkpoints.db"

    class Config:
        env_file = ".env"

settings = Settings()
