from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class TransactionRequest(BaseModel):
    id: int
    timestamp: datetime
    card_id: str = Field(..., min_length=1, max_length=50)
    merchant_id: str = Field(..., min_length=1, max_length=50)
    amount: float = Field(..., gt=0, le=1000000)
    mcc: str = Field(..., min_length=4, max_length=4)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    device_id: Optional[str] = Field(None, max_length=100)
    ip: Optional[str] = Field(None, max_length=45)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    
    @validator('mcc')
    def validate_mcc(cls, v):
        if not v.isdigit():
            raise ValueError('MCC must be numeric')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "id": 12345,
                "timestamp": "2024-01-15T14:30:00Z",
                "card_id": "card_123456",
                "merchant_id": "merch_987654",
                "amount": 127.50,
                "mcc": "5411",
                "currency": "USD",
                "device_id": "device_abc123",
                "ip": "192.168.1.100",
                "city": "New York",
                "country": "US"
            }
        }

class FeatureExplanation(BaseModel):
    feature: str
    importance: float
    description: str

class ScoringResponse(BaseModel):
    tx_id: int
    p_fraud: float = Field(..., ge=0, le=1)
    score: float = Field(..., ge=0, le=1)
    model_version: str
    reasons: List[FeatureExplanation] = []
    component_scores: Dict[str, float] = {}
    is_fraud: bool
    latency_ms: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                "tx_id": 12345,
                "p_fraud": 0.85,
                "score": 0.85,
                "model_version": "v1.2.0",
                "reasons": [
                    {
                        "feature": "velocity_1m_count",
                        "importance": 0.25,
                        "description": "5 transactions in 1 minute"
                    }
                ],
                "component_scores": {
                    "lgbm": 0.82,
                    "graph": 0.76,
                    "anomaly": 0.91
                },
                "is_fraud": True,
                "latency_ms": 23.5
            }
        }

class AlertSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM" 
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertStatus(str, Enum):
    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"

class AlertResponse(BaseModel):
    id: int
    tx_id: int
    severity: AlertSeverity
    reason: str
    status: AlertStatus
    created_at: datetime
    assigned_to: Optional[str] = None
    
class DecisionResponse(BaseModel):
    id: int
    tx_id: int
    p_fraud: float
    score: float
    model_version: str
    route: str
    created_at: datetime
    latency_ms: Optional[float] = None

class ModelStage(str, Enum):
    SHADOW = "shadow"
    CANARY = "canary" 
    PRODUCTION = "production"

class ModelResponse(BaseModel):
    id: int
    version: str
    type: str
    stage: ModelStage
    traffic_percentage: float
    metrics: Dict[str, Any]
    created_at: datetime
    promoted_at: Optional[datetime] = None
        