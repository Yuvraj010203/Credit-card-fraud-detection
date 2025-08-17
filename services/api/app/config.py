from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Fraud Detection API"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str = "postgresql://fraud:password@localhost:5432/frauddb"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_EXPIRE_SECONDS: int = 3600
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_CONSUMER_GROUP: str = "api-service"
    
    # Neo4j
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    
    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minio"
    MINIO_SECRET_KEY: str = "password"
    MINIO_SECURE: bool = False
    MODEL_BUCKET: str = "models"
    
    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    
    # ML Models
    MODEL_VERSION: str = "v1.0.0"
    SCORE_THRESHOLD: float = 0.7
    SHAP_EXPLAINER_PATH: str = "explainers/shap_explainer.pkl"
    
    # Feature Engineering
    VELOCITY_WINDOW_MINUTES: List[int] = [1, 5, 30, 120]
    EMBEDDING_DIMENSION: int = 128
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Performance
    MAX_CONCURRENT_REQUESTS: int = 1000
    TIMEOUT_SECONDS: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()