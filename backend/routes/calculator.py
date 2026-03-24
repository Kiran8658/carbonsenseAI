from fastapi import APIRouter, HTTPException
from models.schemas import EmissionInput, EmissionResponse, SimulatorInput, SimulatorResponse
from services.carbon_service import calculate_emissions, simulate_reduction
from services.ml_service import predict_trend_forecast

router = APIRouter(prefix="/api", tags=["Carbon Calculator"])


@router.post("/calculate", response_model=EmissionResponse)
def calculate(input: EmissionInput):
    """Calculate carbon emissions from electricity and fuel usage."""
    try:
        result = calculate_emissions(input.electricity_kwh, input.fuel_litres)
        return EmissionResponse(
            success=True,
            data=result,
            message=f"Carbon footprint calculated: {result['total_co2']} kg CO₂"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate", response_model=SimulatorResponse)
def simulate(input: SimulatorInput):
    """Simulate emission reduction based on percentage cuts."""
    try:
        result = simulate_reduction(
            input.electricity_kwh,
            input.fuel_litres,
            input.electricity_reduction_pct,
            input.fuel_reduction_pct,
        )
        return SimulatorResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
def get_mock_history():
    """
    Return historical data for trend charts.
    Uses ML Model 3 (Trend Forecaster) if available, falls back to mock.
    """
    # Mock historical data (past 6 months)
    months = ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan"]
    historical_values = [496, 496, 506, 497, 516, 0]
    
    mock_data = [
        {"month": "Aug 2024", "electricity_co2": 312, "fuel_co2": 184, "total_co2": 496},
        {"month": "Sep 2024", "electricity_co2": 289, "fuel_co2": 207, "total_co2": 496},
        {"month": "Oct 2024", "electricity_co2": 345, "fuel_co2": 161, "total_co2": 506},
        {"month": "Nov 2024", "electricity_co2": 267, "fuel_co2": 230, "total_co2": 497},
        {"month": "Dec 2024", "electricity_co2": 378, "fuel_co2": 138, "total_co2": 516},
        {"month": "Jan 2025", "electricity_co2": 0,   "fuel_co2": 0,   "total_co2": 0},
    ]
    
    # Try ML model for forecast
    forecast_result = predict_trend_forecast(historical_values[:-1])  # Exclude last month
    
    if forecast_result:
        response_data = {
            "success": True,
            "history": mock_data,
            "forecast": forecast_result.get("forecast", []),
            "model_used": "ML Trend Forecaster"
        }
    else:
        response_data = {
            "success": True,
            "history": mock_data,
            "model_used": "Mock Data (Fallback)"
        }
    
    return response_data

