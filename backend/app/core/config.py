from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "WizMap Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql://wizmap:wizmap@postgres:5432/wizmap"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # MinIO
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "wizmap-uploads"
    MINIO_SECURE: bool = False

    # Processing
    MAX_FILE_SIZE_MB: int = 100
    ALLOWED_FILE_EXTENSIONS: list = [".txt", ".csv", ".json"]

    # ML Models
    EMBEDDING_DIM: int = 384

    # Embedding API (SiliconFlow / 硅基流动, OpenAI-compatible /embeddings endpoint)
    # Embeddings are fetched from this API; there is no local model.
    EMBEDDING_API_KEY: str = ""   # <-- 填入你的 SiliconFlow API Key
    EMBEDDING_BASE_URL: str = "https://api.siliconflow.cn/v1"
    EMBEDDING_MODEL: str = ""     # <-- 填入模型名，例如 BAAI/bge-large-zh-v1.5
    EMBEDDING_BATCH_SIZE: int = 32
    EMBEDDING_TIMEOUT: int = 60   # seconds per request

    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3001", "http://localhost:3000", "http://localhost:3002"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
