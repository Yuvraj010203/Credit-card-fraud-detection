import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import math
import numpy as np
from geopy.distance import geodesic
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.schemas import TransactionRequest
from ..models.database import Transaction, Card, Merchant, Device
from ..utils.redis_client import RedisClient
from ..utils.geo_utils import get_country_coordinates, is_holiday
from ..config import settings

logger = logging.getLogger(__name__)

class FeatureService:
    def __init__(self):
        self.redis = RedisClient()
        
    async def generate_features(
        self, 
        transaction: TransactionRequest, 
        db: Session
    ) -> Dict[str, Any]:
        """Generate all features for a transaction"""
        
        features = {}
        
        # Basic transaction features
        features.update(self._get_basic_features(transaction))
        
        # Temporal features
        features.update(self._get_temporal_features(transaction.timestamp))
        
        # Velocity features (async)
        velocity_features = await self._get_velocity_features(transaction)
        features.update(velocity_features)
        
        # Geographic features
        geo_features = await self._get_geographic_features(transaction, db)
        features.update(geo_features)
        
        # Device features
        device_features = await self._get_device_features(transaction, db)
        features.update(device_features)
        
        # Merchant features
        merchant_features = await self._get_merchant_features(transaction, db)
        features.update(merchant_features)
        
        # Entity risk scores
        risk_features = await self._get_risk_features(transaction, db)
        features.update(risk_features)
        
        return features
    
    def _get_basic_features(self, transaction: TransactionRequest) -> Dict[str, Any]:
        """Basic transaction features"""
        return {
            'amount': transaction.amount,
            'amount_log': math.log1p(transaction.amount),
            'currency': transaction.currency,
            'mcc': transaction.mcc
        }
    
    def _get_temporal_features(self, timestamp: datetime) -> Dict[str, Any]:
        """Time-based features with cyclical encoding"""
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        
        return {
            'hour': hour,
            'hour_sin': math.sin(2 * math.pi * hour / 24),
            'hour_cos': math.cos(2 * math.pi * hour / 24),
            'day_of_week': day_of_week,
            'is_weekend': day_of_week >= 5,
            'is_holiday': is_holiday(timestamp.date()),
            'month': timestamp.month
        }
    
    async def _get_velocity_features(self, transaction: TransactionRequest) -> Dict[str, Any]:
        """Calculate velocity features using Redis"""
        features = {}
        current_time = transaction.timestamp
        
        # Time windows in minutes
        windows = settings.VELOCITY_WINDOW_MINUTES
        
        for window in windows:
            # Count-based velocity
            count_key = f"velocity:count:{transaction.card_id}:{window}m"
            count = await self.redis.get_count_in_window(count_key, window * 60)
            features[f'velocity_{window}m_count'] = count
            
            # Amount-based velocity
            amount_key = f"velocity:amount:{transaction.card_id}:{window}m"
            total_amount = await self.redis.get_sum_in_window(amount_key, window * 60)
            features[f'velocity_{window}m_amount'] = total_amount
            
            # Update counters for future calculations
            await self.redis.increment_counter(count_key, 1, window * 60)
            await self.redis.increment_counter(amount_key, transaction.amount, window * 60)
        
        return features
    
    async def _get_geographic_features(
        self, 
        transaction: TransactionRequest, 
        db: Session
    ) -> Dict[str, Any]:
        """Geographic and location-based features"""
        features = {
            'country': transaction.country,
            'city': transaction.city,
            'distance_from_home': 0.0,
            'country_change': False
        }
        
        try:
            # Get card's home location
            card = db.query(Card).filter(Card.id == transaction.card_id).first()
            if card and card.home_country:
                # Check for country change
                features['country_change'] = (card.home_country != transaction.country)
                
                # Calculate distance from home
                if card.home_city and transaction.city:
                    home_coords = get_country_coordinates(card.home_country, card.home_city)
                    tx_coords = get_country_coordinates(transaction.country, transaction.city)
                    
                    if home_coords and tx_coords:
                        distance = geodesic(home_coords, tx_coords).kilometers
                        features['distance_from_home'] = distance
            
            # Get recent geographic pattern
            recent_countries = await self._get_recent_countries(transaction.card_id)
            features['recent_country_count'] = len(set(recent_countries))
            features['geographic_velocity'] = len(recent_countries) > 2
            
        except Exception as e:
            logger.warning(f"Error calculating geographic features: {e}")
        
        return features
    
    async def _get_device_features(
        self, 
        transaction: TransactionRequest, 
        db: Session
    ) -> Dict[str, Any]:
        """Device-based features"""
        features = {
            'device_id': transaction.device_id,
            'new_device': False,
            'device_risk_score': 0.0,
            'device_card_count': 1
        }
        
        if not transaction.device_id:
            return features
        
        try:
            # Check if device exists
            device = db.query(Device).filter(Device.id == transaction.device_id).first()
            
            if not device:
                features['new_device'] = True
                features['device_risk_score'] = 0.5  # New devices are medium risk
            else:
                # Calculate device risk score based on historical usage
                device_tx_count = db.query(func.count(Transaction.id))\
                    .filter(Transaction.device_id == transaction.device_id)\
                    .scalar()
                
                # Device used by multiple cards is riskier
                card_count = db.query(func.count(func.distinct(Transaction.card_id)))\
                    .filter(Transaction.device_id == transaction.device_id)\
                    .scalar()
                
                features['device_card_count'] = card_count
                
                # Risk calculation
                risk_score = 0.1  # Base risk
                if card_count > 5:  # Device used by many cards
                    risk_score += 0.4
                if device.is_proxy or device.is_vpn:
                    risk_score += 0.3
                
                features['device_risk_score'] = min(risk_score, 1.0)
        
        except Exception as e:
            logger.warning(f"Error calculating device features: {e}")
        
        return features
    
    async def _get_merchant_features(
        self, 
        transaction: TransactionRequest, 
        db: Session
    ) -> Dict[str, Any]:
        """Merchant-based features"""
        features = {
            'merchant_id': transaction.merchant_id,
            'merchant_risk_score': 0.0,
            'merchant_novelty': False,
            'merchant_avg_ticket': 0.0
        }
        
        try:
            merchant = db.query(Merchant).filter(
                Merchant.id == transaction.merchant_id
            ).first()
            
            if merchant:
                features['merchant_risk_score'] = self._get_merchant_risk_score(merchant)
                features['merchant_avg_ticket'] = merchant.avg_ticket_size or 0.0
                
                # Check if card has used this merchant before
                previous_tx = db.query(Transaction).filter(
                    Transaction.card_id == transaction.card_id,
                    Transaction.merchant_id == transaction.merchant_id
                ).first()
                
                features['merchant_novelty'] = previous_tx is None
            else:
                # New merchant
                features['merchant_novelty'] = True
                features['merchant_risk_score'] = 0.3  # Unknown merchants are medium risk
        
        except Exception as e:
            logger.warning(f"Error calculating merchant features: {e}")
        
        return features
    
    async def _get_risk_features(
        self, 
        transaction: TransactionRequest, 
        db: Session
    ) -> Dict[str, Any]:
        """Risk-based aggregated features"""
        features = {}
        
        try:
            # Card age and risk bucket
            card = db.query(Card).filter(Card.id == transaction.card_id).first()
            if card:
                features['card_age_days'] = card.age_days
                features['card_risk_bucket'] = card.risk_bucket
            
            # Amount z-score relative to card's history
            avg_amount = db.query(func.avg(Transaction.amount))\
                .filter(Transaction.card_id == transaction.card_id)\
                .scalar() or transaction.amount
            
            std_amount = db.query(func.stddev(Transaction.amount))\
                .filter(Transaction.card_id == transaction.card_id)\
                .scalar() or 1.0
            
            features['amount_zscore'] = (transaction.amount - avg_amount) / max(std_amount, 1.0)
            
            # Time since last transaction
            last_tx = db.query(Transaction)\
                .filter(Transaction.card_id == transaction.card_id)\
                .order_by(Transaction.ts.desc())\
                .first()
            
            if last_tx:
                time_diff = (transaction.timestamp - last_tx.ts).total_seconds() / 3600
                features['hours_since_last_tx'] = time_diff
            else:
                features['hours_since_last_tx'] = 999.0  # Large value for first transaction
        
        except Exception as e:
            logger.warning(f"Error calculating risk features: {e}")
        
        return features
    
    def _get_merchant_risk_score(self, merchant: Merchant) -> float:
        """Calculate merchant risk score based on MCC and historical data"""
        # High-risk MCCs
        high_risk_mccs = {
            '7995',  # Betting/Casino Gambling
            '6012',  # Customer Financial Institution
            '6051',  # Non-FI, Credit Card Member Financial Institution
            '4816',  # Computer Network Services
            '5933',  # Pawn Shops
            '7273',  # Dating/Personal Services
            '5122',  # Drugs/Proprietaries/Sundry
            '7299'   # Miscellaneous Services
        }
        
        base_risk = 0.1
        if merchant.mcc in high_risk_mccs:
            base_risk += 0.4
        
        # Merchant-specific risk based on bucket
        if merchant.risk_bucket == 'HIGH':
            base_risk += 0.3
        elif merchant.risk_bucket == 'MEDIUM':
            base_risk += 0.1
        
        return min(base_risk, 1.0)
    
    async def _get_recent_countries(self, card_id: str, hours: int = 24) -> List[str]:
        """Get list of countries used by card in recent hours"""
        key = f"recent_countries:{card_id}"
        countries = await self.redis.get_recent_items(key, hours * 3600)
        return countries or []