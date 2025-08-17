#!/usr/bin/env python3

"""
Script to create all necessary Python files with basic content.
"""

import os
from pathlib import Path

BASE_DIR = Path("/Users/parthbatwara/Desktop/Code/credit-card-fraud-detection")

# Define all the Python files that need to be created
python_files = {
    # API Service - remaining files
    "services/api/app/dependencies.py": "# Dependencies for FastAPI",
    "services/api/app/api/v1/endpoints/scoring.py": "# Scoring endpoints",
    "services/api/app/api/v1/endpoints/decisions.py": "# Decision endpoints", 
    "services/api/app/api/v1/endpoints/models.py": "# Model management endpoints",
    "services/api/app/api/v1/endpoints/alerts.py": "# Alert endpoints",
    "services/api/app/api/v1/endpoints/drift.py": "# Drift monitoring endpoints",
    "services/api/app/core/__init__.py": "# Core package",
    "services/api/app/core/security.py": "# Security utilities",
    "services/api/app/core/logging.py": "# Logging configuration", 
    "services/api/app/core/exceptions.py": "# Custom exceptions",
    "services/api/app/services/__init__.py": "# Services package",
    "services/api/app/services/scoring.py": "# Scoring service",
    "services/api/app/services/feature_service.py": "# Feature engineering service",
    "services/api/app/services/graph_service.py": "# Graph service",
    "services/api/app/services/explanation.py": "# Explanation service",
    "services/api/app/services/drift_detector.py": "# Drift detection service",
    "services/api/app/services/model_registry.py": "# Model registry service",
    "services/api/app/utils/__init__.py": "# Utils package",
    "services/api/app/utils/feature_utils.py": "# Feature utilities",
    "services/api/app/utils/geo_utils.py": "# Geo utilities",
    "services/api/app/utils/time_utils.py": "# Time utilities",
    "services/api/tests/__init__.py": "# API Tests",
    "services/api/tests/conftest.py": "# Test configuration",
    "services/api/tests/test_scoring.py": "# Scoring tests",
    "services/api/tests/test_features.py": "# Feature tests",
    "services/api/tests/test_api.py": "# API tests",

    # Inference Service
    "services/inference/__init__.py": "# Inference Service",
    "services/inference/app/__init__.py": "# Inference App",
    "services/inference/app/main.py": "# Inference main application",
    "services/inference/app/config.py": "# Inference configuration",
    "services/inference/app/models/__init__.py": "# Inference Models",
    "services/inference/app/models/lgbm_model.py": "# LightGBM model",
    "services/inference/app/models/autoencoder.py": "# Autoencoder model",
    "services/inference/app/models/graph_model.py": "# Graph model",
    "services/inference/app/models/ensemble.py": "# Ensemble model",
    "services/inference/app/features/__init__.py": "# Features package",
    "services/inference/app/features/transaction_features.py": "# Transaction features",
    "services/inference/app/features/velocity_features.py": "# Velocity features",
    "services/inference/app/features/graph_features.py": "# Graph features",
    "services/inference/app/features/anomaly_features.py": "# Anomaly features",
    "services/inference/app/consumers/__init__.py": "# Consumers package",
    "services/inference/app/consumers/inference_consumer.py": "# Inference consumer",
    "services/inference/app/utils/__init__.py": "# Utils package",
    "services/inference/app/utils/cache.py": "# Cache utilities",
    "services/inference/app/utils/kafka_utils.py": "# Kafka utilities",
    "services/inference/app/utils/model_loader.py": "# Model loader",
    "services/inference/tests/__init__.py": "# Inference tests",

    # Enricher Service
    "services/enricher/__init__.py": "# Enricher Service",
    "services/enricher/app/__init__.py": "# Enricher App",
    "services/enricher/app/main.py": "# Enricher main application",
    "services/enricher/app/config.py": "# Enricher configuration",
    "services/enricher/app/enrichers/__init__.py": "# Enrichers package",
    "services/enricher/app/enrichers/geo_enricher.py": "# Geo enricher",
    "services/enricher/app/enrichers/device_enricher.py": "# Device enricher",
    "services/enricher/app/enrichers/merchant_enricher.py": "# Merchant enricher",
    "services/enricher/app/consumers/__init__.py": "# Consumers package",
    "services/enricher/app/consumers/enrichment_consumer.py": "# Enrichment consumer",
    "services/enricher/app/utils/__init__.py": "# Utils package",
    "services/enricher/app/utils/geo_utils.py": "# Geo utilities",
    "services/enricher/app/utils/device_utils.py": "# Device utilities",
    "services/enricher/tests/__init__.py": "# Enricher tests",

    # Shared modules
    "shared/__init__.py": "# Shared package",
    "shared/schemas/__init__.py": "# Shared schemas",
    "shared/schemas/transaction.py": "# Transaction schema",
    "shared/schemas/decision.py": "# Decision schema",
    "shared/schemas/alert.py": "# Alert schema",
    "shared/schemas/model.py": "# Model schema",
    "shared/utils/__init__.py": "# Shared utils",
    "shared/utils/kafka_client.py": "# Kafka client",
    "shared/utils/redis_client.py": "# Redis client",
    "shared/utils/postgres_client.py": "# Postgres client",
    "shared/utils/neo4j_client.py": "# Neo4j client",
    "shared/utils/minio_client.py": "# MinIO client",
    "shared/constants/__init__.py": "# Constants package",
    "shared/constants/feature_names.py": "# Feature names",
    "shared/constants/model_types.py": "# Model types",
    "shared/constants/alert_types.py": "# Alert types",

    # Tests
    "tests/__init__.py": "# Integration tests",
    "tests/integration/__init__.py": "# Integration tests package",
    "tests/integration/test_end_to_end.py": "# End-to-end tests",
    "tests/integration/test_kafka_flow.py": "# Kafka flow tests",
    "tests/integration/test_model_pipeline.py": "# Model pipeline tests",
    "tests/performance/__init__.py": "# Performance tests",
    "tests/performance/test_latency.py": "# Latency tests",
    "tests/performance/test_throughput.py": "# Throughput tests",
    "tests/fixtures/__init__.py": "# Test fixtures",
}

def create_python_files():
    """Create all Python files with basic content."""
    for file_path, content in python_files.items():
        full_path = BASE_DIR / file_path
        
        # Create directory if it doesn't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file with content
        with open(full_path, 'w') as f:
            f.write(content + '\n')
        
        print(f"Created: {file_path}")

if __name__ == "__main__":
    create_python_files()
    print(f"\\nCreated {len(python_files)} Python files!")
