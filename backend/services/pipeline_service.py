"""
ML Data Pipeline Service
========================
Handles the full data engineering pipeline:
- Input validation & sanity checks
- Missing value handling
- Outlier detection (IQR + Z-score)
- Feature engineering (rolling averages, seasonality, trends)
- Industry benchmarking
- Cost estimation
"""

import logging
import math
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

import numpy as np

logger = logging.getLogger(__name__)

# ─── Emission Factors ────────────────────────────────────────────────
ELECTRICITY_FACTOR = 0.82   # kg CO₂/kWh  (India grid avg, CEA 2023)
FUEL_FACTOR_DIESEL = 2.3    # kg CO₂/litre (IPCC/MoEFCC)
FUEL_FACTOR_PETROL = 2.31   # kg CO₂/litre

# ─── Cost Factors (INR) ──────────────────────────────────────────────
ELECTRICITY_RATE_INR = 8.5      # ₹/kWh (industrial avg)
DIESEL_RATE_INR = 96.0          # ₹/litre (2025 avg)

# ─── Industry Benchmarks (avg monthly CO₂ in kg for MSMEs) ──────────
INDUSTRY_BENCHMARKS: Dict[str, Dict[str, float]] = {
    "Manufacturing":      {"avg": 1200, "p25": 600,  "p75": 1800},
    "Retail":             {"avg": 400,  "p25": 200,  "p75": 700},
    "Food & Beverage":    {"avg": 800,  "p25": 400,  "p75": 1400},
    "Textile":            {"avg": 950,  "p25": 500,  "p75": 1500},
    "Construction":       {"avg": 1500, "p25": 800,  "p75": 2500},
    "IT & Services":      {"avg": 200,  "p25": 80,   "p75": 350},
    "Healthcare":         {"avg": 600,  "p25": 300,  "p75": 1000},
    "Hospitality":        {"avg": 900,  "p25": 450,  "p75": 1600},
    "Transportation":     {"avg": 2000, "p25": 900,  "p75": 3500},
    "Agriculture":        {"avg": 550,  "p25": 250,  "p75": 900},
    "General MSME":       {"avg": 700,  "p25": 300,  "p75": 1200},
}

# ─── Sanity Bounds ────────────────────────────────────────────────────
MAX_ELECTRICITY_KWH = 100_000   # 100 MWh/month — unrealistic above this
MAX_FUEL_LITRES = 50_000        # 50 kL/month
MIN_NONZERO = 0.1


# ══════════════════════════════════════════════════════════════════════
# 1. Input Validation
# ══════════════════════════════════════════════════════════════════════

def validate_inputs(electricity_kwh: float, fuel_litres: float) -> Dict[str, Any]:
    """
    Validate inputs and return flags + cleaned values.
    Returns: {cleaned_electricity, cleaned_fuel, flags: List[str], is_valid: bool}
    """
    flags: List[str] = []
    elec = electricity_kwh
    fuel = fuel_litres

    # Negative check (Pydantic ge=0 already handles, but belt-and-suspenders)
    if elec < 0:
        flags.append("⚠️ Negative electricity — clamped to 0")
        elec = 0.0
    if fuel < 0:
        flags.append("⚠️ Negative fuel — clamped to 0")
        fuel = 0.0

    # Missing / zero handling
    if elec == 0 and fuel == 0:
        flags.append("⚠️ Both inputs are zero — no meaningful output possible")

    # Outlier / sanity checks
    if elec > MAX_ELECTRICITY_KWH:
        flags.append(f"⚠️ Electricity ({elec:.0f} kWh) is unusually high for an MSME")
    if fuel > MAX_FUEL_LITRES:
        flags.append(f"⚠️ Fuel ({fuel:.0f} L) is unusually high for an MSME")

    # Ratio sanity
    if elec > 0 and fuel > 0:
        ratio = elec / (fuel + 1e-9)
        if ratio > 500:
            flags.append("ℹ️ Very high electricity-to-fuel ratio — electricity-heavy business detected")
        elif ratio < 0.02:
            flags.append("ℹ️ Very low electricity-to-fuel ratio — fuel-heavy business detected")

    is_valid = elec >= 0 and fuel >= 0 and (elec + fuel) > 0

    return {
        "cleaned_electricity": max(0.0, elec),
        "cleaned_fuel": max(0.0, fuel),
        "flags": flags,
        "is_valid": is_valid,
    }


# ══════════════════════════════════════════════════════════════════════
# 2. Feature Engineering
# ══════════════════════════════════════════════════════════════════════

def engineer_features(historical_data: List[Dict]) -> Dict[str, Any]:
    """
    Extract ML-friendly features from historical monthly data.
    Expected each record: {total_co2, electricity_co2, fuel_co2}
    """
    if not historical_data:
        return {}

    totals = [h.get("total_co2", 0) for h in historical_data]
    elec   = [h.get("electricity_co2", 0) for h in historical_data]
    fuel   = [h.get("fuel_co2", 0) for h in historical_data]

    n = len(totals)
    features: Dict[str, Any] = {}

    # ── Rolling averages ──────────────────────────────────────────────
    if n >= 3:
        features["rolling_avg_3m"] = float(np.mean(totals[-3:]))
    if n >= 6:
        features["rolling_avg_6m"] = float(np.mean(totals[-6:]))

    # ── Trend (linear slope) ─────────────────────────────────────────
    if n >= 2:
        x = np.arange(n)
        slope = float(np.polyfit(x, totals, 1)[0])
        features["trend_slope"] = slope
        features["trend_direction"] = "increasing" if slope > 2 else "decreasing" if slope < -2 else "stable"

    # ── Seasonality detection (peak month) ───────────────────────────
    if n >= 6:
        peak_idx = int(np.argmax(totals))
        features["peak_month_idx"] = peak_idx
        features["seasonality_amplitude"] = float(max(totals) - min(totals))
        features["seasonality_ratio"] = float(
            (max(totals) - min(totals)) / (np.mean(totals) + 1e-9)
        )

    # ── Volatility ───────────────────────────────────────────────────
    if n >= 2:
        features["volatility_std"] = float(np.std(totals))
        features["volatility_cv"] = float(np.std(totals) / (np.mean(totals) + 1e-9))

    # ── Source mix ───────────────────────────────────────────────────
    avg_total = np.mean(totals) or 1
    features["avg_elec_share"] = float(np.mean(elec) / avg_total)
    features["avg_fuel_share"] = float(np.mean(fuel) / avg_total)

    # ── Recent vs. historical comparison ─────────────────────────────
    if n >= 4:
        recent = np.mean(totals[-2:])
        historical = np.mean(totals[:-2])
        features["recent_vs_historical_pct"] = float(
            (recent - historical) / (historical + 1e-9) * 100
        )

    return features


# ══════════════════════════════════════════════════════════════════════
# 3. Outlier Detection
# ══════════════════════════════════════════════════════════════════════

def detect_outliers(values: List[float]) -> Dict[str, Any]:
    """IQR + Z-score outlier detection."""
    if len(values) < 4:
        return {"outlier_indices": [], "method": "insufficient_data"}

    arr = np.array(values)
    q1, q3 = float(np.percentile(arr, 25)), float(np.percentile(arr, 75))
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr

    iqr_outliers = [i for i, v in enumerate(values) if v < lower or v > upper]

    mean, std = float(np.mean(arr)), float(np.std(arr))
    z_outliers = [
        i for i, v in enumerate(values) if std > 0 and abs((v - mean) / std) > 2.5
    ]

    outliers = list(set(iqr_outliers + z_outliers))

    return {
        "outlier_indices": outliers,
        "iqr_bounds": {"lower": round(lower, 2), "upper": round(upper, 2)},
        "z_score_threshold": 2.5,
        "method": "IQR + Z-score",
        "has_outliers": len(outliers) > 0,
    }


# ══════════════════════════════════════════════════════════════════════
# 4. Industry Benchmarking
# ══════════════════════════════════════════════════════════════════════

def get_industry_benchmark(total_co2: float, sector: str = "General MSME") -> Dict[str, Any]:
    """Compare user emissions against industry benchmark."""
    bench = INDUSTRY_BENCHMARKS.get(sector, INDUSTRY_BENCHMARKS["General MSME"])
    avg   = bench["avg"]
    p25   = bench["p25"]
    p75   = bench["p75"]

    # Rough percentile estimate (linear interpolation in 3-bucket model)
    if total_co2 <= p25:
        percentile = (total_co2 / p25) * 25
    elif total_co2 <= avg:
        percentile = 25 + ((total_co2 - p25) / (avg - p25 + 1e-9)) * 25
    elif total_co2 <= p75:
        percentile = 50 + ((total_co2 - avg) / (p75 - avg + 1e-9)) * 25
    else:
        percentile = min(99, 75 + ((total_co2 - p75) / (p75 + 1e-9)) * 24)

    is_above_avg = total_co2 > avg
    reduction_needed = max(0, total_co2 - avg)

    return {
        "sector": sector,
        "avg_monthly_co2": avg,
        "your_co2": round(total_co2, 1),
        "percentile": round(percentile, 1),
        "is_above_average": is_above_avg,
        "reduction_to_average": round(reduction_needed, 1),
        "p25_benchmark": p25,
        "p75_benchmark": p75,
        "rating": (
            "Top 25% — Excellent!" if percentile <= 25 else
            "Below Average — Good" if percentile <= 50 else
            "Above Average — Needs Improvement" if percentile <= 75 else
            "High Emitter — Urgent Action"
        ),
    }


# ══════════════════════════════════════════════════════════════════════
# 5. Cost Savings Estimation
# ══════════════════════════════════════════════════════════════════════

def estimate_cost_savings(
    electricity_kwh: float,
    fuel_litres: float,
    efficiency_gain_pct: float = 20.0,
) -> Dict[str, Any]:
    """
    Estimate INR cost savings at a given efficiency gain percentage.
    """
    elec_cost   = electricity_kwh * ELECTRICITY_RATE_INR
    fuel_cost   = fuel_litres * DIESEL_RATE_INR
    total_cost  = elec_cost + fuel_cost

    savings_factor = efficiency_gain_pct / 100.0
    monthly_savings = total_cost * savings_factor
    annual_savings  = monthly_savings * 12

    return {
        "current_monthly_cost_inr": round(total_cost, 2),
        "electricity_cost_inr":     round(elec_cost, 2),
        "fuel_cost_inr":            round(fuel_cost, 2),
        "potential_monthly_savings_inr": round(monthly_savings, 2),
        "annual_savings_inr":       round(annual_savings, 2),
        "savings_from_efficiency_pct": efficiency_gain_pct,
    }


# ══════════════════════════════════════════════════════════════════════
# 6. Confidence Score
# ══════════════════════════════════════════════════════════════════════

def compute_confidence_score(
    electricity_kwh: float,
    fuel_litres: float,
    model_loaded: bool,
    flags: List[str],
    historical_n: int = 0,
) -> Tuple[float, Dict[str, float]]:
    """
    Compute a 0–1 confidence score and a prediction range.
    Higher = more confident.
    """
    base = 0.85 if model_loaded else 0.70

    # Penalise for data quality flags
    penalty = len([f for f in flags if "⚠️" in f]) * 0.06
    base = max(0.40, base - penalty)

    # Bonus for having historical data
    history_bonus = min(0.10, historical_n * 0.015)
    confidence = min(0.97, base + history_bonus)

    # Prediction range (±uncertainty %)
    uncertainty_pct = (1 - confidence) * 0.60   # e.g. 0.88 conf → ±7.2%
    co2 = electricity_kwh * ELECTRICITY_FACTOR + fuel_litres * FUEL_FACTOR_DIESEL
    low  = round(co2 * (1 - uncertainty_pct), 2)
    high = round(co2 * (1 + uncertainty_pct), 2)

    return round(confidence, 3), {"low": low, "high": high}


# ══════════════════════════════════════════════════════════════════════
# 7. Yearly Simulation
# ══════════════════════════════════════════════════════════════════════

def compute_yearly_impact(savings_co2_per_month: float, savings_inr_per_month: float) -> Dict[str, Any]:
    """Convert monthly savings into yearly equivalents with eco-metaphors."""
    yearly_co2  = savings_co2_per_month * 12
    yearly_cost = savings_inr_per_month * 12

    # 1 mature tree sequesters ~21 kg CO₂/year
    trees = int(yearly_co2 / 21) if yearly_co2 > 0 else 0

    # Average Indian home uses ~100 kWh/month → 0.82 kg CO₂ * 100 = 82 kg/month
    homes = round(yearly_co2 / (82 * 12), 2) if yearly_co2 > 0 else 0

    # kms not driven (avg petrol car emits 0.12 kg/km)
    km_avoided = round(yearly_co2 / 0.12, 0) if yearly_co2 > 0 else 0

    return {
        "yearly_co2_savings":       round(yearly_co2, 1),
        "yearly_cost_savings_inr":  round(yearly_cost, 2),
        "trees_equivalent":         trees,
        "homes_powered_equivalent": homes,
        "km_not_driven":            int(km_avoided),
    }
