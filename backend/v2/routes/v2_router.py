"""V2 API Routes - New features with feature flags"""

from fastapi import APIRouter, HTTPException
from v2.feature_flags import is_feature_enabled, FeatureFlag, get_feature_manager
from v2.services.esg_service import ESGScoringService
from v2.services.benchmark_service import BenchmarkService, BenchmarkCategory
from v2.services.lstm_service import LSTMForecastService
from v2.services.anomaly_service import AnomalyDetectionService
from v2.services.simulation_service import AdvancedSimulationService
from v2.services.csv_service import CSVUploadService
from v2.services.chatbot_service import AIConversationService, ConversationManager
from v2.models.schemas import (
    ESGInputModel, ESGV2Response, FeatureFlagListResponse, BenchmarkInputModel, BenchmarkResponse,
    LSTMForecastInputModel, LSTMScenarioInputModel, LSTMEnsembleInputModel, LSTMForecastResponse,
    AnomalyDetectionInputModel, AnomalyDetectionResponse, MonteCarloInputModel, ScenarioAnalysisInputModel, SimulationResponse,
    CSVUploadInputModel, CSVValidationInput, CSVValidationResponse, CSVImportResponse,
    ChatInputModel, ChatResponseModel, ConversationContextModel, ChatAPIResponse
)

router = APIRouter(prefix="/api/v2", tags=["v2 - New Features"])

# Initialize services
esg_service = ESGScoringService()
benchmark_service = BenchmarkService()
lstm_service = LSTMForecastService()
anomaly_service = AnomalyDetectionService()
simulation_service = AdvancedSimulationService()
csv_service = CSVUploadService()
conversation_manager = ConversationManager()


@router.post("/esg-score", response_model=ESGV2Response)
def calculate_esg_score(input_data: ESGInputModel):
    """
    Calculate comprehensive ESG (Environmental, Social, Governance) score
    Requires: ESG_SCORING feature flag enabled
    """
    
    # Check if feature is enabled
    if not is_feature_enabled(FeatureFlag.ESG_SCORING):
        raise HTTPException(
            status_code=403,
            detail="ESG Scoring feature is not enabled. Contact administrator."
        )
    
    try:
        # Calculate ESG score
        esg_score = esg_service.calculate_esg_score(input_data.dict())
        
        # Get industry benchmark
        benchmark = esg_service.benchmark_against_industry(
            esg_score.overall_score,
            input_data.industry_sector
        )
        
        # Convert ESGScore dataclass to Pydantic models
        from v2.models.schemas import ESGScoreResponse, ESGRecommendation
        
        esg_response = ESGScoreResponse(
            environmental_score=esg_score.environmental_score,
            social_score=esg_score.social_score,
            governance_score=esg_score.governance_score,
            overall_score=esg_score.overall_score,
            grade=esg_score.grade,
            recommendations=[
                ESGRecommendation(**rec) for rec in esg_score.recommendations
            ]
        )
        
        return ESGV2Response(
            success=True,
            data=esg_response,
            benchmark=benchmark,
            message=f"ESG Score: {esg_score.overall_score} ({esg_score.grade}) | "
                    f"Benchmark: {benchmark['vs_average']:+.1f} vs industry average"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/features")
def get_features():
    """
    Get all available v2 features and their status
    Public endpoint (no auth required)
    """
    manager = get_feature_manager()
    return {
        "success": True,
        "features": manager.get_status(),
        "enabled": {k: v for k, v in manager.get_status().items() if v},
        "message": "Feature flag status retrieved successfully"
    }


@router.get("/health-v2")
def health_check():
    """Health check for v2 services"""
    manager = get_feature_manager()
    return {
        "status": "healthy",
        "version": "2.0.0",
        "features_enabled": sum(1 for v in manager.get_status().values() if v),
        "total_features": len(manager.get_status())
    }


@router.post("/benchmark", response_model=BenchmarkResponse)
def get_benchmark(input_data: BenchmarkInputModel):
    """
    Get benchmark comparison for a metric
    Requires: BENCHMARKING feature flag enabled
    """
    
    if not is_feature_enabled(FeatureFlag.BENCHMARKING):
        raise HTTPException(
            status_code=403,
            detail="Benchmarking feature is not enabled. Contact administrator."
        )
    
    try:
        # Map category string to enum
        category_map = {
            "carbon_footprint": BenchmarkCategory.CARBON_FOOTPRINT,
            "esg_score": BenchmarkCategory.ESG_SCORE,
            "cost_savings": BenchmarkCategory.COST_SAVINGS,
            "renewable_adoption": BenchmarkCategory.RENEWABLE_ADOPTION,
        }
        
        category = category_map.get(input_data.category)
        if not category:
            raise ValueError(f"Unknown category: {input_data.category}")
        
        # Get benchmark data
        benchmark = benchmark_service.get_benchmark(
            value=input_data.value,
            category=category,
            industry=input_data.industry,
            region=input_data.region
        )
        
        # Convert to dict for JSON response
        benchmark_dict = {
            "your_value": benchmark.your_value,
            "industry_average": benchmark.industry_average,
            "industry_percentile": benchmark.industry_percentile,
            "regional_average": benchmark.regional_average,
            "regional_percentile": benchmark.regional_percentile,
            "best_in_class": benchmark.best_in_class,
            "worst_in_class": benchmark.worst_in_class,
            "performance_rating": benchmark.performance_rating,
            "gap_to_average": benchmark.gap_to_average,
            "gap_to_best": benchmark.gap_to_best,
        }
        
        return BenchmarkResponse(
            success=True,
            data=benchmark_dict,
            message=f"Benchmark: {benchmark.performance_rating} | "
                    f"Top {benchmark.industry_percentile:.0f}% in {input_data.industry}"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/benchmark/peer-group", response_model=BenchmarkResponse)
def get_peer_group(input_data: BenchmarkInputModel):
    """
    Get peer group analysis for a metric
    Requires: BENCHMARKING feature flag enabled
    """
    
    if not is_feature_enabled(FeatureFlag.BENCHMARKING):
        raise HTTPException(
            status_code=403,
            detail="Benchmarking feature is not enabled. Contact administrator."
        )
    
    try:
        category_map = {
            "carbon_footprint": BenchmarkCategory.CARBON_FOOTPRINT,
            "esg_score": BenchmarkCategory.ESG_SCORE,
            "cost_savings": BenchmarkCategory.COST_SAVINGS,
            "renewable_adoption": BenchmarkCategory.RENEWABLE_ADOPTION,
        }
        
        category = category_map.get(input_data.category)
        if not category:
            raise ValueError(f"Unknown category: {input_data.category}")
        
        peer_group = benchmark_service.get_peer_group(
            your_value=input_data.value,
            category=category,
            industry=input_data.industry,
            region=input_data.region
        )
        
        return BenchmarkResponse(
            success=True,
            data=peer_group,
            message=f"Peer Analysis: {peer_group['performance']} performance"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmark/industry/{industry}")
def get_industry_summary(industry: str):
    """
    Get industry benchmark summary
    Requires: BENCHMARKING feature flag enabled
    """
    
    if not is_feature_enabled(FeatureFlag.BENCHMARKING):
        raise HTTPException(
            status_code=403,
            detail="Benchmarking feature is not enabled. Contact administrator."
        )
    
    try:
        summary = benchmark_service.get_industry_summary(industry)
        return {
            "success": True,
            "data": summary,
            "message": f"Industry summary for {industry.title()}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/benchmark/compare-industries")
def compare_industries(input_data: BenchmarkInputModel):
    """
    Compare a value across all industries
    Requires: BENCHMARKING feature flag enabled
    """
    
    if not is_feature_enabled(FeatureFlag.BENCHMARKING):
        raise HTTPException(
            status_code=403,
            detail="Benchmarking feature is not enabled. Contact administrator."
        )
    
    try:
        category_map = {
            "carbon_footprint": BenchmarkCategory.CARBON_FOOTPRINT,
            "esg_score": BenchmarkCategory.ESG_SCORE,
            "cost_savings": BenchmarkCategory.COST_SAVINGS,
            "renewable_adoption": BenchmarkCategory.RENEWABLE_ADOPTION,
        }
        
        category = category_map.get(input_data.category)
        if not category:
            raise ValueError(f"Unknown category: {input_data.category}")
        
        comparisons = benchmark_service.compare_industries(
            value=input_data.value,
            category=category
        )
        
        return {
            "success": True,
            "data": comparisons,
            "message": f"Comparison across {len(comparisons)} industries"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast/lstm", response_model=LSTMForecastResponse)
def forecast_lstm(input_data: LSTMForecastInputModel):
    """
    LSTM-based emissions forecast
    Requires: LSTM_FORECAST feature flag enabled
    
    Args:
        input_data: Historical data and forecast parameters
    """
    
    if not is_feature_enabled(FeatureFlag.LSTM_FORECAST):
        raise HTTPException(
            status_code=403,
            detail="LSTM Forecast feature is not enabled. Contact administrator."
        )
    
    try:
        historical_data = input_data.historical_data
        months_ahead = input_data.months_ahead
        
        if not historical_data or len(historical_data) < 3:
            raise ValueError("Need at least 3 historical data points")
        
        forecast_result = lstm_service.forecast_lstm(
            historical_data=historical_data,
            months_ahead=months_ahead
        )
        
        forecast_data = [
            {
                "month": p.month,
                "predicted_co2": p.predicted_co2,
                "confidence_interval_low": p.confidence_interval_low,
                "confidence_interval_high": p.confidence_interval_high,
                "trend": p.trend
            }
            for p in forecast_result.forecast_points
        ]
        
        return {
            "success": True,
            "data": {
                "forecast": forecast_data,
                "accuracy_score": forecast_result.accuracy_score,
                "model_type": forecast_result.model_type,
                "method": forecast_result.method_details
            },
            "message": f"LSTM forecast for {months_ahead} months (Accuracy: {forecast_result.accuracy_score:.1%})"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast/scenario", response_model=LSTMForecastResponse)
def forecast_scenario(input_data: LSTMScenarioInputModel):
    """
    Forecast with reduction scenario
    Simulates impact of emissions reduction initiatives
    Requires: LSTM_FORECAST feature flag enabled
    """
    
    if not is_feature_enabled(FeatureFlag.LSTM_FORECAST):
        raise HTTPException(
            status_code=403,
            detail="LSTM Forecast feature is not enabled. Contact administrator."
        )
    
    try:
        historical_data = input_data.historical_data
        reduction_pct = input_data.reduction_pct
        months_ahead = input_data.months_ahead
        
        forecast_result = lstm_service.forecast_scenario(
            historical_data=historical_data,
            reduction_pct=reduction_pct,
            months_ahead=months_ahead
        )
        
        forecast_data = [
            {
                "month": p.month,
                "predicted_co2": p.predicted_co2,
                "confidence_interval_low": p.confidence_interval_low,
                "confidence_interval_high": p.confidence_interval_high,
                "trend": p.trend
            }
            for p in forecast_result.forecast_points
        ]
        
        # Calculate total reduction
        if historical_data:
            baseline = historical_data[-1]
            projected = forecast_result.forecast_points[-1].predicted_co2
            total_reduction = baseline - projected
        else:
            total_reduction = 0
        
        return {
            "success": True,
            "data": {
                "forecast": forecast_data,
                "reduction_scenario": {
                    "annual_reduction_pct": reduction_pct,
                    "projected_total_reduction_kg": round(total_reduction, 2),
                    "accuracy_score": forecast_result.accuracy_score
                },
                "model_type": forecast_result.model_type,
                "method": forecast_result.method_details
            },
            "message": f"Scenario forecast: {reduction_pct}% annual reduction = {total_reduction:.0f} kg saved"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast/ensemble", response_model=LSTMForecastResponse)
def forecast_ensemble(input_data: LSTMEnsembleInputModel):
    """
    Advanced ensemble forecast combining multiple models
    More accurate for volatile patterns
    Requires: LSTM_FORECAST feature flag enabled
    """
    
    if not is_feature_enabled(FeatureFlag.LSTM_FORECAST):
        raise HTTPException(
            status_code=403,
            detail="LSTM Forecast feature is not enabled. Contact administrator."
        )
    
    try:
        historical_data = input_data.historical_data
        months_ahead = input_data.months_ahead
        
        forecast_result = lstm_service.forecast_ensemble(
            historical_data=historical_data,
            months_ahead=months_ahead
        )
        
        forecast_data = [
            {
                "month": p.month,
                "predicted_co2": p.predicted_co2,
                "confidence_interval_low": p.confidence_interval_low,
                "confidence_interval_high": p.confidence_interval_high,
                "trend": p.trend
            }
            for p in forecast_result.forecast_points
        ]
        
        # Get AI summary
        summary = lstm_service.get_forecast_ai_summary(forecast_result)
        
        return {
            "success": True,
            "data": {
                "forecast": forecast_data,
                "accuracy_score": forecast_result.accuracy_score,
                "model_type": forecast_result.model_type,
                "method": forecast_result.method_details,
                "ai_summary": summary
            },
            "message": f"Ensemble forecast: {summary['recommendation']}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/anomaly/detect", response_model=AnomalyDetectionResponse)
def detect_anomalies(input_data: AnomalyDetectionInputModel):
    """
    Detect anomalies in emissions data
    Uses Isolation Forest + Statistical methods (z-score, IQR)
    Requires: ANOMALY_DETECTION feature flag enabled
    """
    
    if not is_feature_enabled(FeatureFlag.ANOMALY_DETECTION):
        raise HTTPException(
            status_code=403,
            detail="Anomaly Detection feature is not enabled. Contact administrator."
        )
    
    try:
        historical_data = input_data.historical_data
        sensitivity = input_data.sensitivity
        
        if not historical_data or len(historical_data) < 4:
            raise ValueError("Need at least 4 historical data points")
        
        result = anomaly_service.detect_anomalies(
            historical_data=historical_data,
            sensitivity=sensitivity
        )
        
        # Format anomalies for response
        anomalies_data = [
            {
                "month": a.month,
                "value": round(a.value, 2),
                "is_anomaly": a.is_anomaly,
                "anomaly_score": round(a.anomaly_score, 3),
                "deviation_pct": round(a.deviation_pct, 1),
                "method": a.method,
                "severity": a.severity
            }
            for a in result.anomalies_detected
        ]
        
        return {
            "success": True,
            "data": {
                "anomalies": anomalies_data,
                "summary": {
                    "total_anomalies": result.anomaly_count,
                    "anomaly_percentage": round(result.anomaly_percentage, 1),
                    "average_anomaly_score": round(result.average_anomaly_score, 3),
                    "health_status": result.overall_health
                },
                "trend_analysis": result.trend_analysis,
                "recommendations": result.recommendations
            },
            "message": f"Anomaly detection complete: {result.anomaly_count} anomalies detected ({result.anomaly_percentage:.1f}%)"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/anomaly/summary", response_model=AnomalyDetectionResponse)
def get_anomaly_summary(input_data: AnomalyDetectionInputModel):
    """
    Ai-powered anomaly summary with insights and actions
    Requires: ANOMALY_DETECTION feature flag enabled
    """
    
    if not is_feature_enabled(FeatureFlag.ANOMALY_DETECTION):
        raise HTTPException(
            status_code=403,
            detail="Anomaly Detection feature is not enabled. Contact administrator."
        )
    
    try:
        result = anomaly_service.detect_anomalies(
            historical_data=input_data.historical_data,
            sensitivity=input_data.sensitivity
        )
        
        # Get AI summary
        ai_summary = anomaly_service.get_anomaly_summary_ai(result)
        
        return {
            "success": True,
            "data": {
                "health_status": ai_summary["health_status"],
                "anomalies_found": ai_summary["anomalies_found"],
                "anomaly_rate_pct": ai_summary["anomaly_rate_pct"],
                "severity_distribution": ai_summary["severity_distribution"],
                "trend": ai_summary["trend"],
                "key_metrics": ai_summary["key_metrics"],
                "recommendations": ai_summary["recommendations"],
                "next_actions": ai_summary["next_actions"]
            },
            "message": f"Anomaly Analysis: System Health = {ai_summary['health_status']}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulation/run-monte-carlo", response_model=SimulationResponse)
def run_monte_carlo(input_data: MonteCarloInputModel):
    """
    Run Monte Carlo simulation for emissions forecasting with risk analysis
    Generates 10,000 possible paths using Geometric Brownian Motion
    Calculates risk metrics: VaR, CVaR, skewness, kurtosis, percentiles
    Requires: ADVANCED_SIMULATION feature flag enabled
    
    Args:
        input_data: Historical data and simulation parameters
    """
    
    if not is_feature_enabled(FeatureFlag.ADVANCED_SIMULATION):
        raise HTTPException(
            status_code=403,
            detail="Advanced Simulation feature is not enabled. Contact administrator."
        )
    
    try:
        historical_data = input_data.historical_data
        num_months = input_data.num_months
        volatility_multiplier = input_data.volatility_multiplier
        trend = input_data.trend
        
        if not historical_data or len(historical_data) < 3:
            raise ValueError("Need at least 3 historical data points")
        
        # Run Monte Carlo simulation
        result = simulation_service.run_monte_carlo(
            historical_data=historical_data,
            num_months=num_months,
            volatility_multiplier=volatility_multiplier,
            trend=trend
        )
        
        # Format aggregated results for response
        aggregated_results = [
            {
                "month": point.month,
                "mean_co2": round(point.mean_co2, 2),
                "percentile_5": round(point.percentile_5, 2),
                "percentile_25": round(point.percentile_25, 2),
                "percentile_50": round(point.percentile_50, 2),
                "percentile_75": round(point.percentile_75, 2),
                "percentile_95": round(point.percentile_95, 2),
                "std_dev": round(point.std_dev, 2)
            }
            for point in result["aggregated_results"]
        ]
        
        # Get AI summary
        ai_summary = simulation_service.get_simulation_summary_ai(result)
        
        return {
            "success": True,
            "data": {
                "simulation_results": aggregated_results,
                "risk_metrics": {
                    "value_at_risk_95": round(result["risk_metrics"]["value_at_risk_95"], 2),
                    "conditional_value_at_risk": round(result["risk_metrics"]["conditional_value_at_risk"], 2),
                    "percentile_probability": round(result["risk_metrics"]["percentile_probability"], 3),
                    "skewness": round(result["risk_metrics"]["skewness"], 3),
                    "kurtosis": round(result["risk_metrics"]["kurtosis"], 3)
                },
                "scenario_paths": {
                    "base_case": [round(v, 2) for v in result["scenario_paths"]["base_case"]],
                    "best_case": [round(v, 2) for v in result["scenario_paths"]["best_case"]],
                    "worst_case": [round(v, 2) for v in result["scenario_paths"]["worst_case"]]
                },
                "ai_summary": ai_summary
            },
            "message": f"Monte Carlo simulation complete: {num_months} months, {result['risk_metrics']['percentile_probability']:.1%} probability final value < 95th percentile"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulation/scenario-analysis", response_model=SimulationResponse)
def scenario_analysis(input_data: ScenarioAnalysisInputModel):
    """
    Analyze custom emissions scenarios with adjustable volatility and trend
    Useful for what-if analysis and strategic planning
    Requires: ADVANCED_SIMULATION feature flag enabled
    
    Args:
        input_data: Historical data, num_months, and scenario adjustments
        scenario_adjustments: Dict with 'volatility' and 'trend' modifications
    """
    
    if not is_feature_enabled(FeatureFlag.ADVANCED_SIMULATION):
        raise HTTPException(
            status_code=403,
            detail="Advanced Simulation feature is not enabled. Contact administrator."
        )
    
    try:
        historical_data = input_data.historical_data
        num_months = input_data.num_months
        scenario_adjustments = input_data.scenario_adjustments
        
        if not historical_data or len(historical_data) < 3:
            raise ValueError("Need at least 3 historical data points")
        
        # Run scenario analysis
        result = simulation_service.scenario_analysis(
            historical_data=historical_data,
            scenario_adjustments=scenario_adjustments,
            num_months=num_months
        )
        
        # Format aggregated results for response
        aggregated_results = [
            {
                "month": point.month,
                "mean_co2": round(point.mean_co2, 2),
                "percentile_5": round(point.percentile_5, 2),
                "percentile_25": round(point.percentile_25, 2),
                "percentile_50": round(point.percentile_50, 2),
                "percentile_75": round(point.percentile_75, 2),
                "percentile_95": round(point.percentile_95, 2),
                "std_dev": round(point.std_dev, 2)
            }
            for point in result["aggregated_results"]
        ]
        
        # Get AI summary
        ai_summary = simulation_service.get_simulation_summary_ai(result)
        
        return {
            "success": True,
            "data": {
                "scenario_name": result.get("scenario_name", "Custom Scenario"),
                "adjustments_applied": scenario_adjustments,
                "simulation_results": aggregated_results,
                "risk_metrics": {
                    "value_at_risk_95": round(result["risk_metrics"]["value_at_risk_95"], 2),
                    "conditional_value_at_risk": round(result["risk_metrics"]["conditional_value_at_risk"], 2),
                    "percentile_probability": round(result["risk_metrics"]["percentile_probability"], 3),
                    "skewness": round(result["risk_metrics"]["skewness"], 3),
                    "kurtosis": round(result["risk_metrics"]["kurtosis"], 3)
                },
                "scenario_paths": {
                    "base_case": [round(v, 2) for v in result["scenario_paths"]["base_case"]],
                    "best_case": [round(v, 2) for v in result["scenario_paths"]["best_case"]],
                    "worst_case": [round(v, 2) for v in result["scenario_paths"]["worst_case"]]
                },
                "ai_summary": ai_summary
            },
            "message": f"Scenario analysis complete with adjustments: {scenario_adjustments}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/csv/validate", response_model=CSVValidationResponse)
def validate_csv(input_data: CSVValidationInput):
    """
    Validate CSV content and structure
    Checks for required columns, data types, and emissions values
    Requires: CSV_UPLOAD feature flag enabled
    
    Args:
        input_data: CSV content and delimiter
    """
    
    if not is_feature_enabled(FeatureFlag.CSV_UPLOAD):
        raise HTTPException(
            status_code=403,
            detail="CSV Upload feature is not enabled. Contact administrator."
        )
    
    try:
        # Validate CSV
        validation_result = csv_service.validate_csv_content(
            csv_content=input_data.csv_content,
            delimiter=input_data.delimiter
        )
        
        return {
            "success": validation_result.is_valid,
            "data": {
                "is_valid": validation_result.is_valid,
                "data_points": validation_result.data_points,
                "date_range": validation_result.date_range,
                "numeric_columns": validation_result.numeric_columns,
                "errors": validation_result.errors,
                "warnings": validation_result.warnings
            },
            "message": f"Validation: {validation_result.data_points} data points found" if validation_result.is_valid else f"Validation failed: {'; '.join(validation_result.errors)}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/csv/import", response_model=CSVImportResponse)
def import_csv(input_data: CSVUploadInputModel):
    """
    Import and process CSV emissions data
    Extracts emissions series for analysis with LSTM, simulation, anomaly detection
    Requires: CSV_UPLOAD feature flag enabled
    
    Args:
        input_data: CSV content, source name, and delimiter
    """
    
    if not is_feature_enabled(FeatureFlag.CSV_UPLOAD):
        raise HTTPException(
            status_code=403,
            detail="CSV Upload feature is not enabled. Contact administrator."
        )
    
    try:
        # Import CSV
        import_result = csv_service.import_csv_data(
            csv_content=input_data.csv_content,
            delimiter=input_data.delimiter,
            source_name=input_data.source_name
        )
        
        if not import_result.success:
            raise ValueError(import_result.message)
        
        # Generate summary
        summary = csv_service.generate_import_summary(import_result)
        
        return {
            "success": True,
            "data": {
                "import_summary": summary,
                "emissions_data": import_result.emissions_series,
                "dates": import_result.dates,
                "metadata": import_result.metadata,
                "next_actions": [
                    "Use emissions_data for LSTM forecasting: POST /api/v2/forecast/lstm",
                    "Run anomaly detection: POST /api/v2/anomaly/detect",
                    "Generate Monte Carlo simulations: POST /api/v2/simulation/run-monte-carlo",
                    "Get ESG score: POST /api/v2/esg-score"
                ]
            },
            "message": import_result.message
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/csv/preview", response_model=CSVValidationResponse)
def preview_csv(input_data: CSVValidationInput):
    """
    Preview parsed CSV data without importing
    Shows parsed rows and detection of date/emissions columns
    Requires: CSV_UPLOAD feature flag enabled
    
    Args:
        input_data: CSV content and delimiter
    """
    
    if not is_feature_enabled(FeatureFlag.CSV_UPLOAD):
        raise HTTPException(
            status_code=403,
            detail="CSV Upload feature is not enabled. Contact administrator."
        )
    
    try:
        # Validate and get parsed data
        validation_result = csv_service.validate_csv_content(
            csv_content=input_data.csv_content,
            delimiter=input_data.delimiter
        )
        
        # Prepare preview data (first 10 rows)
        preview_rows = []
        if validation_result.parsed_data:
            for row in validation_result.parsed_data[:10]:
                preview_rows.append(row)
        
        return {
            "success": validation_result.is_valid,
            "data": {
                "is_valid": validation_result.is_valid,
                "total_data_points": validation_result.data_points,
                "preview_rows": preview_rows,
                "preview_count": len(preview_rows),
                "date_range": validation_result.date_range,
                "numeric_columns": validation_result.numeric_columns,
                "errors": validation_result.errors,
                "warnings": validation_result.warnings
            },
            "message": f"Preview: showing {len(preview_rows)} of {validation_result.data_points} rows"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/message", response_model=ChatAPIResponse)
def chat_message(input_data: ChatInputModel):
    """
    Send message to AI chatbot for natural language Q&A
    Routes to appropriate services based on intent detection
    Requires: AI_CHATBOT feature flag enabled
    
    Args:
        input_data: User message and conversation ID
    """
    
    if not is_feature_enabled(FeatureFlag.AI_CHATBOT):
        raise HTTPException(
            status_code=403,
            detail="AI Chatbot feature is not enabled. Contact administrator."
        )
    
    try:
        # Get or create conversation
        conversation = conversation_manager.get_conversation(input_data.conversation_id)
        if not conversation:
            conversation = conversation_manager.create_conversation(input_data.conversation_id)
        
        # Add user message to history
        conversation.add_to_history(input_data.message, "user")
        
        # Detect intent
        intent = conversation.detect_intent(input_data.message)
        
        # Generate response
        chat_response = conversation.generate_response(intent)
        
        # Add bot response to history
        conversation.add_to_history(chat_response.message, "bot")
        
        # Update context
        conversation.current_context['last_intent'] = intent.intent_type
        
        return {
            "success": True,
            "data": {
                "message": chat_response.message,
                "intent": chat_response.intent,
                "intent_confidence": round(chat_response.confidence, 2),
                "suggestions": chat_response.suggestions,
                "service_calls": chat_response.service_calls,
                "entities": intent.entities,
                "conversation_id": input_data.conversation_id,
                "context": conversation.get_context_summary()
            },
            "message": f"Intent detected: {intent.intent_type} ({intent.confidence:.0%})"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/intents", response_model=ChatAPIResponse)
def analyze_intent(input_data: ChatInputModel):
    """
    Analyze user message for intent detection without generating response
    Returns detected intent, confidence, entities, and relevant services
    Requires: AI_CHATBOT feature flag enabled
    
    Args:
        input_data: User message
    """
    
    if not is_feature_enabled(FeatureFlag.AI_CHATBOT):
        raise HTTPException(
            status_code=403,
            detail="AI Chatbot feature is not enabled. Contact administrator."
        )
    
    try:
        # Get conversation
        conversation = conversation_manager.get_conversation(input_data.conversation_id)
        if not conversation:
            conversation = conversation_manager.create_conversation(input_data.conversation_id)
        
        # Detect intent only
        intent = conversation.detect_intent(input_data.message)
        
        return {
            "success": True,
            "data": {
                "intent_type": intent.intent_type,
                "confidence": round(intent.confidence, 2),
                "entities": intent.entities,
                "relevant_services": intent.relevant_services,
                "conversation_id": input_data.conversation_id
            },
            "message": f"Detected intent: {intent.intent_type} ({intent.confidence:.0%})"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/reset", response_model=ChatAPIResponse)
def reset_conversation(input_data: ChatInputModel):
    """
    Reset conversation history and context
    Requires: AI_CHATBOT feature flag enabled
    
    Args:
        input_data: Conversation ID
    """
    
    if not is_feature_enabled(FeatureFlag.AI_CHATBOT):
        raise HTTPException(
            status_code=403,
            detail="AI Chatbot feature is not enabled. Contact administrator."
        )
    
    try:
        conversation = conversation_manager.get_conversation(input_data.conversation_id)
        if conversation:
            conversation.reset_context()
        
        return {
            "success": True,
            "data": {
                "conversation_id": input_data.conversation_id,
                "status": "reset"
            },
            "message": "Conversation history cleared"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/context/{conversation_id}", response_model=ChatAPIResponse)
def get_context(conversation_id: str):
    """
    Get current conversation context and summary
    Requires: AI_CHATBOT feature flag enabled
    
    Args:
        conversation_id: ID of conversation
    """
    
    if not is_feature_enabled(FeatureFlag.AI_CHATBOT):
        raise HTTPException(
            status_code=403,
            detail="AI Chatbot feature is not enabled. Contact administrator."
        )
    
    try:
        conversation = conversation_manager.get_conversation(conversation_id)
        
        if not conversation:
            return {
                "success": False,
                "data": {"conversation_id": conversation_id},
                "message": "Conversation not found"
            }
        
        context = conversation.get_context_summary()
        
        return {
            "success": True,
            "data": {
                "conversation_id": conversation_id,
                "context": context,
                "history_length": len(conversation.conversation_history)
            },
            "message": "Conversation context retrieved"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat/conversation/{conversation_id}", response_model=ChatAPIResponse)
def delete_conversation(conversation_id: str):
    """
    Delete conversation and all history
    Requires: AI_CHATBOT feature flag enabled
    
    Args:
        conversation_id: ID of conversation to delete
    """
    
    if not is_feature_enabled(FeatureFlag.AI_CHATBOT):
        raise HTTPException(
            status_code=403,
            detail="AI Chatbot feature is not enabled. Contact administrator."
        )
    
    try:
        conversation_manager.delete_conversation(conversation_id)
        
        return {
            "success": True,
            "data": {"conversation_id": conversation_id},
            "message": "Conversation deleted"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
