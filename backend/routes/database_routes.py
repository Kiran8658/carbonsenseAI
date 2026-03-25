"""
Database Integration with API Routes
Add these routes to your FastAPI main.py to use database storage
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from models.db_models import get_db
from services.database_service import DatabaseService

router = APIRouter(prefix="/api/v2/db", tags=["database"])


# Store Endpoints

@router.post("/store/user-input")
def store_user_input(
    sector: str,
    emissions_value: float,
    description: str = None,
    db: Session = Depends(get_db)
):
    """Store user-entered emissions data"""
    result = DatabaseService.store_user_input(
        db=db,
        sector=sector,
        emissions_value=emissions_value,
        description=description,
        source="api"
    )
    return {
        "success": True,
        "id": result.id,
        "message": f"Stored {sector} emission of {emissions_value} kg CO2"
    }


@router.post("/store/prediction")
def store_prediction_route(
    prediction_type: str,
    predicted_value: float,
    confidence_score: float = None,
    input_id: int = None,
    confidence_interval_low: float = None,
    confidence_interval_high: float = None,
    db: Session = Depends(get_db)
):
    """Store prediction result"""
    result = DatabaseService.store_prediction(
        db=db,
        prediction_type=prediction_type,
        predicted_value=predicted_value,
        input_id=input_id,
        confidence_score=confidence_score,
        confidence_interval_low=confidence_interval_low,
        confidence_interval_high=confidence_interval_high
    )
    return {
        "success": True,
        "id": result.id,
        "message": f"Stored {prediction_type} prediction"
    }


@router.post("/store/anomaly")
def store_anomaly_route(
    is_anomaly: bool,
    anomaly_score: float,
    severity: str,
    deviation_percent: float,
    detection_method: str,
    input_id: int = None,
    db: Session = Depends(get_db)
):
    """Store anomaly detection result"""
    result = DatabaseService.store_anomaly(
        db=db,
        is_anomaly=is_anomaly,
        anomaly_score=anomaly_score,
        severity=severity,
        deviation_percent=deviation_percent,
        detection_method=detection_method,
        input_id=input_id
    )
    return {
        "success": True,
        "id": result.id,
        "is_anomaly": is_anomaly,
        "severity": severity
    }


@router.post("/store/alert")
def store_alert_route(
    alert_type: str,
    severity: str,
    current_value: float,
    message: str,
    threshold_value: float = None,
    db: Session = Depends(get_db)
):
    """Store alert"""
    result = DatabaseService.store_alert(
        db=db,
        alert_type=alert_type,
        severity=severity,
        current_value=current_value,
        message=message,
        threshold_value=threshold_value
    )
    return {
        "success": True,
        "id": result.id,
        "alert_type": alert_type,
        "severity": severity
    }


# Retrieve Endpoints

@router.get("/user-inputs")
def get_user_inputs(limit: int = 100, db: Session = Depends(get_db)):
    """Get recent user inputs"""
    data = DatabaseService.get_user_inputs(db, limit=limit)
    return {
        "count": len(data),
        "data": [
            {
                "id": d.id,
                "timestamp": d.timestamp.isoformat() if d.timestamp else None,
                "sector": d.sector,
                "emissions_value": d.emissions_value,
                "source": d.source
            }
            for d in data
        ]
    }


@router.get("/predictions/{prediction_type}")
def get_predictions(prediction_type: str, limit: int = 50, db: Session = Depends(get_db)):
    """Get predictions by type"""
    data = DatabaseService.get_predictions_by_type(db, prediction_type, limit=limit)
    return {
        "prediction_type": prediction_type,
        "count": len(data),
        "data": [
            {
                "id": d.id,
                "predicted_value": d.predicted_value,
                "confidence_score": d.confidence_score,
                "timestamp": d.timestamp.isoformat() if d.timestamp else None
            }
            for d in data
        ]
    }


@router.get("/anomalies")
def get_anomalies(severity: str = None, db: Session = Depends(get_db)):
    """Get detected anomalies"""
    data = DatabaseService.get_anomalies(db, severity=severity)
    return {
        "count": len(data),
        "data": [
            {
                "id": d.id,
                "is_anomaly": d.is_anomaly,
                "severity": d.severity,
                "anomaly_score": d.anomaly_score,
                "timestamp": d.timestamp.isoformat() if d.timestamp else None
            }
            for d in data
        ]
    }


@router.get("/alerts")
def get_active_alerts(db: Session = Depends(get_db)):
    """Get active alerts"""
    data = DatabaseService.get_active_alerts(db)
    return {
        "count": len(data),
        "data": [
            {
                "id": d.id,
                "alert_type": d.alert_type,
                "severity": d.severity,
                "message": d.message,
                "created_at": d.created_at.isoformat() if d.created_at else None
            }
            for d in data
        ]
    }


@router.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    """Acknowledge an alert"""
    result = DatabaseService.acknowledge_alert(db, alert_id)
    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {
        "success": True,
        "message": f"Alert {alert_id} acknowledged"
    }


@router.get("/statistics")
def get_statistics(db: Session = Depends(get_db)):
    """Get database statistics"""
    stats = DatabaseService.get_statistics(db)
    return stats
