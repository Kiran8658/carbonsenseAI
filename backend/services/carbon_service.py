"""
Carbon calculation service.
Emission factors:
  - Electricity: 0.82 kg CO2 per kWh (India grid average)
  - Fuel (diesel): 2.3 kg CO2 per litre
Uses ML Model 2 (Carbon Scorer) with fallback to rule-based scoring.
"""

from services.ml_service import predict_carbon_score

ELECTRICITY_FACTOR = 0.82   # kg CO2 per kWh
FUEL_FACTOR = 2.3            # kg CO2 per litre


def calculate_emissions(electricity_kwh: float, fuel_litres: float) -> dict:
    electricity_co2 = round(electricity_kwh * ELECTRICITY_FACTOR, 2)
    fuel_co2 = round(fuel_litres * FUEL_FACTOR, 2)
    total_co2 = round(electricity_co2 + fuel_co2, 2)

    breakdown_percentage = {}
    if total_co2 > 0:
        breakdown_percentage = {
            "electricity": round((electricity_co2 / total_co2) * 100, 1),
            "fuel": round((fuel_co2 / total_co2) * 100, 1),
        }
    else:
        breakdown_percentage = {"electricity": 0, "fuel": 0}

    score, score_value = get_carbon_score(total_co2)

    return {
        "electricity_co2": electricity_co2,
        "fuel_co2": fuel_co2,
        "total_co2": total_co2,
        "carbon_score": score,
        "carbon_score_value": score_value,
        "breakdown_percentage": breakdown_percentage,
    }


def get_carbon_score(total_co2: float) -> tuple[str, int]:
    """
    Get carbon score using ML Model 2 (Carbon Scorer).
    Falls back to rule-based scoring if model fails.
    Returns (label, score_value 0-100)
    """
    # Try ML model first
    try:
        ml_result = predict_carbon_score(total_co2)
        if ml_result is not None:
            label, score_value = ml_result
            return (label, score_value)
    except Exception as e:
        print(f"ML carbon scoring failed: {e}, using fallback")
    
    # Fallback to rule-based scoring
    if total_co2 <= 100:
        return ("Excellent", 90)
    elif total_co2 <= 300:
        return ("Good", 70)
    elif total_co2 <= 600:
        return ("Average", 50)
    elif total_co2 <= 1000:
        return ("Poor", 30)
    else:
        return ("Critical", 10)


def simulate_reduction(
    electricity_kwh: float,
    fuel_litres: float,
    electricity_reduction_pct: float,
    fuel_reduction_pct: float
) -> dict:
    before = calculate_emissions(electricity_kwh, fuel_litres)

    new_electricity = electricity_kwh * (1 - electricity_reduction_pct / 100)
    new_fuel = fuel_litres * (1 - fuel_reduction_pct / 100)
    after = calculate_emissions(new_electricity, new_fuel)

    savings = round(before["total_co2"] - after["total_co2"], 2)
    savings_pct = round((savings / before["total_co2"] * 100) if before["total_co2"] > 0 else 0, 1)

    return {
        "before_co2": before["total_co2"],
        "after_co2": after["total_co2"],
        "savings_co2": savings,
        "savings_percentage": savings_pct,
        "electricity_before": before["electricity_co2"],
        "electricity_after": after["electricity_co2"],
        "fuel_before": before["fuel_co2"],
        "fuel_after": after["fuel_co2"],
    }

