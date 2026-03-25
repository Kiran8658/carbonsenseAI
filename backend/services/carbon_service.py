"""
Carbon Calculation Service — upgraded with pipeline integration.
Includes:
  - ML scoring with fallback
  - Industry benchmarking
  - Cost savings estimation
  - Confidence scores
  - Yearly simulation impact
"""

from services.ml_service import predict_carbon_score
from services.pipeline_service import (
    validate_inputs,
    get_industry_benchmark,
    estimate_cost_savings,
    compute_confidence_score,
    compute_yearly_impact,
    ELECTRICITY_FACTOR,
    FUEL_FACTOR_DIESEL,
)
from typing import Optional

_model_loaded_flag = {"emissions": False, "scorer": False}


def set_model_flags(emissions: bool, scorer: bool):
    """Called by ml_service on startup to inform pipeline of model status."""
    _model_loaded_flag["emissions"] = emissions
    _model_loaded_flag["scorer"] = scorer


def calculate_emissions(
    electricity_kwh: float,
    fuel_litres: float,
    industry_sector: str = "General MSME",
    include_benchmark: bool = True,
) -> dict:
    # ── 1. Validate inputs ────────────────────────────────────────────
    validated = validate_inputs(electricity_kwh, fuel_litres)
    elec = validated["cleaned_electricity"]
    fuel = validated["cleaned_fuel"]
    flags = validated["flags"]

    # ── 2. Core emission calculation ──────────────────────────────────
    electricity_co2 = round(elec * ELECTRICITY_FACTOR, 2)
    fuel_co2        = round(fuel * FUEL_FACTOR_DIESEL, 2)
    total_co2       = round(electricity_co2 + fuel_co2, 2)

    breakdown_percentage = {}
    if total_co2 > 0:
        breakdown_percentage = {
            "electricity": round((electricity_co2 / total_co2) * 100, 1),
            "fuel":        round((fuel_co2        / total_co2) * 100, 1),
        }
    else:
        breakdown_percentage = {"electricity": 0, "fuel": 0}

    # ── 3. ML carbon score (with fallback) ────────────────────────────
    score, score_value, model_used = get_carbon_score(total_co2)

    # ── 4. Confidence score ───────────────────────────────────────────
    confidence, pred_range = compute_confidence_score(
        elec, fuel,
        model_loaded=_model_loaded_flag["scorer"],
        flags=flags,
    )

    # ── 5. Industry benchmark ─────────────────────────────────────────
    benchmark = get_industry_benchmark(total_co2, industry_sector) if include_benchmark else None

    # ── 6. Cost savings (assume 20% efficiency gain) ──────────────────
    cost_info = estimate_cost_savings(elec, fuel, efficiency_gain_pct=20.0)

    return {
        "electricity_co2":     electricity_co2,
        "fuel_co2":            fuel_co2,
        "total_co2":           total_co2,
        "carbon_score":        score,
        "carbon_score_value":  score_value,
        "breakdown_percentage": breakdown_percentage,
        "confidence_score":    confidence,
        "prediction_range":    pred_range,
        "industry_benchmark":  benchmark,
        "cost_savings":        cost_info,
        "ml_model_used":       model_used,
        "data_quality_flags":  flags,
    }


def get_carbon_score(total_co2: float):
    """
    ML carbon scoring with graceful fallback.
    Returns (label, score_value, model_name)
    """
    try:
        ml_result = predict_carbon_score(total_co2)
        if ml_result is not None:
            label, score_value = ml_result
            return (label, score_value, "ML Carbon Scorer")
    except Exception as e:
        print(f"ML carbon scoring failed: {e}, using rule-based fallback")

    # Rule-based fallback
    if total_co2 <= 100:
        return ("Excellent", 92, "Rule-based")
    elif total_co2 <= 300:
        return ("Good", 75, "Rule-based")
    elif total_co2 <= 600:
        return ("Average", 55, "Rule-based")
    elif total_co2 <= 1000:
        return ("Poor", 32, "Rule-based")
    else:
        return ("Critical", 12, "Rule-based")


def simulate_reduction(
    electricity_kwh: float,
    fuel_litres: float,
    electricity_reduction_pct: float,
    fuel_reduction_pct: float,
    industry_sector: str = "General MSME",
) -> dict:
    before = calculate_emissions(electricity_kwh, fuel_litres, industry_sector, include_benchmark=False)

    new_electricity = electricity_kwh * (1 - electricity_reduction_pct / 100)
    new_fuel        = fuel_litres        * (1 - fuel_reduction_pct        / 100)
    after = calculate_emissions(new_electricity, new_fuel, industry_sector, include_benchmark=False)

    savings     = round(before["total_co2"] - after["total_co2"], 2)
    savings_pct = round((savings / before["total_co2"] * 100) if before["total_co2"] > 0 else 0, 1)

    # Monthly cost savings
    before_cost = before["cost_savings"]["current_monthly_cost_inr"]
    after_cost_info = estimate_cost_savings(new_electricity, new_fuel, efficiency_gain_pct=0)
    monthly_cost_savings = round(before_cost - after_cost_info["current_monthly_cost_inr"], 2)

    # Yearly impact
    yearly = compute_yearly_impact(savings, monthly_cost_savings)

    return {
        "before_co2":          before["total_co2"],
        "after_co2":           after["total_co2"],
        "savings_co2":         savings,
        "savings_percentage":  savings_pct,
        "electricity_before":  before["electricity_co2"],
        "electricity_after":   after["electricity_co2"],
        "fuel_before":         before["fuel_co2"],
        "fuel_after":          after["fuel_co2"],
        # New
        "yearly_co2_savings":       yearly["yearly_co2_savings"],
        "yearly_cost_savings_inr":  yearly["yearly_cost_savings_inr"],
        "trees_equivalent":         yearly["trees_equivalent"],
        "homes_powered_equivalent": yearly["homes_powered_equivalent"],
    }
