# Quick Reference: How to Call Services with Database Integration

## Import Required Modules

```python
from models.db_models import SessionLocal
from v2.services.lstm_service import LSTMForecastService
from v2.services.anomaly_service import AnomalyDetectionService
from v2.services.alert_service import AlertSystem
from v2.services.simulation_service import AdvancedSimulationService
from v2.services.advanced_reports_service import ReportGenerator
from v2.services.csv_service import CSVUploadService
from v2.services.chatbot_service import AIConversationService
```

---

## 1. LSTM Forecast Service

### Without Database:
```python
service = LSTMForecastService()
result = service.forecast_lstm(
    historical_data=[100, 120, 110, 130, 125],
    months_ahead=12
)
```

### With Database:
```python
db = SessionLocal()
service = LSTMForecastService()
result = service.forecast_lstm(
    historical_data=[100, 120, 110, 130, 125],
    months_ahead=12,
    db=db  # ← Adds automatic storage
)
db.close()
```

**Stored:** Prediction with 12-month forecast points, confidence intervals, accuracy score

---

## 2. Anomaly Detection Service

### Without Database:
```python
service = AnomalyDetectionService()
result = service.detect_anomalies(
    historical_data=[100, 120, 110, 130, 125, 800],  # 800 is anomaly
    sensitivity="medium"
)
```

### With Database:
```python
db = SessionLocal()
service = AnomalyDetectionService()
result = service.detect_anomalies(
    historical_data=[100, 120, 110, 130, 125, 800],
    sensitivity="medium",
    db=db  # ← Stores anomaly detection results
)
db.close()
```

**Stored:** Each detected anomaly with severity, score, and deviation percentage

---

## 3. Monte Carlo Simulation

### Without Database:
```python
service = AdvancedSimulationService(num_simulations=10000)
result = service.run_monte_carlo(
    historical_data=[100, 120, 110, 130, 125],
    num_months=12,
    volatility_multiplier=1.0,
    trend="auto"
)
```

### With Database:
```python
db = SessionLocal()
service = AdvancedSimulationService(num_simulations=10000)
result = service.run_monte_carlo(
    historical_data=[100, 120, 110, 130, 125],
    num_months=12,
    volatility_multiplier=1.0,
    trend="auto",
    db=db  # ← Stores simulation results
)
db.close()
```

**Stored:** Base case path, best/worst case, summary statistics, risk metrics

---

## 4. Alert System

### Without Database:
```python
alert_system = AlertSystem()
alert = alert_system.check_emissions_alert(
    current_emissions=550,
    period="daily",
    baseline=500
)
```

### With Database:
```python
db = SessionLocal()
alert_system = AlertSystem(db=db)  # ← Pass db to constructor
alert = alert_system.check_emissions_alert(
    current_emissions=550,
    period="daily",
    baseline=500
)
db.close()
```

**Stored:** Alert with type, severity, message, current value, threshold

---

## 5. CSV Import Service

### Without Database:
```python
service = CSVUploadService()
result = service.import_csv_data(
    csv_content="date,emissions\n2024-01-01,150\n2024-01-02,160",
    delimiter=",",
    source_name="Monthly_Report.csv"
)
```

### With Database:
```python
db = SessionLocal()
service = CSVUploadService()
result = service.import_csv_data(
    csv_content="date,emissions\n2024-01-01,150\n2024-01-02,160",
    delimiter=",",
    source_name="Monthly_Report.csv",
    db=db  # ← Logs import and stores emissions as historical data
)
db.close()
```

**Stored:** CSV import log + each emissions value as historical training data

---

## 6. Advanced Reports

### Without Database:
```python
service = ReportGenerator()
report = service.generate_full_report(
    data={
        "total_emissions": 250,
        "baseline": 200,
        "trend": "increasing",
        "historical": [150, 160, 170, 180, 200, 250]
    }
)
```

### With Database:
```python
db = SessionLocal()
service = ReportGenerator()
report = service.generate_full_report(
    data={
        "total_emissions": 250,
        "baseline": 200,
        "trend": "increasing",
        "historical": [150, 160, 170, 180, 200, 250]
    },
    db=db  # ← Stores full report
)
db.close()
```

**Stored:** Complete report (executive summary, analysis, forecast, comparisons)

---

## 7. AI Chatbot Service

### Without Database:
```python
service = AIConversationService()
intent = service.detect_intent("Forecast next month's emissions")
response = service.generate_response(intent=intent)
```

### With Database:
```python
db = SessionLocal()
service = AIConversationService()
intent = service.detect_intent("Forecast next month's emissions")
response = service.generate_response(
    intent=intent,
    db=db  # ← Logs conversation turn
)
db.close()
```

**Stored:** Conversation metadata (intent, entities, confidence, timestamp)

---

## Best Practice: FastAPI Dependency Pattern

### Create a dependency function in main.py:

```python
from fastapi import Depends
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Use in your endpoints:
@app.post("/api/v2/forecast")
async def forecast(data: InputData, db: Session = Depends(get_db)):
    service = LSTMForecastService()
    result = service.forecast_lstm(
        historical_data=data.history,
        db=db  # Automatically injected
    )
    return result

@app.post("/api/v2/detect-anomalies")
async def detect_anomalies(data: InputData, db: Session = Depends(get_db)):
    service = AnomalyDetectionService()
    result = service.detect_anomalies(
        historical_data=data.history,
        db=db
    )
    return result
```

---

## Batch Operations with Database

### Process Multiple Forecasts:
```python
db = SessionLocal()
service = LSTMForecastService()

for month_reduction in [0, 10, 20, 30]:
    result = service.forecast_scenario(
        historical_data=data,
        reduction_pct=month_reduction,
        months_ahead=12,
        db=db  # Each result stored
    )
    print(f"Stored scenario with {month_reduction}% reduction")

db.close()
```

---

## Error Handling

### Database errors are non-blocking:
```python
db = SessionLocal()
service = LSTMForecastService()

try:
    result = service.forecast_lstm(
        historical_data=[100, 120, 110],
        db=db
    )
    # Even if database storage fails, result is returned
    return result
except Exception as e:
    print(f"Forecast failed: {e}")
    db.close()
    raise
```

---

## Retrieve Stored Results

### Query via database service:
```python
from v2.services.database_service import DatabaseService

db = SessionLocal()

# Get recent predictions
predictions = DatabaseService.get_predictions_by_type(db, "lstm", limit=10)
for pred in predictions:
    print(f"Forecast: {pred.predicted_value} (Confidence: {pred.confidence_score})")

# Get active alerts
alerts = DatabaseService.get_active_alerts(db)
for alert in alerts:
    print(f"Alert: {alert.message}")

# Get statistics
stats = DatabaseService.get_statistics(db)
print(stats)

db.close()
```

---

## Key Points

✅ **All parameters optional** - Services work without db parameter
✅ **No performance impact** - Storage happens async, non-blocking
✅ **Automatic persistence** - No manual save needed
✅ **Error safe** - DB errors don't break forecasting
✅ **Historical tracking** - All results stored for replay
✅ **Full audit trail** - All operations timestamped and logged

---

## Typical Workflow

```python
# 1. Get database session
db = SessionLocal()

# 2. Create service instance
forecast_service = LSTMForecastService()

# 3. Call with db parameter
result = forecast_service.forecast_lstm(
    historical_data=user_data,
    db=db
)

# 4. Result automatically stored
# 5. Return to frontend
return result

# 6. Close session
db.close()
```

That's it! The database integration handles the rest automatically. ✅
