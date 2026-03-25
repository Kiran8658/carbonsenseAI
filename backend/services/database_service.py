"""
Database Service
Handles all database operations for storing and retrieving data
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.db_models import (
    UserInputData, HistoricalData, PredictionData,
    AnomalyData, AlertData, ReportData, CSVImportLog
)


class DatabaseService:
    """Service for all database operations"""

    @staticmethod
    def store_user_input(
        db: Session,
        sector: str,
        emissions_value: float,
        description: str = None,
        source: str = "api",
        metadata: Dict = None
    ) -> UserInputData:
        """Store user-entered emissions data"""
        user_input = UserInputData(
            sector=sector,
            emissions_value=emissions_value,
            description=description,
            source=source,
            meta=metadata or {}
        )
        db.add(user_input)
        db.commit()
        db.refresh(user_input)
        print(f"✓ Stored user input: {sector} = {emissions_value} kg CO2 (ID: {user_input.id})")
        return user_input

    @staticmethod
    def store_historical_data(
        db: Session,
        timestamps: List[datetime],
        values: List[float],
        sector: str = "general",
        data_source: str = "csv",
        is_training: bool = True
    ) -> List[HistoricalData]:
        """Store batch of historical data"""
        records = []
        for timestamp, value in zip(timestamps, values):
            record = HistoricalData(
                timestamp=timestamp,
                sector=sector,
                emissions_value=value,
                data_source=data_source,
                is_training_data=1 if is_training else 0
            )
            records.append(record)
        
        db.add_all(records)
        db.commit()
        print(f"✓ Stored {len(records)} historical data points")
        return records

    @staticmethod
    def store_prediction(
        db: Session,
        prediction_type: str,
        predicted_value: float,
        input_id: Optional[int] = None,
        confidence_score: float = None,
        confidence_interval_low: float = None,
        confidence_interval_high: float = None,
        input_features: Dict = None,
        prediction_result: Dict = None,
        model_version: str = None
    ) -> PredictionData:
        """Store prediction result"""
        prediction = PredictionData(
            input_id=input_id,
            prediction_type=prediction_type,
            predicted_value=predicted_value,
            confidence_score=confidence_score,
            confidence_interval_low=confidence_interval_low,
            confidence_interval_high=confidence_interval_high,
            input_features=input_features or {},
            prediction_result=prediction_result or {},
            model_version=model_version
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        print(f"✓ Stored {prediction_type} prediction: {predicted_value} (ID: {prediction.id})")
        return prediction

    @staticmethod
    def store_anomaly(
        db: Session,
        is_anomaly: bool,
        anomaly_score: float,
        severity: str,
        deviation_percent: float,
        detection_method: str,
        input_id: Optional[int] = None,
        baseline_value: float = None,
        details: Dict = None
    ) -> AnomalyData:
        """Store anomaly detection result"""
        anomaly = AnomalyData(
            input_id=input_id,
            is_anomaly=1 if is_anomaly else 0,
            anomaly_score=anomaly_score,
            severity=severity,
            deviation_percent=deviation_percent,
            detection_method=detection_method,
            baseline_value=baseline_value,
            meta=details or {}
        )
        db.add(anomaly)
        db.commit()
        db.refresh(anomaly)
        status = "ANOMALY DETECTED" if is_anomaly else "NORMAL"
        print(f"✓ Stored anomaly result: {status}, Severity: {severity} (ID: {anomaly.id})")
        return anomaly

    @staticmethod
    def store_alert(
        db: Session,
        alert_type: str,
        severity: str,
        current_value: float,
        message: str,
        threshold_value: float = None,
        metadata: Dict = None
    ) -> AlertData:
        """Store generated alert"""
        alert = AlertData(
            alert_type=alert_type,
            severity=severity,
            current_value=current_value,
            threshold_value=threshold_value,
            message=message,
            is_active=1,
            meta=metadata or {}
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        print(f"✓ Stored alert: {alert_type} ({severity}) - {message} (ID: {alert.id})")
        return alert

    @staticmethod
    def store_report(
        db: Session,
        report_type: str,
        report_content: Dict,
        data_period_start: datetime,
        data_period_end: datetime,
        total_emissions: float,
        summary: str = None,
        metadata: Dict = None
    ) -> ReportData:
        """Store generated report"""
        report = ReportData(
            report_type=report_type,
            report_content=report_content,
            summary=summary,
            data_period_start=data_period_start,
            data_period_end=data_period_end,
            total_emissions=total_emissions,
            metadata=metadata or {}
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        print(f"✓ Stored {report_type} report: {total_emissions} kg CO2 (ID: {report.id})")
        return report

    @staticmethod
    def log_csv_import(
        db: Session,
        filename: str,
        rows_imported: int,
        rows_failed: int = 0,
        error_message: str = None,
        import_summary: Dict = None
    ) -> CSVImportLog:
        """Log CSV import operation"""
        status = "success" if rows_failed == 0 else "partial" if rows_imported > 0 else "failed"
        
        log = CSVImportLog(
            filename=filename,
            rows_imported=rows_imported,
            rows_failed=rows_failed,
            import_status=status,
            error_message=error_message,
            import_summary=import_summary or {}
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        print(f"✓ Logged CSV import: {filename} ({rows_imported} rows, Status: {status})")
        return log

    # Retrieval Methods

    @staticmethod
    def get_user_inputs(db: Session, limit: int = 100) -> List[UserInputData]:
        """Get recent user input data"""
        return db.query(UserInputData).order_by(desc(UserInputData.timestamp)).limit(limit).all()

    @staticmethod
    def get_predictions_by_type(db: Session, prediction_type: str, limit: int = 50) -> List[PredictionData]:
        """Get predictions by type"""
        return db.query(PredictionData).filter(
            PredictionData.prediction_type == prediction_type
        ).order_by(desc(PredictionData.timestamp)).limit(limit).all()

    @staticmethod
    def get_active_alerts(db: Session) -> List[AlertData]:
        """Get active (unacknowledged) alerts"""
        return db.query(AlertData).filter(
            AlertData.is_active == 1
        ).order_by(desc(AlertData.created_at)).all()

    @staticmethod
    def get_anomalies(db: Session, severity: str = None) -> List[AnomalyData]:
        """Get anomalies, optionally filtered by severity"""
        query = db.query(AnomalyData).filter(AnomalyData.is_anomaly == 1)
        if severity:
            query = query.filter(AnomalyData.severity == severity)
        return query.order_by(desc(AnomalyData.timestamp)).all()

    @staticmethod
    def get_reports_by_type(db: Session, report_type: str, limit: int = 20) -> List[ReportData]:
        """Get reports by type"""
        return db.query(ReportData).filter(
            ReportData.report_type == report_type
        ).order_by(desc(ReportData.created_at)).limit(limit).all()

    @staticmethod
    def acknowledge_alert(db: Session, alert_id: int) -> AlertData:
        """Mark alert as acknowledged"""
        alert = db.query(AlertData).filter(AlertData.id == alert_id).first()
        if alert:
            alert.is_active = 0
            alert.acknowledged_at = datetime.utcnow()
            db.commit()
            db.refresh(alert)
            print(f"✓ Alert {alert_id} acknowledged")
        return alert

    @staticmethod
    def get_statistics(db: Session) -> Dict[str, Any]:
        """Get database statistics"""
        user_inputs = db.query(UserInputData).count()
        predictions = db.query(PredictionData).count()
        anomalies = db.query(AnomalyData).filter(AnomalyData.is_anomaly == 1).count()
        alerts = db.query(AlertData).filter(AlertData.is_active == 1).count()
        reports = db.query(ReportData).count()
        
        return {
            "total_user_inputs": user_inputs,
            "total_predictions": predictions,
            "total_anomalies_detected": anomalies,
            "active_alerts": alerts,
            "total_reports": reports,
            "timestamp": datetime.utcnow().isoformat()
        }
