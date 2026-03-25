from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date


class EmissionInput(BaseModel):
    electricity_kwh: float = Field(..., ge=0, le=100000, description="Electricity consumed in kWh")
    fuel_litres: float = Field(..., ge=0, le=50000, description="Fuel consumed in litres")
    month: Optional[str] = Field(default=None, description="Month label e.g. 'Jan 2025'")
    business_type: Optional[str] = Field(default="MSME", description="Type of business")
    industry_sector: Optional[str] = Field(default="Manufacturing", description="Industry sector")
    num_employees: Optional[int] = Field(default=None, ge=1, description="Number of employees")


class IndustryBenchmark(BaseModel):
    sector: str
    avg_monthly_co2: float
    your_co2: float
    percentile: float          # where user stands vs. peers (0–100)
    is_above_average: bool
    reduction_to_average: float


class CostSavings(BaseModel):
    current_monthly_cost_inr: float
    potential_monthly_savings_inr: float
    annual_savings_inr: float
    electricity_cost_inr: float
    fuel_cost_inr: float
    savings_from_efficiency_pct: float


class EmissionBreakdown(BaseModel):
    electricity_co2: float
    fuel_co2: float
    total_co2: float
    carbon_score: str
    carbon_score_value: int
    breakdown_percentage: dict
    # New fields
    confidence_score: Optional[float] = None   # 0–1 model confidence
    prediction_range: Optional[Dict[str, float]] = None  # {low, high}
    industry_benchmark: Optional[IndustryBenchmark] = None
    cost_savings: Optional[CostSavings] = None
    ml_model_used: Optional[str] = None
    data_quality_flags: Optional[List[str]] = None


class EmissionResponse(BaseModel):
    success: bool
    data: EmissionBreakdown
    message: str


class SuggestionInput(BaseModel):
    electricity_kwh: float
    fuel_litres: float
    total_co2: float
    business_type: Optional[str] = "MSME"
    industry_sector: Optional[str] = "Manufacturing"


class Suggestion(BaseModel):
    title: str
    description: str
    impact: str
    savings_percentage: float
    category: str
    priority: str
    cost_savings_inr: Optional[float] = None
    implementation_cost: Optional[str] = None
    payback_months: Optional[int] = None
    confidence: Optional[float] = None


class SuggestionResponse(BaseModel):
    success: bool
    suggestions: List[Suggestion]
    summary: str
    estimated_reduction: float
    model_used: Optional[str] = None
    total_potential_savings_inr: Optional[float] = None


class SimulatorInput(BaseModel):
    electricity_kwh: float
    fuel_litres: float
    electricity_reduction_pct: float = Field(default=0, ge=0, le=100)
    fuel_reduction_pct: float = Field(default=0, ge=0, le=100)


class SimulatorResponse(BaseModel):
    before_co2: float
    after_co2: float
    savings_co2: float
    savings_percentage: float
    electricity_before: float
    electricity_after: float
    fuel_before: float
    fuel_after: float
    # New: yearly projections
    yearly_co2_savings: Optional[float] = None
    yearly_cost_savings_inr: Optional[float] = None
    trees_equivalent: Optional[int] = None
    homes_powered_equivalent: Optional[float] = None


class PipelineStatusResponse(BaseModel):
    status: str
    models: Dict[str, Any]
    data_quality: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    last_updated: str
