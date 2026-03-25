"""Pydantic models for v2 features"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any


# ──── ESG Scoring Models ────

class ESGInputModel(BaseModel):
    """Input data for ESG scoring calculation"""
    co2_kg: float
    annual_savings_reduction: Optional[float] = 0
    renewable_usage_pct: Optional[float] = 0
    carbon_offset_tons: Optional[float] = 0
    employees: Optional[int] = 10
    industry_sector: Optional[str] = "General MSME"
    
    # Certifications & commitments
    certified_emissions_plan: Optional[bool] = False
    esg_report_published: Optional[bool] = False
    third_party_audit: Optional[bool] = False
    sustainability_commitment: Optional[bool] = False
    community_programs: Optional[bool] = False
    dei_programs: Optional[bool] = False
    data_transparency: Optional[bool] = False


class ESGRecommendation(BaseModel):
    """Single ESG recommendation"""
    category: str
    priority: str  # HIGH, MEDIUM, LOW
    action: str
    impact: str


class ESGScoreResponse(BaseModel):
    """ESG score response"""
    environmental_score: float
    social_score: float
    governance_score: float
    overall_score: float
    grade: str
    recommendations: List[ESGRecommendation]


class ESGBenchmark(BaseModel):
    """Industry benchmark comparison"""
    industry: str
    your_score: float
    industry_average: float
    industry_leader_score: float
    percentile: float
    vs_average: float
    performance: str


class ESGV2Response(BaseModel):
    """Complete ESG API response"""
    success: bool
    data: ESGScoreResponse
    benchmark: ESGBenchmark
    message: str


# ──── Benchmark Models ────

class BenchmarkInputModel(BaseModel):
    """Input for benchmark comparison"""
    value: float
    category: str  # carbon_footprint, esg_score, cost_savings, renewable_adoption
    industry: str  # retail, manufacturing, tech, energy, finance
    region: Optional[str] = "global"


class ComparisonMetrics(BaseModel):
    """Comparison metrics"""
    your_value: float
    industry_average: float
    best_performer: float
    worst_performer: float


class ImprovementPotential(BaseModel):
    """Improvement opportunities"""
    to_reach_average: float
    to_reach_top_quartile: float


class PeerGroupResponse(BaseModel):
    """Peer group analysis"""
    peer_group: str
    your_ranking: str
    performance: str
    comparison: ComparisonMetrics
    improvement_potential: ImprovementPotential


class BenchmarkResponse(BaseModel):
    """Benchmark comparison response"""
    success: bool
    data: Dict[str, Any]
    message: str


# ──── Feature Flag Models ----

class FeatureFlagStatus(BaseModel):
    """Feature flag status for admin dashboard"""
    feature: str
    enabled: bool


class FeatureFlagListResponse(BaseModel):
    """List of all feature flags"""
    success: bool
    features: Dict[str, bool]
    message: str


# ──── LSTM Forecast Models ----

class LSTMForecastInputModel(BaseModel):
    """Input for LSTM forecasting"""
    historical_data: List[float]
    months_ahead: int = 12


class LSTMScenarioInputModel(BaseModel):
    """Input for scenario forecasting"""
    historical_data: List[float]
    reduction_pct: float = 15
    months_ahead: int = 12


class LSTMEnsembleInputModel(BaseModel):
    """Input for ensemble forecasting"""
    historical_data: List[float]
    months_ahead: int = 12


class ForecastPoint(BaseModel):
    """Single forecast data point"""
    month: int
    predicted_co2: float
    confidence_interval_low: float
    confidence_interval_high: float
    trend: str


class LSTMForecastResponse(BaseModel):
    """LSTM forecast response"""
    success: bool
    data: Dict[str, Any]
    message: str


# ──── Anomaly Detection Models ----

class AnomalyDetectionInputModel(BaseModel):
    """Input for anomaly detection"""
    historical_data: List[float]
    sensitivity: str = "medium"  # "low", "medium", "high"


class AnomalyPointModel(BaseModel):
    """Single anomaly detection result"""
    month: int
    value: float
    is_anomaly: bool
    anomaly_score: float
    deviation_pct: float
    method: str
    severity: str


class AnomalyDetectionResponse(BaseModel):
    """Anomaly detection response"""
    success: bool
    data: Dict[str, Any]
    message: str


# ──── Advanced Simulation Models ----

class MonteCarloInputModel(BaseModel):
    """Input for Monte Carlo simulation"""
    historical_data: List[float]
    num_months: int = 12
    volatility_multiplier: float = 1.0
    trend: str = "auto"  # "auto", "increasing", "decreasing", "stable"


class ScenarioAnalysisInputModel(BaseModel):
    """Input for scenario analysis simulation"""
    historical_data: List[float]
    scenario_adjustments: Dict[str, float]
    num_months: int = 12


class SimulationPointModel(BaseModel):
    """Aggregated simulation point with percentiles"""
    month: int
    mean_co2: float
    percentile_5: float
    percentile_25: float
    percentile_50: float
    percentile_75: float
    percentile_95: float
    std_dev: float


class SimulationResponse(BaseModel):
    """Monte Carlo simulation response"""
    success: bool
    data: Dict[str, Any]
    message: str


# ──── CSV Upload Models ----

class CSVUploadInputModel(BaseModel):
    """Input for CSV file upload"""
    csv_content: str
    source_name: str = "Uploaded CSV"
    delimiter: str = ","


class CSVValidationInput(BaseModel):
    """Input for CSV validation"""
    csv_content: str
    delimiter: str = ","


class CSVValidationResponse(BaseModel):
    """CSV validation response"""
    success: bool
    data: Dict[str, Any]
    message: str


class CSVImportResponse(BaseModel):
    """CSV import response"""
    success: bool
    data: Dict[str, Any]
    message: str


# ──── AI Chatbot Models ----

class ChatInputModel(BaseModel):
    """Input for chatbot message"""
    message: str
    conversation_id: str = "default"


class ChatIntentModel(BaseModel):
    """Detected chat intent"""
    intent_type: str
    confidence: float
    entities: Dict[str, Any]
    relevant_services: List[str]


class ChatSuggestionModel(BaseModel):
    """Chat suggestion/action"""
    text: str
    emoji: str = "💡"


class ChatResponseModel(BaseModel):
    """Chatbot response"""
    message: str
    intent: str
    suggestions: List[str]
    service_calls: List[Dict[str, Any]]
    confidence: float
    timestamp: str = ""


class ChatHistoryModel(BaseModel):
    """Chat message in history"""
    content: str
    timestamp: str
    sender: str  # "user" or "bot"


class ConversationContextModel(BaseModel):
    """Conversation context"""
    conversation_id: str
    message_count: int
    last_intent: Optional[str] = None
    data_source: Optional[str] = None
    analysis_type: Optional[str] = None


class ChatAPIResponse(BaseModel):
    """API response for chat"""
    success: bool
    data: Dict[str, Any]
    message: str
