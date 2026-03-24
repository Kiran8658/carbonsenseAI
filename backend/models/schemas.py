from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class EmissionInput(BaseModel):
    electricity_kwh: float = Field(..., ge=0, description="Electricity consumed in kWh")
    fuel_litres: float = Field(..., ge=0, description="Fuel consumed in litres")
    month: Optional[str] = Field(default=None, description="Month label e.g. 'Jan 2025'")
    business_type: Optional[str] = Field(default="MSME", description="Type of business")


class EmissionBreakdown(BaseModel):
    electricity_co2: float
    fuel_co2: float
    total_co2: float
    carbon_score: str
    carbon_score_value: int
    breakdown_percentage: dict


class EmissionResponse(BaseModel):
    success: bool
    data: EmissionBreakdown
    message: str


class SuggestionInput(BaseModel):
    electricity_kwh: float
    fuel_litres: float
    total_co2: float
    business_type: Optional[str] = "MSME"


class Suggestion(BaseModel):
    title: str
    description: str
    impact: str
    savings_percentage: float
    category: str
    priority: str


class SuggestionResponse(BaseModel):
    success: bool
    suggestions: List[Suggestion]
    summary: str
    estimated_reduction: float
    # Optional metadata used by the frontend to label which engine produced the result.
    model_used: Optional[str] = None


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
