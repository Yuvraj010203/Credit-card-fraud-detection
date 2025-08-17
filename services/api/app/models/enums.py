"""
Enums for the application.
"""

from enum import Enum


class ModelType(str, Enum):
    """Model types."""
    LIGHTGBM = "lightgbm"
    AUTOENCODER = "autoencoder"
    GRAPH = "graph"
    ENSEMBLE = "ensemble"


class FeatureType(str, Enum):
    """Feature types."""
    TRANSACTION = "transaction"
    VELOCITY = "velocity"
    GRAPH = "graph"
    ANOMALY = "anomaly"


class AlertType(str, Enum):
    """Alert types."""
    FRAUD_DETECTED = "fraud_detected"
    HIGH_RISK_TRANSACTION = "high_risk_transaction"
    MODEL_DRIFT = "model_drift"
    SYSTEM_ERROR = "system_error"
    VELOCITY_BREACH = "velocity_breach"
    PATTERN_ANOMALY = "pattern_anomaly"
