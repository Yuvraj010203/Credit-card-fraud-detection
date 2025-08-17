from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    ts = Column(DateTime, nullable=False, index=True)
    card_id = Column(String(50), nullable=False, index=True)
    merchant_id = Column(String(50), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    mcc = Column(String(10), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    device_id = Column(String(100))
    ip = Column(String(45))
    city = Column(String(100))
    country = Column(String(2))
    label = Column(Integer, default=0)  # 0=benign, 1=fraud
    raw = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    decisions = relationship("Decision", back_populates="transaction")
    alerts = relationship("Alert", back_populates="transaction")
    features = relationship("TransactionFeature", back_populates="transaction", uselist=False)

class TransactionFeature(Base):
    __tablename__ = "features_tx"
    
    id = Column(Integer, primary_key=True, index=True)
    tx_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, unique=True)
    
    # Temporal features
    hour_sin = Column(Float)
    hour_cos = Column(Float)
    day_of_week = Column(Integer)
    is_weekend = Column(Boolean)
    is_holiday = Column(Boolean)
    
    # Amount features
    amount_log = Column(Float)
    amount_zscore = Column(Float)
    
    # Velocity features
    velocity_1m_count = Column(Integer, default=0)
    velocity_5m_count = Column(Integer, default=0)
    velocity_30m_count = Column(Integer, default=0)
    velocity_120m_count = Column(Integer, default=0)
    velocity_1m_amount = Column(Float, default=0.0)
    velocity_5m_amount = Column(Float, default=0.0)
    velocity_30m_amount = Column(Float, default=0.0)
    velocity_120m_amount = Column(Float, default=0.0)
    
    # Geo features
    distance_from_home = Column(Float)
    country_change = Column(Boolean, default=False)
    
    # Device features
    new_device = Column(Boolean, default=False)
    device_risk_score = Column(Float, default=0.0)
    
    # Merchant features
    merchant_risk_score = Column(Float, default=0.0)
    merchant_novelty = Column(Boolean, default=False)
    
    # Graph embeddings
    card_embedding = Column(JSON)  # List of floats
    merchant_embedding = Column(JSON)  # List of floats
    device_embedding = Column(JSON)  # List of floats
    
    # Anomaly scores
    autoencoder_error = Column(Float)
    isolation_forest_score = Column(Float)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    transaction = relationship("Transaction", back_populates="features")

class Decision(Base):
    __tablename__ = "decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    tx_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, index=True)
    p_fraud = Column(Float, nullable=False)
    score = Column(Float, nullable=False)
    model_version = Column(String(50), nullable=False)
    route = Column(String(20), nullable=False)  # production, shadow, canary
    explanation_json = Column(JSON)
    latency_ms = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    transaction = relationship("Transaction", back_populates="decisions")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    tx_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, index=True)
    severity = Column(String(10), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    reason = Column(Text, nullable=False)
    status = Column(String(20), default="OPEN")  # OPEN, ASSIGNED, RESOLVED, FALSE_POSITIVE
    assigned_to = Column(String(100))
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    transaction = relationship("Transaction", back_populates="alerts")

class Card(Base):
    __tablename__ = "cards"
    
    id = Column(String(50), primary_key=True)
    account_id = Column(String(50), nullable=False)
    age_days = Column(Integer, default=0)
    home_country = Column(String(2))
    home_city = Column(String(100))
    risk_bucket = Column(String(10), default="LOW")  # LOW, MEDIUM, HIGH
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class Merchant(Base):
    __tablename__ = "merchants"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(200))
    mcc = Column(String(10), nullable=False)
    city = Column(String(100))
    country = Column(String(2))
    risk_bucket = Column(String(10), default="LOW")  # LOW, MEDIUM, HIGH
    avg_ticket_size = Column(Float)
    transaction_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(String(100), primary_key=True)
    type = Column(String(50))  # mobile, desktop, tablet
    fingerprint = Column(String(500))
    risk_bucket = Column(String(10), default="LOW")  # LOW, MEDIUM, HIGH
    is_proxy = Column(Boolean, default=False)
    is_vpn = Column(Boolean, default=False)
    first_seen = Column(DateTime, server_default=func.now())
    last_seen = Column(DateTime, server_default=func.now())

class DriftMetric(Base):
    __tablename__ = "drift_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    window_start = Column(DateTime, nullable=False)
    window_end = Column(DateTime, nullable=False)
    
    # PSI metrics
    psi_amount = Column(Float)
    psi_hour = Column(Float)
    psi_country = Column(Float)
    psi_mcc = Column(Float)
    
    # Distribution distance metrics
    js_geo = Column(Float)  # Jensen-Shannon divergence for geo
    ks_amount = Column(Float)  # Kolmogorov-Smirnov test for amount
    
    # Performance metrics
    concept_auc = Column(Float)
    concept_drift_detected = Column(Boolean, default=False)
    
    created_at = Column(DateTime, server_default=func.now())

class Model(Base):
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), nullable=False, unique=True)
    type = Column(String(50), nullable=False)  # lgbm, autoencoder, ensemble
    path = Column(String(500), nullable=False)  # MinIO path
    metrics_json = Column(JSON)  # AUC, precision, recall, etc.
    stage = Column(String(20), default="shadow")  # shadow, canary, production
    traffic_percentage = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())
    promoted_at = Column(DateTime)
    
# Create indexes for performance
Index('idx_transactions_ts_card', Transaction.ts, Transaction.card_id)
Index('idx_transactions_ts_merchant', Transaction.ts, Transaction.merchant_id)
Index('idx_decisions_created_score', Decision.created_at, Decision.score)
Index('idx_alerts_status_severity', Alert.status, Alert.severity)