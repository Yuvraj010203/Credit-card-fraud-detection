from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
import time
import logging
from datetime import datetime

from ...database import get_db
from ...models.schemas import TransactionRequest, ScoringResponse
from ...services.scoring import ScoringService
from ...services.feature_service import FeatureService
from ...core.exceptions import ScoringException

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/score", response_model=ScoringResponse)
async def score_transaction(
    transaction: TransactionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    scoring_service: ScoringService = Depends()
):
    """
    Score a single transaction for fraud probability
    """
    start_time = time.time()
    
    try:
        # Generate features
        feature_service = FeatureService()
        features = await feature_service.generate_features(transaction, db)
        
        # Score transaction
        result = await scoring_service.score_transaction(transaction, features, db)
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        result.latency_ms = latency_ms
        
        # Create alert if needed (background task)
        if result.p_fraud > scoring_service.threshold:
            background_tasks.add_task(
                create_alert_if_needed,
                transaction.id,
                result.p_fraud,
                result.reasons,
                db
            )
        
        logger.info(f"Transaction {transaction.id} scored: {result.p_fraud:.4f} ({latency_ms:.2f}ms)")
        return result
        
    except Exception as e:
        logger.error(f"Error scoring transaction {transaction.id}: {e}")
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")

@router.post("/batch-score")
async def batch_score_transactions(
    transactions: list[TransactionRequest],
    db: Session = Depends(get_db),
    scoring_service: ScoringService = Depends()
):
    """
    Score multiple transactions in batch
    """
    if len(transactions) > 1000:
        raise HTTPException(status_code=400, detail="Batch size cannot exceed 1000")
    
    results = []
    feature_service = FeatureService()
    
    for transaction in transactions:
        try:
            features = await feature_service.generate_features(transaction, db)
            result = await scoring_service.score_transaction(transaction, features, db)
            results.append(result)
        except Exception as e:
            logger.error(f"Error in batch scoring transaction {transaction.id}: {e}")
            results.append({
                "tx_id": transaction.id,
                "error": str(e),
                "p_fraud": None
            })
    
    return {"results": results, "total": len(results)}

async def create_alert_if_needed(tx_id: int, fraud_prob: float, reasons: list, db: Session):
    """Background task to create alerts for high-risk transactions"""
    from ...models.database import Alert
    from ...services.alert_service import AlertService
    
    alert_service = AlertService()
    await alert_service.create_alert(tx_id, fraud_prob, reasons, db)