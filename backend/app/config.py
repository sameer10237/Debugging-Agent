"""Backend application configuration."""

from pydantic_settings import BaseSettings
from typing import List
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Database
    database_url: str = "postgresql+asyncpg://debug_user:debug_password@localhost:5432/debugging_agent"
    database_echo: bool = False
    database_pool_size: int = 20
    database_pool_recycle: int = 3600

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    debug: bool = False
    log_level: str = "INFO"

    # CORS
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    cors_credentials: bool = True
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]

    # LLM
    openai_api_key: str = ""
    model_name: str = "gpt-4"
    model_temperature: float = 0.1
    max_tokens: int = 8192

    # Agent
    max_agent_iterations: int = 5
    agent_timeout: int = 300
    enable_code_execution: bool = True

    # Security
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # File upload
    upload_max_size: int = 52428800  # 50MB
    allowed_extensions: List[str] = [
        "py", "ts", "tsx", "js", "jsx", "java", "cs", "cpp", "c", "go", "rs", "rb"
    ]

    # Logging
    log_file_path: str = "./logs/app.log"
    log_max_size: int = 10485760  # 10MB
    log_backup_count: int = 5

    # Frontend
    frontend_url: str = "http://localhost:5173"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # Features
    enable_auto_fixes: bool = True
    enable_security_analysis: bool = True
    enable_performance_analysis: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
