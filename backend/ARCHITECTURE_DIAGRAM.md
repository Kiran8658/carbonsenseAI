# CarbonSense ML Integration - Architecture Diagram

## System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      CARBONSENSE API                            │
│                    (FastAPI Backend)                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────────────┐
                    │ Initialize on   │
                    │ Startup (main.py)
                    └─────────────────┘
                              ↓
                    ┌─────────────────────────────┐
                    │  Load 3 ML Models           │
                    │  (ml_service.py)            │
                    └─────────────────────────────┘
                         ↙    ↓    ↘
              ✅ Model 1   ✅ Model 2   ✅ Model 3


═══════════════════════════════════════════════════════════════════

REQUEST FLOWS:

1️⃣  POST /api/calculate
    ├─ Input: electricity_kwh, fuel_litres
    ├─ Carbon Calculation (carbon_service.py)
    │  ├─ electricity_co2 = kwh * 0.82
    │  ├─ fuel_co2 = litres * 2.3
    │  ├─ total_co2 = electricity_co2 + fuel_co2
    │  └─ carbon_score = get_carbon_score(total_co2)
    │     ├─ Try: ML Model 2 (predict_carbon_score)
    │     │  └─ Success? ✅ Return ML result
    │     └─ Fail? → Fallback rule-based scoring
    │        └─ (≤100=Excellent, ≤300=Good, etc)
    └─ Response: {electricity_co2, fuel_co2, total_co2, carbon_score, carbon_score_value}


2️⃣  POST /api/ai-suggestions  
    ├─ Input: electricity_kwh, fuel_litres, total_co2, business_type
    ├─ AI Service (ai_service.py)
    │  ├─ Try: ML Model 1 (predict_emissions)
    │  │  └─ Success? ✅ Return ML-powered suggestions
    │  └─ Fail? → get_mock_suggestions()
    │     └─ Uses pre-defined suggestion library
    └─ Response: {suggestions[], summary, estimated_reduction, model_used}


3️⃣  GET /api/history
    ├─ Historical Data (calculator.py)
    │  ├─ Load mock 6-month history
    │  ├─ Try: ML Model 3 (predict_trend_forecast)
    │  │  └─ Success? ✅ Return ML forecast for next 6 months
    │  └─ Fail? → Use mock trend data
    └─ Response: {history[], forecast[], model_used}


═══════════════════════════════════════════════════════════════════

FALLBACK ARCHITECTURE:

Model 1 (Emissions Predictor)
    ↓
Try ML Prediction
    ├─ Success ✅ → Use ML result
    └─ Fail ❌ → Fallback to Mock Suggestions
                └─ Always returns 5 tailored suggestions

Model 2 (Carbon Scorer)
    ↓
Try ML Classification
    ├─ Success ✅ → Use ML result (Label + Score)
    └─ Fail ❌ → Fallback to Rule-Based Scoring
                └─ Always returns score (0-100)

Model 3 (Trend Forecaster)
    ↓
Try ML Time-Series Prediction
    ├─ Success ✅ → Use ML forecast
    └─ Fail ❌ → Fallback to Mock Historical Data
                └─ Always returns 6-month mock data


═══════════════════════════════════════════════════════════════════

ERROR HANDLING:

┌─────────────────────────────────────────────────────────────────┐
│                    INDEPENDENT FALLBACKS                        │
│                                                                  │
│  ✅ Model 1 Fails → Model 2 & 3 UNAFFECTED                     │
│  ✅ Model 2 Fails → Model 1 & 3 UNAFFECTED                     │
│  ✅ Model 3 Fails → Model 1 & 2 UNAFFECTED                     │
│  ✅ All Fail → Each uses own fallback (no cascade)             │
│                                                                  │
│  🎯 App NEVER crashes - always has working response            │
└─────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════

FILES STRUCTURE:

backend/
├── main.py                           (Modified: +model init)
├── requirements.txt                  (Modified: +sklearn, joblib)
├── test_models.py                    (NEW: Test integration)
├── ML_INTEGRATION_GUIDE.md           (NEW: This guide)
│
├── services/
│   ├── ml_service.py                 (NEW: Model loading)
│   ├── ai_service.py                 (Modified: +ML Model 1)
│   └── carbon_service.py              (Modified: +ML Model 2)
│
├── routes/
│   ├── calculator.py                 (Modified: +ML Model 3)
│   └── suggestions.py                (Unchanged)
│
├── models/
│   └── schemas.py                    (Unchanged)
│
├── emissions_model.pkl               (Your trained model)
├── carbon_scorer_model.pkl           (Your trained model)
└── trend_forecaster_model.pkl        (Your trained model)


═══════════════════════════════════════════════════════════════════

LOGGING OUTPUT:

On Startup:
    🚀 Starting CarbonSense API...
    ✅ Loaded Emissions Model
    ✅ Loaded Carbon Scorer Model
    ✅ Loaded Trend Forecaster Model
    ✅ CarbonSense API started successfully!

On Success (Model works):
    ✅ Emissions prediction: 640.00 kg CO2

On Fallback (Model fails):
    ❌ Emissions prediction failed: [error]
    Using fallback to mock suggestions

Health Check:
    {
      "status": "healthy",
      "models": {
        "emissions_model": "✅ Loaded",
        "scorer_model": "✅ Loaded",
        "trend_model": "✅ Loaded"
      }
    }


═══════════════════════════════════════════════════════════════════

TESTING CHECKLIST:

✅ Model files exist (3 .pkl files)
✅ Models load without errors
✅ Each endpoint callable
✅ Fallback works when model removed
✅ All models fail scenario handled
✅ API responds even with all failures


═══════════════════════════════════════════════════════════════════
```

## Ready for Features! 🚀

Tell me what features you want to add and I'll integrate them smoothly with the ML models.
