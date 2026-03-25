from fastapi import APIRouter, HTTPException
from models.schemas import EmissionInput, EmissionResponse, SimulatorInput, SimulatorResponse
from models.db_models import SessionLocal
from services.carbon_service import calculate_emissions, simulate_reduction
from services.ml_service import predict_trend_forecast, predict_emissions_with_confidence
from services.pipeline_service import get_industry_benchmark, INDUSTRY_BENCHMARKS
from services.database_service import DatabaseService

router = APIRouter(prefix="/api", tags=["Carbon Calculator"])


@router.post("/calculate", response_model=EmissionResponse)
def calculate(input: EmissionInput):
    """
    Calculate carbon emissions with ML confidence, benchmarks, and cost savings.
    Also stores the input data and results to MySQL database.
    """
    db = SessionLocal()
    try:
        # Calculate emissions
        result = calculate_emissions(
            input.electricity_kwh,
            input.fuel_litres,
            industry_sector=input.industry_sector or "General MSME",
        )
        
        # Store user input to database
        try:
            total_emissions = result.get('total_co2', 0)
            sector = input.industry_sector or "General MSME"
            
            # Store as user input
            user_input_record = DatabaseService.store_user_input(
                db=db,
                sector=sector,
                emissions_value=total_emissions,
                description=f"Electricity: {input.electricity_kwh} kWh, Fuel: {input.fuel_litres} L",
                source="web_dashboard"
            )
            
            # Store the detailed prediction with all calculation results
            DatabaseService.store_prediction(
                db=db,
                prediction_type="dashboard_calculation",
                predicted_value=total_emissions,
                confidence_score=result.get('confidence_score', 0.8),
                prediction_result={
                    "electricity_kwh": input.electricity_kwh,
                    "fuel_litres": input.fuel_litres,
                    "sector": sector,
                    "electricity_co2": result.get('electricity_co2', 0),
                    "fuel_co2": result.get('fuel_co2', 0),
                    "carbon_score": result.get('carbon_score', 'N/A'),
                    "breakdown_percentage": result.get('breakdown_percentage', {}),
                    "industry_benchmark": result.get('industry_benchmark', {}),
                    "cost_savings": result.get('cost_savings', {}),
                }
            )
        except Exception as e:
            print(f"⚠️  Database storage error (non-blocking): {str(e)}")
            # Don't fail the API response if database storage fails
        
        return EmissionResponse(
            success=True,
            data=result,
            message=f"Carbon footprint calculated: {result['total_co2']} kg CO₂"
                    f" | Confidence: {int((result.get('confidence_score', 0.8)) * 100)}%"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/simulate", response_model=SimulatorResponse)
def simulate(input: SimulatorInput):
    """Simulate emission reduction with yearly projections."""
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
def get_history():
    """
    Return historical data for trend charts + ML-powered forecast.
    """
    months = ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan"]
    historical_values = [496, 496, 506, 497, 516, 502]

    mock_data = [
        {"month": "Aug 2024", "electricity_co2": 312, "fuel_co2": 184, "total_co2": 496},
        {"month": "Sep 2024", "electricity_co2": 289, "fuel_co2": 207, "total_co2": 496},
        {"month": "Oct 2024", "electricity_co2": 345, "fuel_co2": 161, "total_co2": 506},
        {"month": "Nov 2024", "electricity_co2": 267, "fuel_co2": 230, "total_co2": 497},
        {"month": "Dec 2024", "electricity_co2": 378, "fuel_co2": 138, "total_co2": 516},
        {"month": "Jan 2025", "electricity_co2": 322, "fuel_co2": 180, "total_co2": 502},
    ]

    forecast_result = predict_trend_forecast(historical_values)

    return {
        "success": True,
        "history": mock_data,
        "forecast": forecast_result.get("forecast", []) if forecast_result else [],
        "model_used": forecast_result.get("model_used", "Mock Data") if forecast_result else "Mock Data",
    }


@router.get("/benchmark/{sector}")
def get_benchmark(sector: str, co2: float = 0):
    """Get industry benchmark for a specific sector."""
    try:
        result = get_industry_benchmark(co2, sector)
        return {"success": True, "benchmark": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sectors")
def list_sectors():
    """List all available industry sectors for benchmarking."""
    return {
        "success": True,
        "sectors": list(INDUSTRY_BENCHMARKS.keys()),
    }


@router.post("/ml-predict")
def ml_predict(payload: dict):
    """
    Direct ML ensemble prediction with confidence score.
    Used by the ML Pipeline status page.
    """
    try:
        electricity_kwh = float(payload.get("electricity_kwh", 0))
        fuel_litres     = float(payload.get("fuel_litres", 0))

        result = predict_emissions_with_confidence(electricity_kwh, fuel_litres)
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/store-input")
def store_user_input(payload: dict):
    """
    Store user input data (electricity, fuel, sector) to MySQL database.
    This is called by the frontend to save form submissions.
    """
    db = SessionLocal()
    try:
        electricity_kwh = float(payload.get("electricity_kwh", 0))
        fuel_litres = float(payload.get("fuel_litres", 0))
        sector = payload.get("sector", "General MSME")
        description = payload.get("description", "User input from dashboard form")
        
        # Calculate total CO2 for storage
        electricity_co2 = electricity_kwh * 0.82  # Typical conversion factor
        fuel_co2 = fuel_litres * 2.3  # Typical conversion factor
        total_co2 = electricity_co2 + fuel_co2
        
        # Store user input
        result = DatabaseService.store_user_input(
            db=db,
            sector=sector,
            emissions_value=total_co2,
            description=description,
            source="web_dashboard_form"
        )
        
        return {
            "success": True,
            "message": f"User input stored successfully (ID: {result.id})",
            "data": {
                "id": result.id,
                "sector": sector,
                "electricity_kwh": electricity_kwh,
                "fuel_litres": fuel_litres,
                "total_co2": round(total_co2, 2),
                "stored_at": result.created_at.isoformat() if hasattr(result, 'created_at') else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing user input: {str(e)}")
    finally:
        db.close()
