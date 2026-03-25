"""
Anomaly Detection Service for CarbonSense v2
Detects unusual emissions patterns using Isolation Forest + Statistical Methods
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sklearn.ensemble import IsolationForest
import numpy as np
import statistics


@dataclass
class AnomalyPoint:
    """Single anomaly detection result"""
    month: int
    value: float
    is_anomaly: bool
    anomaly_score: float  # -1 to 1, where 1 is most anomalous
    deviation_pct: float  # % deviation from expected
    method: str  # "isolation_forest" or "statistical"
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"


@dataclass
class AnomalyResult:
    """Complete anomaly detection results"""
    anomalies_detected: List[AnomalyPoint]
    anomaly_count: int
    anomaly_percentage: float
    average_anomaly_score: float
    statistical_summary: Dict[str, float]
    trend_analysis: Dict[str, Any]
    recommendations: List[str]
    overall_health: str  # "HEALTHY", "WARNING", "ALERT", "CRITICAL"


class AnomalyDetectionService:
    """Detect anomalies in emissions data using multiple methods"""
    
    def __init__(self, contamination: float = 0.1):
        """
        Initialize anomaly detection service
        
        Args:
            contamination: Expected fraction of outliers (10% default)
        """
        self.contamination = contamination
        self.iso_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
    
    def detect_anomalies(
        self,
        historical_data: List[float],
        sensitivity: str = "medium",
        db: Session = None
    ) -> AnomalyResult:
        """
        Detect anomalies using ensemble of methods
        
        Args:
            historical_data: Time series of emissions (CO2 kg)
            sensitivity: "low" (only extreme), "medium" (balanced), "high" (sensitive)
        
        Returns:
            AnomalyResult with identified anomalies and analysis
        """
        
        if not historical_data or len(historical_data) < 4:
            raise ValueError("Need at least 4 historical data points")
        
        data_array = np.array(historical_data).reshape(-1, 1)
        
        # Apply Isolation Forest
        iso_predictions = self.iso_forest.fit_predict(data_array)
        iso_scores = self.iso_forest.score_samples(data_array)
        
        # Apply statistical method
        stat_anomalies = self._detect_statistical_anomalies(historical_data, sensitivity)
        
        # Combine methods
        anomalies = self._merge_detections(
            historical_data,
            iso_predictions,
            iso_scores,
            stat_anomalies,
            sensitivity
        )
        
        # Analyze trends
        trend_analysis = self._analyze_trend(historical_data, anomalies)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            historical_data,
            anomalies,
            trend_analysis
        )
        
        # Determine overall health
        overall_health = self._determine_health(anomalies)
        
        result = AnomalyResult(
            anomalies_detected=anomalies,
            anomaly_count=len([a for a in anomalies if a.is_anomaly]),
            anomaly_percentage=len([a for a in anomalies if a.is_anomaly]) / len(anomalies) * 100,
            average_anomaly_score=np.mean([a.anomaly_score for a in anomalies if a.is_anomaly]) if anomalies else 0,
            statistical_summary=self._calculate_summary(historical_data),
            trend_analysis=trend_analysis,
            recommendations=recommendations,
            overall_health=overall_health
        )
        
        # Store in database if session provided
        if db:
            self._store_anomaly_result(db, result)
        
        return result
    
    def _store_anomaly_result(self, db: Session, result: AnomalyResult) -> None:
        """Store anomaly detection result in database"""
        try:
            from services.database_service import DatabaseService
            
            # Store each detected anomaly
            for anomaly_point in result.anomalies_detected:
                if anomaly_point.is_anomaly:
                    DatabaseService.store_anomaly(
                        db=db,
                        is_anomaly=True,
                        anomaly_score=anomaly_point.anomaly_score,
                        severity=anomaly_point.severity,
                        deviation_pct=anomaly_point.deviation_pct,
                        anomaly_details={
                            "month": anomaly_point.month,
                            "value": anomaly_point.value,
                            "method": anomaly_point.method,
                            "recommendations": result.recommendations
                        }
                    )
        except Exception as e:
            # Log error but don't fail the detection
            print(f"Database storage error in anomaly detection: {str(e)}")
    
    def _detect_statistical_anomalies(
        self,
        data: List[float],
        sensitivity: str
    ) -> List[Tuple[int, bool]]:
        """
        Detect anomalies using statistical methods (z-score, IQR)
        
        Returns:
            List of (index, is_anomaly) tuples
        """
        
        if len(data) < 4:
            return [(i, False) for i in range(len(data))]
        
        # Z-score method
        mean = statistics.mean(data)
        stdev = statistics.stdev(data)
        
        if stdev == 0:
            return [(i, False) for i in range(len(data))]
        
        # Sensitivity thresholds
        thresholds = {
            "low": 3.0,      # Only extreme outliers
            "medium": 2.5,   # Balanced
            "high": 2.0      # Sensitive
        }
        threshold = thresholds.get(sensitivity, 2.5)
        
        anomalies = []
        for i, value in enumerate(data):
            z_score = abs((value - mean) / stdev)
            is_anomaly = z_score > threshold
            anomalies.append((i, is_anomaly))
        
        return anomalies
    
    def _merge_detections(
        self,
        data: List[float],
        iso_predictions: np.ndarray,
        iso_scores: np.ndarray,
        stat_anomalies: List[Tuple[int, bool]],
        sensitivity: str
    ) -> List[AnomalyPoint]:
        """
        Merge Isolation Forest and statistical detections
        """
        
        # Normalize isolation forest scores to 0-1 range
        iso_scores_norm = (iso_scores - iso_scores.min()) / (iso_scores.max() - iso_scores.min() + 1e-10)
        
        # Calculate expected value
        mean_val = np.mean(data)
        
        anomaly_points = []
        for i, value in enumerate(data):
            # Isolation Forest detection
            is_iso_anomaly = iso_predictions[i] == -1
            iso_score = iso_scores_norm[i]
            
            # Statistical detection
            is_stat_anomaly = stat_anomalies[i][1]
            
            # Combined decision (both methods agree or strong signal)
            is_anomaly = is_iso_anomaly or is_stat_anomaly
            
            # Calculate deviation
            deviation_pct = ((value - mean_val) / mean_val * 100) if mean_val != 0 else 0
            
            # Determine method and severity
            if is_iso_anomaly and is_stat_anomaly:
                method = "ensemble"
                severity = self._calculate_severity(abs(deviation_pct), iso_score)
            elif is_iso_anomaly:
                method = "isolation_forest"
                severity = self._calculate_severity(abs(deviation_pct), iso_score)
            elif is_stat_anomaly:
                method = "statistical"
                severity = self._calculate_severity(abs(deviation_pct), iso_score)
            else:
                method = "none"
                severity = "LOW"
            
            anomaly_points.append(AnomalyPoint(
                month=i + 1,
                value=value,
                is_anomaly=is_anomaly,
                anomaly_score=float(iso_score),
                deviation_pct=float(deviation_pct),
                method=method,
                severity=severity
            ))
        
        return anomaly_points
    
    def _calculate_severity(self, deviation_pct: float, anomaly_score: float) -> str:
        """Calculate severity level"""
        
        # Weighted combination
        weighted_severity = (abs(deviation_pct) * 0.6 + anomaly_score * 100 * 0.4)
        
        if weighted_severity > 70:
            return "CRITICAL"
        elif weighted_severity > 50:
            return "HIGH"
        elif weighted_severity > 30:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _analyze_trend(
        self,
        data: List[float],
        anomalies: List[AnomalyPoint]
    ) -> Dict[str, Any]:
        """Analyze trend and anomaly patterns"""
        
        anomalous_values = [a.value for a in anomalies if a.is_anomaly]
        normal_values = [a.value for a in anomalies if not a.is_anomaly]
        
        analysis = {
            "total_points": len(data),
            "anomaly_count": len(anomalous_values),
            "normal_count": len(normal_values),
            "anomaly_percentage": len(anomalous_values) / len(data) * 100,
        }
        
        if normal_values:
            analysis["normal_mean"] = float(np.mean(normal_values))
            analysis["normal_std"] = float(np.std(normal_values))
        
        if anomalous_values:
            analysis["anomaly_mean"] = float(np.mean(anomalous_values))
            analysis["anomaly_max"] = float(max(anomalous_values))
            analysis["anomaly_min"] = float(min(anomalous_values))
        
        # Trend detection
        if len(data) >= 3:
            recent_3 = data[-3:]
            if recent_3[-1] > recent_3[0] * 1.1:
                analysis["trend"] = "INCREASING"
            elif recent_3[-1] < recent_3[0] * 0.9:
                analysis["trend"] = "DECREASING"
            else:
                analysis["trend"] = "STABLE"
        
        return analysis
    
    def _generate_recommendations(
        self,
        data: List[float],
        anomalies: List[AnomalyPoint],
        trend_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # High anomaly percentage
        if trend_analysis.get("anomaly_percentage", 0) > 25:
            recommendations.append(
                "⚠️ High anomaly rate (>25%) - Review data collection and sensor calibration"
            )
        
        # Increasing trend with anomalies
        if trend_analysis.get("trend") == "INCREASING" and anomalies:
            critical_anomalies = [a for a in anomalies if a.severity == "CRITICAL"]
            if critical_anomalies:
                recommendations.append(
                    f"🔴 URGENT: {len(critical_anomalies)} critical anomalies detected with increasing trend"
                )
                recommendations.append(
                    "Implement immediate emissions reduction measures (renewable energy, process optimization)"
                )
        
        # Specific anomaly patterns
        high_severity = [a for a in anomalies if a.severity in ["HIGH", "CRITICAL"]]
        if high_severity:
            avg_dev = np.mean([a.deviation_pct for a in high_severity])
            if avg_dev > 50:
                recommendations.append(
                    f"Critical spike detected (+{avg_dev:.1f}%) - Investigate operational changes or equipment malfunction"
                )
            elif avg_dev < -50:
                recommendations.append(
                    f"Significant reduction achieved ({avg_dev:.1f}%) - Document improvement measures for scaling"
                )
        
        # Clustering of anomalies
        if len(anomalies) >= 5:
            anomaly_indices = [i for i, a in enumerate(anomalies) if a.is_anomaly]
            if anomaly_indices:
                max_gap = max([anomaly_indices[i+1] - anomaly_indices[i] 
                              for i in range(len(anomaly_indices)-1)] + [0])
                if max_gap <= 3:
                    recommendations.append(
                        "Consecutive anomalies detected - Indicates systematic issue (process change, equipment upgrade)"
                    )
        
        # Default recommendation
        if not recommendations:
            recommendations.append(
                "✅ Emissions stable with minimal anomalies - Continue current monitoring protocol"
            )
        
        return recommendations
    
    def _determine_health(self, anomalies: List[AnomalyPoint]) -> str:
        """Determine overall health status"""
        
        critical_count = len([a for a in anomalies if a.severity == "CRITICAL" and a.is_anomaly])
        high_count = len([a for a in anomalies if a.severity == "HIGH" and a.is_anomaly])
        
        if critical_count >= 3:
            return "CRITICAL"
        elif critical_count > 0 or high_count >= 5:
            return "ALERT"
        elif high_count > 0:
            return "WARNING"
        else:
            return "HEALTHY"
    
    def _calculate_summary(self, data: List[float]) -> Dict[str, float]:
        """Calculate statistical summary"""
        
        return {
            "mean": float(np.mean(data)),
            "median": float(np.median(data)),
            "std_dev": float(np.std(data)),
            "min": float(np.min(data)),
            "max": float(np.max(data)),
            "q25": float(np.percentile(data, 25)),
            "q75": float(np.percentile(data, 75)),
        }
    
    def get_anomaly_summary_ai(self, result: AnomalyResult) -> Dict[str, Any]:
        """
        Generate AI-powered summary and insights
        
        Args:
            result: AnomalyResult from detect_anomalies
        
        Returns:
            Dict with summary, insights, and next steps
        """
        
        summary = {
            "health_status": result.overall_health,
            "anomalies_found": result.anomaly_count,
            "anomaly_rate_pct": round(result.anomaly_percentage, 1),
            "severity_distribution": self._get_severity_distribution(result.anomalies_detected),
            "trend": result.trend_analysis.get("trend", "UNKNOWN"),
            "key_metrics": {
                "mean_emissions_kg": round(result.statistical_summary.get("mean", 0), 2),
                "std_deviation_kg": round(result.statistical_summary.get("std_dev", 0), 2),
                "min_emissions_kg": round(result.statistical_summary.get("min", 0), 2),
                "max_emissions_kg": round(result.statistical_summary.get("max", 0), 2),
            },
            "recommendations": result.recommendations,
            "next_actions": self._generate_next_actions(result)
        }
        
        return summary
    
    def _get_severity_distribution(self, anomalies: List[AnomalyPoint]) -> Dict[str, int]:
        """Count anomalies by severity"""
        
        distribution = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0
        }
        
        for anomaly in anomalies:
            if anomaly.is_anomaly:
                distribution[anomaly.severity] += 1
        
        return distribution
    
    def _generate_next_actions(self, result: AnomalyResult) -> List[str]:
        """Generate prioritized next actions"""
        
        actions = []
        health = result.overall_health
        
        if health == "CRITICAL":
            actions.append("1. IMMEDIATE: Initiate emergency emissions audit")
            actions.append("2. Contact facilities management for equipment inspection")
            actions.append("3. Prepare incident report and root cause analysis")
        elif health == "ALERT":
            actions.append("1. HIGH PRIORITY: Schedule comprehensive emissions review")
            actions.append("2. Conduct equipment maintenance check")
            actions.append("3. Verify data sensors and reporting accuracy")
        elif health == "WARNING":
            actions.append("1. Monitor anomalies closely over next 48 hours")
            actions.append("2. Review operational changes from past week")
            actions.append("3. Plan maintenance for next scheduled window")
        else:
            actions.append("1. Continue standard monitoring protocol")
            actions.append("2. Monthly review of anomaly trends")
            actions.append("3. Update baseline expectations")
        
        return actions
