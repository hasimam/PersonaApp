from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DATABASE_URL: str
    SECRET_KEY: str
    CORS_ORIGINS: str = "http://localhost:3000"
    ENVIRONMENT: str = "development"

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "PersonaApp API"

    # Test Settings
    MIN_QUESTIONS: int = 40
    MAX_QUESTIONS: int = 60
    LIKERT_SCALE_MIN: int = 1
    LIKERT_SCALE_MAX: int = 5

    # Matching Settings
    TOP_N_MATCHES: int = 3

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
