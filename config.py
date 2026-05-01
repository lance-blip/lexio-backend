import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

class Config:
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "anthropic/claude-sonnet-4-20250514")
    FALLBACK_MODEL: str = os.getenv("FALLBACK_MODEL", "google/gemini-2.0-flash-001")
    API_SECRET_KEY: str = os.getenv("API_SECRET_KEY")
    RATE_LIMIT_FREE: int = int(os.getenv("RATE_LIMIT_FREE", "20"))
    RATE_LIMIT_PREMIUM: int = int(os.getenv("RATE_LIMIT_PREMIUM", "1000"))
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    @classmethod
    def validate(cls):
        if not cls.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is required")
        if not cls.API_SECRET_KEY:
            raise ValueError("API_SECRET_KEY is required")

config = Config()
