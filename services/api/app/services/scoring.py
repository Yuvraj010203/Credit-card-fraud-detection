import asyncio
import json
import pickle
import logging
from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime

from ..models.schemas import TransactionRequest, ScoringResponse
from ..models.database import Decision
from ..config import settings
from .model_registry import ModelRegistry
from .graph_service import GraphService
from ..utils.redis_client import RedisClient
from ..utils.minio_client import MinIOClient

logger = logging.getLogger(__name__)

class ScoringService:
    def __init__(self):
        self.redis = RedisClient()
        self.minio = MinIOClient()
        self.graph_service = GraphService()
        self.model_registry = ModelRegistry()
        self.threshold = settings.SCORE_THRESHOLD
        
        # Model components
        self.lgbm_model = None
        self.autoencoder = None
        self.shap_explainer = None
        self.feature_scaler = None
        self.ensemble_weights = {"lgbm": 0.6, "graph": 0.25, "anomaly": 0.15}
        
    async def initialize(self):
        """Initialize models and components"""
        await self._load_models()
        
    async def _load_models(self):
        """Load ML models from model registry"""
        try:
            # Get active model version
            active_model = await self.model_registry.get_active_model("ensemble")
            if not active_model:
                logger.warning("No active ensemble model found, using default")
                return
            
            # Load LGBM model
            lgbm_path = f"models/{active_model.version}/lgbm_model.pkl"
            lgbm_data = await self.minio.get_object(settings.MODEL_BUCKET, lgbm_path)
            self.lgbm_model = pickle.loads(lgbm_data)
            
            # Load autoencoder
            ae_path = f"models/{active_model.version}/autoencoder.pt"
            # ae_data = await self.minio.get_object(settings.MODEL_BUCKET, ae_path)
            # self.autoencoder = torch.load(io.BytesIO(ae_data))
            
            # Load SHAP explainer
            shap_path = f"models/{active_model.version}/shap_explainer.pkl"
            shap_data = await self.minio.get_object(settings.MODEL_BUCKET, shap_path)
            self.shap_explainer = pickle.loads(shap_data)
            
            # Load feature scaler
            scaler_path = f"models/{active_model.version}/feature_scaler.pkl"
            scaler_data = await self.minio.get_object(settings.MODEL_BUCKET, scaler_path)
            self.feature_scaler = pickle.loads(scaler_data)
            
            logger.info(f"Loaded models for version {active_model.version}")
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            # Use fallback models or raise exception
    
    async def score_transaction(
        self, 
        transaction: TransactionRequest, 
        features: Dict[str, Any],
        db
    ) -> ScoringResponse:
        """Score a single transaction using ensemble approach"""
        
        try:
            # Prepare feature vector
            feature_vector = self._prepare_feature_vector(features)
            
            # Get graph embeddings
            graph_features = await self._get_graph_features(transaction)
            
            # Combine features
            combined_features = np.concatenate([feature_vector, graph_features])
            
            # Scale features
            if self.feature_scaler:
                combined_features = self.feature_scaler.transform([combined_features])[0]
            
            # Get individual model predictions
            scores = await self._get_ensemble_scores(combined_features, features)
            
            # Calculate final ensemble score
            final_score = (
                self.ensemble_weights["lgbm"] * scores["lgbm"] +
                self.ensemble_weights["graph"] * scores["graph"] +
                self.ensemble_weights["anomaly"] * scores["anomaly"]
            )
            
            # Generate explanations
            explanations = await self._generate_explanations(
                combined_features, scores, features
            )
            
            # Save decision to database
            decision = Decision(
                tx_id=transaction.id,
                p_fraud=final_score,
                score=final_score,
                model_version=settings.MODEL_VERSION,
                route="production",
                explanation_json=explanations
            )
            db.add(decision)
            db.commit()
            
            return ScoringResponse(
                tx_id=transaction.id,
                p_fraud=final_score,
                score=final_score,
                model_version=settings.MODEL_VERSION,
                reasons=explanations.get("top_features", []),
                component_scores=scores,
                is_fraud=final_score > self.threshold
            )
            
        except Exception as e:
            logger.error(f"Error scoring transaction {transaction.id}: {e}")
            raise ScoringException(f"Scoring failed: {str(e)}")
    
    def _prepare_feature_vector(self, features: Dict[str, Any]) -> np.ndarray:
        """Convert feature dict to numpy array"""
        # Define feature order (should match training)
        feature_names = [
            'amount_log', 'hour_sin', 'hour_cos', 'day_of_week', 'is_weekend',
            'velocity_1m_count', 'velocity_5m_count', 'velocity_30m_count',
            'velocity_1m_amount', 'velocity_5m_amount', 'velocity_30m_amount',
            'distance_from_home', 'country_change', 'new_device',
            'merchant_risk_score', 'device_risk_score'
        ]
        
        vector = []
        for name in feature_names:
            value = features.get(name, 0.0)
            if isinstance(value, bool):
                value = float(value)
            vector.append(value)
        
        return np.array(vector, dtype=np.float32)
    
    async def _get_graph_features(self, transaction: TransactionRequest) -> np.ndarray:
        """Get graph embeddings for card, merchant, device"""
        try:
            # Get embeddings from cache or compute
            card_emb = await self.graph_service.get_card_embedding(transaction.card_id)
            merchant_emb = await self.graph_service.get_merchant_embedding(transaction.merchant_id)
            device_emb = await self.graph_service.get_device_embedding(transaction.device_id)
            
            # Concatenate embeddings
            graph_features = np.concatenate([card_emb, merchant_emb, device_emb])
            return graph_features
            
        except Exception as e:
            logger.warning(f"Failed to get graph features: {e}")
            # Return zero embeddings as fallback
            embedding_dim = settings.EMBEDDING_DIMENSION
            return np.zeros(embedding_dim * 3, dtype=np.float32)
    
    async def _get_ensemble_scores(
        self, 
        features: np.ndarray, 
        raw_features: Dict[str, Any]
    ) -> Dict[str, float]:
        """Get scores from different model components"""
        
        scores = {}
        
        # LGBM score
        if self.lgbm_model:
            try:
                lgbm_prob = self.lgbm_model.predict_proba([features[:16]])[0][1]  # First 16 features
                scores["lgbm"] = float(lgbm_prob)
            except:
                scores["lgbm"] = 0.5
        else:
            scores["lgbm"] = 0.5
        
        # Graph neural network score (placeholder)
        # This would use a separate GNN model
        scores["graph"] = 0.3  # Placeholder
        
        # Anomaly detection score
        if self.autoencoder:
            try:
                # reconstruction_error = self.autoencoder.get_reconstruction_error(features)
                # scores["anomaly"] = min(reconstruction_error / 10.0, 1.0)  # Normalize
                scores["anomaly"] = raw_features.get("autoencoder_error", 0.1)
            except:
                scores["anomaly"] = 0.1
        else:
            scores["anomaly"] = raw_features.get("isolation_forest_score", 0.1)
        
        return scores
    
    async def _generate_explanations(
        self,
        features: np.ndarray,
        scores: Dict[str, float],
        raw_features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate human-readable explanations using SHAP"""
        
        explanations = {
            "component_scores": scores,
            "top_features": [],
            "risk_factors": [],
            "graph_insights": []
        }
        
        # SHAP explanations for tabular features
        if self.shap_explainer and self.lgbm_model:
            try:
                shap_values = self.shap_explainer.shap_values([features[:16]])[0]
                feature_names = [
                    'log_amount', 'hour_sin', 'hour_cos', 'day_of_week', 'weekend',
                    'vel_1m_count', 'vel_5m_count', 'vel_30m_count',
                    'vel_1m_amount', 'vel_5m_amount', 'vel_30m_amount',
                    'distance_home', 'country_change', 'new_device',
                    'merchant_risk', 'device_risk'
                ]
                
                # Get top contributing features
                feature_importance = list(zip(feature_names, shap_values))
                feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
                
                for name, importance in feature_importance[:5]:
                    explanations["top_features"].append({
                        "feature": name,
                        "importance": float(importance),
                        "description": self._get_feature_description(name, raw_features)
                    })
                    
            except Exception as e:
                logger.warning(f"SHAP explanation failed: {e}")
        
        # Add risk factor explanations
        self._add_risk_factors(explanations, raw_features, scores)
        
        return explanations
    
    def _get_feature_description(self, feature_name: str, features: Dict[str, Any]) -> str:
        """Get human-readable description of feature contribution"""
        descriptions = {
            'log_amount': f"Transaction amount: ${features.get('amount', 0):.2f}",
            'hour_sin': f"Time of day: {features.get('hour', 0)}:00",
            'weekend': "Weekend transaction" if features.get('is_weekend') else "Weekday transaction",
            'vel_1m_count': f"Recent activity: {features.get('velocity_1m_count', 0)} transactions in 1 min",
            'vel_5m_count': f"Recent activity: {features.get('velocity_5m_count', 0)} transactions in 5 min",
            'distance_home': f"Distance from home: {features.get('distance_from_home', 0):.1f} km",
            'country_change': "International transaction" if features.get('country_change') else "Domestic transaction",
            'new_device': "New device detected" if features.get('new_device') else "Known device",
            'merchant_risk': f"Merchant risk score: {features.get('merchant_risk_score', 0):.2f}",
            'device_risk': f"Device risk score: {features.get('device_risk_score', 0):.2f}"
        }
        return descriptions.get(feature_name, f"{feature_name}: {features.get(feature_name, 'N/A')}")
    
    def _add_risk_factors(self, explanations: Dict, features: Dict[str, Any], scores: Dict[str, float]):
        """Add specific risk factors to explanations"""
        risk_factors = []
        
        # High velocity
        if features.get('velocity_1m_count', 0) > 3:
            risk_factors.append("Multiple transactions in short time window")
        
        # Geographic anomaly
        if features.get('distance_from_home', 0) > 1000:
            risk_factors.append("Transaction far from usual location")
        
        # New device
        if features.get('new_device'):
            risk_factors.append("First-time device usage")
        
        # High-risk merchant
        if features.get('merchant_risk_score', 0) > 0.7:
            risk_factors.append("High-risk merchant category")
        
        # Unusual amount
        if features.get('amount_zscore', 0) > 3:
            risk_factors.append("Unusually large transaction amount")
        
        explanations["risk_factors"] = risk_factors