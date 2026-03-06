"""
Centralized configuration – reads from .env with sensible defaults.
Import `from app.config import settings` anywhere in the backend.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend root
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)


class _Settings:
    """Simple settings container — reads env vars once at import time."""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./lifeforge.db")

    # CORS
    CORS_ORIGINS: list[str] = [
        o.strip()
        for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    ]

    # Ollama LLM
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "mistral")
    USE_LLM: bool = os.getenv("USE_LLM", "true").lower() in ("true", "1", "yes")

    # Whisper
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "small")

    # App metadata
    APP_VERSION: str = os.getenv("APP_VERSION", "0.3.0")

    # Backup
    MAX_AUTO_BACKUPS: int = int(os.getenv("MAX_AUTO_BACKUPS", "30"))


settings = _Settings()
