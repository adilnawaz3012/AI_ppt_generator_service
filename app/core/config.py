import logging
from pydantic_settings import BaseSettings
from typing import List, Set

class Settings(BaseSettings):
    APP_NAME: str = "GenAI Presentation Generator API"
    API_V1_STR: str = "/api/v1"

    # Redis URL for Caching and Message Broker for ARQ
    REDIS_URL: str = "redis://redis:6379/0"

    # Security & Rate Limiting
    ALLOWED_API_KEYS_STR: str = "secret-key-1"
    DEFAULT_RATE_LIMIT: str = "100/minute"
    CREATE_RATE_LIMIT: str = "20/minute"

    @property
    def ALLOWED_API_KEYS(self) -> Set[str]:
        return set(self.ALLOWED_API_KEYS_STR.split(','))
    
    # LLM Service API Keys
    OPENAI_API_KEY: str = "12345"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Basic Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)