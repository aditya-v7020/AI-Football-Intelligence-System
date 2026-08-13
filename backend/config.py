"""
Centralized configuration management.
All secrets are loaded from .env — never hardcoded.
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

DEFAULT_CORS_ORIGINS = [
    "https://ai-football-intelligence-system.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://localhost:3000",
]


class Settings:
    """Application settings loaded from environment variables."""

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "").strip()
    FOOTBALL_API_KEY: str = os.getenv("FOOTBALL_API_KEY", "").strip()
    SPORTMONKS_API_KEY: str = os.getenv("SPORTMONKS_API_KEY", "").strip()
    THESPORTSDB_API_KEY: str = os.getenv("THESPORTSDB_API_KEY", "123").strip()
    FOOTBALL_DATA_API_KEY: str = os.getenv("FOOTBALL_DATA_API_KEY", "").strip()
    DATABASE_URL: str = os.getenv("DATABASE_URL", "").strip()

    # LLM configuration
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))

    # API Base URLs
    FOOTBALL_API_BASE_URL: str = "https://v3.football.api-sports.io"
    SPORTMONKS_BASE_URL: str = "https://api.sportmonks.com/v3/football"
    THESPORTSDB_BASE_URL: str = "https://www.thesportsdb.com/api/v1/json"
    FOOTBALL_DATA_BASE_URL: str = "https://api.football-data.org/v4"

    FOOTBALL_SEASON: int = int(os.getenv("FOOTBALL_SEASON", "2024"))

    # Caching configuration (TTL in seconds)
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "1800"))  # 30 minutes

    # Server configuration
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))

    # Production and local development CORS origins
    CORS_ORIGINS: list[str] = list(
        dict.fromkeys(
            DEFAULT_CORS_ORIGINS + [
                item.strip().rstrip("/")
                for item in os.getenv("CORS_ORIGINS", "").split(",")
                if item.strip()
            ]
        )
    )

    @classmethod
    def validate(cls) -> list[str]:
        """Return a list of missing required environment variables."""
        required = {
            "GROQ_API_KEY": cls.GROQ_API_KEY,
            "TAVILY_API_KEY": cls.TAVILY_API_KEY,
            "FOOTBALL_API_KEY": cls.FOOTBALL_API_KEY,
            "DATABASE_URL": cls.DATABASE_URL,
        }
        return [name for name, value in required.items() if not value]


settings = Settings()
