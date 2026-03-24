"""
AI Suggestions Service.
Uses trained ML models with fallback to mock suggestions.
Fallback logic:
  - Model 1 (Emissions) fails? → Use mock
  - Model 2 (Scorer) fails? → Use mock calculation
  - Model 3 (Trend) fails? → Use mock trend
"""

import os
from typing import List
from services.ml_service import predict_emissions, predict_carbon_score, predict_trend_forecast

# Mock suggestions library — categorized by emission level
MOCK_SUGGESTIONS = {
    "low": [
        {
            "title": "Switch to LED Lighting",
            "description": "Replace conventional bulbs with LED lights across your facility. LEDs use up to 75% less energy and last 25x longer.",
            "impact": "Reduces electricity consumption by 10-15%",
            "savings_percentage": 12.0,
            "category": "Electricity",
            "priority": "Medium",
        },
        {
            "title": "Install Smart Power Strips",
            "description": "Use smart power strips to eliminate standby power waste from idle office equipment and machinery.",
            "impact": "Saves 5-10% on electricity bills",
            "savings_percentage": 7.0,
            "category": "Electricity",
            "priority": "Low",
        },
        {
            "title": "Optimize Delivery Routes",
            "description": "Use route optimization software to reduce fuel consumption on deliveries by eliminating redundant trips.",
            "impact": "Reduces fuel use by 8-12%",
            "savings_percentage": 10.0,
            "category": "Fuel",
            "priority": "Medium",
        },
    ],
    "medium": [
        {
            "title": "Solar Panel Installation",
            "description": "Install rooftop solar panels to generate clean electricity. A 10kW system can offset 40-60% of your electricity needs.",
            "impact": "Reduces electricity CO₂ by 40-60%",
            "savings_percentage": 45.0,
            "category": "Electricity",
            "priority": "High",
        },
        {
            "title": "Energy Audit",
            "description": "Conduct a professional energy audit to identify major energy waste points. Most audits pay for themselves within 6 months.",
            "impact": "Identifies 15-30% savings opportunities",
            "savings_percentage": 22.0,
            "category": "Electricity",
            "priority": "High",
        },
        {
            "title": "Switch to CNG/Electric Vehicles",
            "description": "Transition your fleet to CNG or electric vehicles. EVs emit zero direct CO₂ and have lower running costs.",
            "impact": "Reduces fuel CO₂ by 50-100%",
            "savings_percentage": 60.0,
            "category": "Fuel",
            "priority": "High",
        },
        {
            "title": "HVAC Optimization",
            "description": "Upgrade to energy-efficient HVAC systems and use smart thermostats to reduce cooling/heating energy by 25%.",
            "impact": "Reduces electricity use by 20-25%",
            "savings_percentage": 22.0,
            "category": "Electricity",
            "priority": "Medium",
        },
    ],
    "high": [
        {
            "title": "Renewable Energy PPA",
            "description": "Sign a Power Purchase Agreement (PPA) with a renewable energy provider to buy 100% green electricity.",
            "impact": "Eliminates electricity CO₂ entirely",
            "savings_percentage": 82.0,
            "category": "Electricity",
            "priority": "Critical",
        },
        {
            "title": "Carbon Offset Program",
            "description": "Partner with verified carbon offset programs (like Gold Standard) to neutralize unavoidable emissions.",
            "impact": "Offsets 100% of remaining emissions",
            "savings_percentage": 100.0,
            "category": "Offsets",
            "priority": "Critical",
        },
        {
            "title": "Process Electrification",
            "description": "Replace fuel-powered industrial processes with electric alternatives powered by renewables.",
            "impact": "Reduces fuel CO₂ by 70-90%",
            "savings_percentage": 80.0,
            "category": "Fuel",
            "priority": "Critical",
        },
        {
            "title": "ISO 14001 Certification",
            "description": "Implement an Environmental Management System (EMS) under ISO 14001 to systematically reduce your footprint.",
            "impact": "Systematic 20-40% reduction over 2 years",
            "savings_percentage": 30.0,
            "category": "Operations",
            "priority": "High",
        },
    ],
}


def get_emission_level(total_co2: float) -> str:
    if total_co2 <= 300:
        return "low"
    elif total_co2 <= 700:
        return "medium"
    else:
        return "high"


def get_mock_suggestions(total_co2: float, electricity_kwh: float, fuel_litres: float) -> dict:
    level = get_emission_level(total_co2)
    suggestions = MOCK_SUGGESTIONS[level]

    # Add universal quick win if electricity is dominant
    if electricity_kwh > fuel_litres * 2:
        quick_win = {
            "title": "Power Factor Correction",
            "description": "Install capacitor banks to improve power factor. This reduces reactive power demand and cuts electricity bills.",
            "impact": "Reduces electricity costs by 5-8%",
            "savings_percentage": 6.0,
            "category": "Electricity",
            "priority": "Low",
        }
        suggestions = suggestions + [quick_win]

    estimated_reduction = max(s["savings_percentage"] for s in suggestions[:3])
    summary = (
        f"Based on your emissions of {total_co2:.1f} kg CO₂, "
        f"we identified {len(suggestions)} actionable strategies. "
        f"Implementing the top recommendations could reduce your footprint by up to {estimated_reduction:.0f}%."
    )

    return {
        "success": True,
        "suggestions": suggestions[:5],  # top 5
        "summary": summary,
        "estimated_reduction": estimated_reduction,
        "model_used": "mock_suggestions",
    }


async def get_ai_suggestions(total_co2: float, electricity_kwh: float, fuel_litres: float, business_type: str) -> dict:
    """
    Get suggestions using ML Model 1 (Emissions Predictor).
    Falls back to mock if model fails.
    """
    try:
        # Try ML model first
        predicted_co2 = predict_emissions(electricity_kwh, fuel_litres)
        
        if predicted_co2 is not None:
            return {
                "success": True,
                "suggestions": get_mock_suggestions(predicted_co2, electricity_kwh, fuel_litres)["suggestions"],
                "summary": f"✨ ML-Powered: Based on your predicted {predicted_co2:.1f} kg CO₂ emissions, here are tailored recommendations.",
                "estimated_reduction": 35.0,
                "model_used": "emissions_model"
            }
    except Exception as e:
        print(f"ML emissions prediction failed: {e}")
    
    # Fallback to mock
    print("Falling back to mock suggestions")
    return get_mock_suggestions(total_co2, electricity_kwh, fuel_litres)

