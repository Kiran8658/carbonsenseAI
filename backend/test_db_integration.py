"""
Test and Demo Script for Database Integration
Shows how to store and retrieve data from MySQL
"""

from sqlalchemy.orm import Session
from models.db_models import SessionLocal
from services.database_service import DatabaseService
from datetime import datetime, timedelta
import json


def demo_full_workflow():
    """Demonstrate complete data flow: input → prediction → storage"""
    print("\n" + "="*70)
    print("CarbonSense Database Integration Demo")
    print("="*70 + "\n")
    
    db = SessionLocal()
    
    try:
        # 1. Store User Input Data
        print("1️⃣  Storing user input data...")
        user_input = DatabaseService.store_user_input(
            db=db,
            sector="Energy",
            emissions_value=250.5,
            description="Monthly emissions from power plant",
            source="web form"
        )
        
        # 2. Store Historical Data
        print("\n2️⃣  Storing historical training data...")
        dates = [datetime.utcnow() - timedelta(days=i) for i in range(10, 0, -1)]
        values = [200 + i*10 for i in range(10)]
        DatabaseService.store_historical_data(
            db=db,
            timestamps=dates,
            values=values,
            sector="Energy",
            data_source="csv",
            is_training=True
        )
        
        # 3. Store Prediction (e.g., from LSTM)
        print("\n3️⃣  Storing LSTM prediction...")
        lstm_prediction = DatabaseService.store_prediction(
            db=db,
            prediction_type="lstm",
            predicted_value=290.3,
            input_id=user_input.id,
            confidence_score=0.94,
            confidence_interval_low=270.0,
            confidence_interval_high=310.0,
            model_version="lstm-v1.0"
        )
        
        # 4. Store Anomaly Detection Result
        print("\n4️⃣  Storing anomaly detection...")
        anomaly = DatabaseService.store_anomaly(
            db=db,
            is_anomaly=False,
            anomaly_score=0.15,
            severity="LOW",
            deviation_percent=5.2,
            detection_method="isolation_forest",
            input_id=user_input.id
        )
        
        # 5. Store Alert (if threshold exceeded)
        print("\n5️⃣  Storing alert...")
        alert = DatabaseService.store_alert(
            db=db,
            alert_type="threshold_exceeded",
            severity="HIGH",
            current_value=250.5,
            message="Energy emissions exceeded weekly threshold",
            threshold_value=200.0
        )
        
        # 6. Store Report
        print("\n6️⃣  Storing advanced report...")
        report = DatabaseService.store_report(
            db=db,
            report_type="executive",
            report_content={
                "total_emissions": 250.5,
                "variance": -5.2,
                "status": "excellent",
                "trend": "decreasing"
            },
            data_period_start=datetime.utcnow() - timedelta(days=30),
            data_period_end=datetime.utcnow(),
            total_emissions=250.5,
            summary="Energy season showing excellent performance"
        )
        
        # 7. Get Database Statistics
        print("\n7️⃣  Database Statistics:")
        stats = DatabaseService.get_statistics(db)
        print(json.dumps(stats, indent=2, default=str))
        
        # 8. Retrieve Data
        print("\n8️⃣  Retrieving stored data...")
        
        print("\n📊 Recent User Inputs:")
        inputs = DatabaseService.get_user_inputs(db, limit=5)
        for inp in inputs:
            print(f"   - {inp.sector}: {inp.emissions_value} kg CO2 (ID: {inp.id})")
        
        print("\n📊 Recent Predictions:")
        predictions = DatabaseService.get_predictions_by_type(db, "lstm", limit=5)
        for pred in predictions:
            print(f"   - {pred.prediction_type}: {pred.predicted_value} kg CO2 (Confidence: {pred.confidence_score})")
        
        print("\n📊 Detected Anomalies:")
        anomalies = DatabaseService.get_anomalies(db)
        if anomalies:
            for anom in anomalies[:3]:
                print(f"   - Severity: {anom.severity}, Score: {anom.anomaly_score}")
        else:
            print("   - No anomalies detected")
        
        print("\n📊 Active Alerts:")
        alerts = DatabaseService.get_active_alerts(db)
        for alert in alerts[:3]:
            print(f"   - {alert.alert_type} ({alert.severity}): {alert.message}")
        
        print("\n✅ Demo completed successfully!")
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    demo_full_workflow()
