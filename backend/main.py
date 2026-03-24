from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import calculator, suggestions, reports
from services.ml_service import initialize_models, get_model_status
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CarbonSense AI API",
    description="AI-powered carbon footprint tracker for MSMEs",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML models on startup
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting CarbonSense API...")
    initialize_models()
    logger.info("✅ CarbonSense API started successfully!")

app.include_router(calculator.router)
app.include_router(suggestions.router)
app.include_router(reports.router)

@app.get("/")
def root():
    return {
        "message": "CarbonSense AI API is running",
        "version": "1.0.0",
        "features": ["ML-powered emissions prediction", "AI suggestions", "Carbon scoring", "Trend forecasting", "PDF report generation"]
    }

@app.get("/health")
def health():
    model_status = get_model_status()
    return {
        "status": "healthy",
        "models": model_status,
        "details": {
            "emissions_predictor": {
                "name": "AI Model #1: Emissions Predictor",
                "type": "RandomForest Regressor",
                "status": "connected" if model_status.get("emissions_model", "").startswith("✅") else "disconnected",
                "description": "Predicts CO₂ emissions from electricity & fuel consumption"
            },
            "carbon_scorer": {
                "name": "AI Model #2: Carbon Scorer",
                "type": "Smart Scoring Algorithm",
                "status": "connected" if model_status.get("scorer_model", "").startswith("✅") else "disconnected",
                "description": "Evaluates business emissions against MSME benchmarks"
            },
            "trend_forecaster": {
                "name": "AI Model #3: Trend Forecaster",
                "type": model_status.get("trend_model", "XGBoost").replace("✅", "").strip() if "✅" in model_status.get("trend_model", "") else "XGBoost/LSTM",
                "status": "connected" if model_status.get("trend_model", "").startswith("✅") else "disconnected",
                "description": "Forecasts future emission trends using time-series analysis"
            }
        }
    }

