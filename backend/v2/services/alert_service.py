"""
Alert System Service
====================
Real-time anomaly detection and alert generation for emissions tracking
"""

import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    """Types of alerts"""
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    ANOMALY_DETECTED = "anomaly"
    TREND_CHANGE = "trend_change"
    FORECAST_WARNING = "forecast_warning"
    PATTERN_CHANGE = "pattern_change"


class Alert:
    """Alert object"""
    
    def __init__(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        message: str,
        value: float,
        threshold: float,
        timestamp: datetime = None,
        metadata: Dict = None
    ):
        self.alert_id = self._generate_id()
        self.alert_type = alert_type
        self.severity = severity
        self.message = message
        self.value = value
        self.threshold = threshold
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
        self.acknowledged = False
    
    def _generate_id(self):
        """Generate unique alert ID"""
        return f"alert_{int(datetime.now().timestamp() * 1000)}"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "alert_id": self.alert_id,
            "type": self.alert_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "value": self.value,
            "threshold": self.threshold,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "acknowledged": self.acknowledged
        }


class AlertSystem:
    """Comprehensive alert management system"""
    
    def __init__(self, db: Session = None):
        self.alerts: List[Alert] = []
        self.thresholds = {
            "daily_emissions": 500.0,  # kg CO2
            "weekly_emissions": 3000.0,
            "monthly_emissions": 12000.0,
            "anomaly_zscore": 2.5,  # Standard deviations
            "trend_change_pct": 15.0  # 15% change
        }
        self.alert_history: List[Alert] = []
        self.db = db  # Optional database session
    
    def check_emissions_alert(
        self,
        current_emissions: float,
        period: str = "daily",
        baseline: Optional[float] = None
    ) -> Optional[Alert]:
        """
        Check if emissions exceed threshold
        
        Args:
            current_emissions: Current emission value
            period: "daily", "weekly", or "monthly"
            baseline: Optional baseline for comparison
        
        Returns:
            Alert object if threshold exceeded, None otherwise
        """
        try:
            threshold = self.thresholds.get(f"{period}_emissions", 500.0)
            
            if current_emissions > threshold:
                severity = self._calculate_severity(
                    current_emissions,
                    threshold,
                    max_multiplier=3.0
                )
                
                alert = Alert(
                    alert_type=AlertType.THRESHOLD_EXCEEDED,
                    severity=severity,
                    message=f"Emissions exceeded {period} threshold: {current_emissions:.2f} kg CO2 (threshold: {threshold:.2f})",
                    value=current_emissions,
                    threshold=threshold,
                    metadata={"period": period}
                )
                
                self._store_alert(alert)
                return alert
        
        except Exception as e:
            logger.error(f"Error checking emissions alert: {e}")
        
        return None
    
    def check_anomaly_alert(
        self,
        value: float,
        mean: float,
        std_dev: float
    ) -> Optional[Alert]:
        """
        Check if value is anomalous (Z-score > threshold)
        
        Args:
            value: Current value
            mean: Historical mean
            std_dev: Historical standard deviation
        
        Returns:
            Alert if anomaly detected
        """
        try:
            if std_dev == 0:
                return None
            
            z_score = abs((value - mean) / std_dev)
            threshold = self.thresholds["anomaly_zscore"]
            
            if z_score > threshold:
                severity = AlertSeverity.HIGH if z_score > 3.0 else AlertSeverity.MEDIUM
                
                alert = Alert(
                    alert_type=AlertType.ANOMALY_DETECTED,
                    severity=severity,
                    message=f"Anomaly detected: Z-score = {z_score:.2f} (threshold: {threshold})",
                    value=value,
                    threshold=mean,
                    metadata={
                        "z_score": z_score,
                        "mean": mean,
                        "std_dev": std_dev
                    }
                )
                
                self._store_alert(alert)
                return alert
        
        except Exception as e:
            logger.error(f"Error checking anomaly alert: {e}")
        
        return None
    
    def check_trend_alert(
        self,
        recent_values: List[float],
        historical_avg: float
    ) -> Optional[Alert]:
        """
        Check for significant trend changes
        
        Args:
            recent_values: Recent emission values
            historical_avg: Historical average
        
        Returns:
            Alert if trend change detected
        """
        try:
            if not recent_values or historical_avg == 0:
                return None
            
            recent_avg = sum(recent_values) / len(recent_values)
            change_pct = abs(recent_avg - historical_avg) / historical_avg * 100
            threshold = self.thresholds["trend_change_pct"]
            
            if change_pct > threshold:
                direction = "increase" if recent_avg > historical_avg else "decrease"
                severity = AlertSeverity.HIGH if change_pct > 30 else AlertSeverity.MEDIUM
                
                alert = Alert(
                    alert_type=AlertType.TREND_CHANGE,
                    severity=severity,
                    message=f"Significant trend {direction}: {change_pct:.1f}% change detected",
                    value=recent_avg,
                    threshold=historical_avg,
                    metadata={
                        "direction": direction,
                        "change_pct": change_pct,
                        "recent_avg": recent_avg
                    }
                )
                
                self._store_alert(alert)
                return alert
        
        except Exception as e:
            logger.error(f"Error checking trend alert: {e}")
        
        return None
    
    def check_forecast_alert(
        self,
        forecast: List[float],
        threshold: float
    ) -> Optional[Alert]:
        """
        Check if forecast predicts threshold breach
        
        Args:
            forecast: Forecasted values
            threshold: Alert threshold
        
        Returns:
            Alert if forecast indicates breach
        """
        try:
            if not forecast:
                return None
            
            max_forecast = max(forecast)
            
            if max_forecast > threshold:
                periods_to_breach = next(
                    (i for i, v in enumerate(forecast) if v > threshold),
                    len(forecast)
                )
                
                alert = Alert(
                    alert_type=AlertType.FORECAST_WARNING,
                    severity=AlertSeverity.MEDIUM,
                    message=f"Forecast warns of threshold breach in {periods_to_breach + 1} periods",
                    value=max_forecast,
                    threshold=threshold,
                    metadata={
                        "periods_to_breach": periods_to_breach,
                        "max_forecast": max_forecast
                    }
                )
                
                self._store_alert(alert)
                return alert
        
        except Exception as e:
            logger.error(f"Error checking forecast alert: {e}")
        
        return None
    
    def get_active_alerts(self) -> List[Dict]:
        """Get all unacknowledged alerts"""
        return [
            alert.to_dict() for alert in self.alerts
            if not alert.acknowledged
        ]
    
    def get_alert_summary(self) -> Dict:
        """Get alert summary statistics"""
        active_alerts = self.get_active_alerts()
        
        severity_count = {
            "critical": len([a for a in active_alerts if a["severity"] == "critical"]),
            "high": len([a for a in active_alerts if a["severity"] == "high"]),
            "medium": len([a for a in active_alerts if a["severity"] == "medium"]),
            "low": len([a for a in active_alerts if a["severity"] == "low"])
        }
        
        return {
            "total_alerts": len(active_alerts),
            "severity_breakdown": severity_count,
            "critical_alerts": severity_count["critical"],
            "needs_attention": severity_count["critical"] > 0 or severity_count["high"] > 0,
            "last_alert": (
                self.alerts[-1].timestamp.isoformat()
                if self.alerts else None
            )
        }
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Mark alert as acknowledged"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False
    
    def _calculate_severity(
        self,
        value: float,
        threshold: float,
        max_multiplier: float = 3.0
    ) -> AlertSeverity:
        """Calculate alert severity based on how much value exceeds threshold"""
        multiplier = value / threshold
        
        if multiplier >= max_multiplier:
            return AlertSeverity.CRITICAL
        elif multiplier >= 2.0:
            return AlertSeverity.HIGH
        elif multiplier >= 1.5:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW
    
    def _store_alert(self, alert: Alert):
        """Store alert in active list and database if available"""
        self.alerts.append(alert)
        self.alert_history.append(alert)
        
        # Keep only last 1000 alerts
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
        
        # Store to database if session available
        if self.db:
            self._store_alert_to_db(alert)
    
    def _store_alert_to_db(self, alert: Alert):
        """Store alert to database"""
        try:
            from services.database_service import DatabaseService
            
            DatabaseService.store_alert(
                db=self.db,
                alert_type=alert.alert_type.value,
                severity=alert.severity.value.upper(),
                message=alert.message,
                current_value=alert.value,
                threshold=alert.threshold,
                alert_details={
                    "alert_id": alert.alert_id,
                    "timestamp": alert.timestamp.isoformat() if alert.timestamp else None,
                    "metadata": alert.metadata
                }
            )
        except Exception as e:
            logger.error(f"Database storage error in alert system: {str(e)}")
    
    def set_threshold(self, threshold_name: str, value: float) -> bool:
        """Update threshold value"""
        if threshold_name in self.thresholds:
            self.thresholds[threshold_name] = value
            return True
        return False
    
    def get_thresholds(self) -> Dict:
        """Get current thresholds"""
        return self.thresholds.copy()


# Global alert system instance
alert_system = AlertSystem()


def check_emissions(current: float, period: str = "daily") -> Optional[Dict]:
    """Check emissions threshold"""
    alert = alert_system.check_emissions_alert(current, period)
    return alert.to_dict() if alert else None


def check_anomaly(value: float, mean: float, std_dev: float) -> Optional[Dict]:
    """Check for anomalies"""
    alert = alert_system.check_anomaly_alert(value, mean, std_dev)
    return alert.to_dict() if alert else None


def get_active_alerts() -> List[Dict]:
    """Get active alerts"""
    return alert_system.get_active_alerts()


def get_alert_summary() -> Dict:
    """Get alert summary"""
    return alert_system.get_alert_summary()
