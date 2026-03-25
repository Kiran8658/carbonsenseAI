"""
Advanced Simulation Service for CarbonSense v2
Monte Carlo simulation for emissions scenarios and risk analysis
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session
import numpy as np
from scipy import stats
import random


@dataclass
class SimulationPoint:
    """Single simulation outcome"""
    month: int
    mean_co2: float
    percentile_5: float
    percentile_25: float
    percentile_50: float
    percentile_75: float
    percentile_95: float
    std_dev: float


@dataclass
class SimulationResult:
    """Complete simulation results"""
    simulation_paths: List[List[float]]  # All Monte Carlo paths
    aggregated_results: List[SimulationPoint]
    base_case_path: List[float]
    best_case_path: List[float]
    worst_case_path: List[float]
    summary_statistics: Dict[str, float]
    risk_metrics: Dict[str, Any]
    scenario_name: str
    num_simulations: int
    num_months: int
    confidence_level: float


class AdvancedSimulationService:
    """Monte Carlo simulation for emissions forecasting and risk analysis"""
    
    def __init__(self, num_simulations: int = 10000, random_seed: int = 42):
        """
        Initialize simulation service
        
        Args:
            num_simulations: Number of Monte Carlo paths to generate
            random_seed: Random seed for reproducibility
        """
        self.num_simulations = num_simulations
        self.random_seed = random_seed
        random.seed(random_seed)
        np.random.seed(random_seed)
    
    def run_monte_carlo(
        self,
        historical_data: List[float],
        num_months: int = 12,
        volatility_multiplier: float = 1.0,
        trend: str = "auto",
        db: Session = None
    ) -> SimulationResult:
        """
        Run Monte Carlo simulation for emissions forecasting
        
        Args:
            historical_data: Historical CO2 emissions (kg)
            num_months: Number of months to forecast
            volatility_multiplier: Adjust volatility (1.0 = normal, 2.0 = double)
            trend: "auto", "increasing", "decreasing", "stable"
        
        Returns:
            SimulationResult with all paths and aggregated statistics
        """
        
        if not historical_data or len(historical_data) < 3:
            raise ValueError("Need at least 3 historical data points")
        
        historical_array = np.array(historical_data)
        
        # Calculate parameters
        mean_value = np.mean(historical_array)
        std_dev = np.std(historical_array)
        
        # Detect trend
        if trend == "auto":
            trend = self._detect_trend(historical_array)
        
        # Calculate drift (trend component)
        drift = self._calculate_drift(historical_array, trend)
        
        # Adjust volatility
        adjusted_volatility = std_dev * volatility_multiplier
        
        # Generate Monte Carlo paths
        simulation_paths = self._generate_paths(
            initial_value=historical_array[-1],
            mean=mean_value,
            drift=drift,
            volatility=adjusted_volatility,
            num_months=num_months,
            num_simulations=self.num_simulations
        )
        
        # Calculate aggregated results (percentiles at each month)
        aggregated_results = self._aggregate_results(simulation_paths)
        
        # Generate specific paths (base, best, worst)
        base_case = self._generate_single_path(
            initial_value=historical_array[-1],
            drift=drift,
            volatility=0,  # No randomness
            num_months=num_months
        )
        
        best_case = self._generate_single_path(
            initial_value=historical_array[-1],
            drift=drift * -1,  # Opposite trend
            volatility=adjusted_volatility * -0.5,
            num_months=num_months
        )
        
        worst_case = self._generate_single_path(
            initial_value=historical_array[-1],
            drift=drift,
            volatility=adjusted_volatility * 2,
            num_months=num_months
        )
        
        # Calculate summary statistics
        summary_stats = self._calculate_summary_stats(simulation_paths, aggregated_results)
        
        # Calculate risk metrics
        risk_metrics = self._calculate_risk_metrics(
            simulation_paths,
            aggregated_results,
            historical_array
        )
        
        result = SimulationResult(
            simulation_paths=simulation_paths,
            aggregated_results=aggregated_results,
            base_case_path=base_case,
            best_case_path=best_case,
            worst_case_path=worst_case,
            summary_statistics=summary_stats,
            risk_metrics=risk_metrics,
            scenario_name="Monte Carlo",
            num_simulations=self.num_simulations,
            num_months=num_months,
            confidence_level=0.95
        )
        
        # Store in database if session provided
        if db:
            self._store_simulation_result(db, result)
        
        return result
    
    def _detect_trend(self, data: np.ndarray) -> str:
        """Auto-detect trend from historical data"""
        
        if len(data) < 3:
            return "stable"
        
        recent = data[-3:]
        if recent[-1] > recent[0] * 1.1:
            return "increasing"
        elif recent[-1] < recent[0] * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_drift(self, data: np.ndarray, trend: str) -> float:
        """Calculate drift component for trend"""
        
        if len(data) < 2:
            return 0
        
        # Simple linear regression
        x = np.arange(len(data))
        slope = np.polyfit(x, data, 1)[0]
        
        if trend == "increasing":
            return abs(slope) * 0.1  # Amplify upward trend
        elif trend == "decreasing":
            return -abs(slope) * 0.1  # Amplify downward trend
        else:
            return 0  # Stable
    
    def _generate_paths(
        self,
        initial_value: float,
        mean: float,
        drift: float,
        volatility: float,
        num_months: int,
        num_simulations: int
    ) -> List[List[float]]:
        """Generate Monte Carlo simulation paths using Geometric Brownian Motion"""
        
        dt = 1.0  # Time step (months)
        paths = []
        
        for _ in range(num_simulations):
            path = [initial_value]
            current_value = initial_value
            
            for month in range(num_months):
                # Mean-reverting component
                mean_reversion = 0.1 * (mean - current_value) / mean if mean != 0 else 0
                
                # Random component (Brownian motion)
                dw = np.random.normal(0, np.sqrt(dt))
                
                # GBM formula with drift and volatility
                d_value = (drift + mean_reversion) * dt + volatility * dw
                next_value = current_value * (1 + d_value / current_value) if current_value != 0 else current_value
                
                # Ensure non-negative
                next_value = max(0, next_value)
                
                path.append(next_value)
                current_value = next_value
            
            paths.append(path)
        
        return paths
    
    def _generate_single_path(
        self,
        initial_value: float,
        drift: float,
        volatility: float,
        num_months: int
    ) -> List[float]:
        """Generate a single path for deterministic case (base/best/worst)"""
        
        path = [initial_value]
        current_value = initial_value
        
        for _ in range(num_months):
            d_value = drift  # No random component
            next_value = current_value * (1 + d_value / current_value) if current_value != 0 else current_value
            next_value = max(0, next_value)
            path.append(next_value)
            current_value = next_value
        
        return path
    
    def _aggregate_results(self, paths: List[List[float]]) -> List[SimulationPoint]:
        """Calculate percentiles at each time step"""
        
        num_months = len(paths[0]) - 1
        results = []
        
        for month in range(num_months):
            values_at_month = [path[month + 1] for path in paths]
            
            result = SimulationPoint(
                month=month + 1,
                mean_co2=float(np.mean(values_at_month)),
                percentile_5=float(np.percentile(values_at_month, 5)),
                percentile_25=float(np.percentile(values_at_month, 25)),
                percentile_50=float(np.percentile(values_at_month, 50)),
                percentile_75=float(np.percentile(values_at_month, 75)),
                percentile_95=float(np.percentile(values_at_month, 95)),
                std_dev=float(np.std(values_at_month))
            )
            results.append(result)
        
        return results
    
    def _calculate_summary_stats(
        self,
        paths: List[List[float]],
        aggregated: List[SimulationPoint]
    ) -> Dict[str, float]:
        """Calculate summary statistics"""
        
        final_values = [path[-1] for path in paths]
        
        return {
            "final_mean": float(np.mean(final_values)),
            "final_median": float(np.median(final_values)),
            "final_std_dev": float(np.std(final_values)),
            "final_min": float(np.min(final_values)),
            "final_max": float(np.max(final_values)),
            "final_5th_percentile": float(np.percentile(final_values, 5)),
            "final_95th_percentile": float(np.percentile(final_values, 95)),
            "range_5_95": float(np.percentile(final_values, 95) - np.percentile(final_values, 5)),
            "coefficient_of_variation": float(np.std(final_values) / np.mean(final_values)) if np.mean(final_values) != 0 else 0,
        }
    
    def _calculate_risk_metrics(
        self,
        paths: List[List[float]],
        aggregated: List[SimulationPoint],
        historical: np.ndarray
    ) -> Dict[str, Any]:
        """Calculate risk metrics (VaR, CVaR, probability of exceeding thresholds)"""
        
        final_values = np.array([path[-1] for path in paths])
        historical_mean = np.mean(historical)
        
        # Value at Risk (VaR) - 5th percentile
        var_95 = float(np.percentile(final_values, 5))
        
        # Conditional Value at Risk (CVaR) - average below 5th percentile
        cvar_threshold = np.percentile(final_values, 5)
        cvar_95 = float(np.mean(final_values[final_values <= cvar_threshold]))
        
        # Probability of exceeding historical mean
        prob_exceed = float(np.sum(final_values > historical_mean * 1.1) / len(final_values))
        
        # Probability of below historical mean
        prob_below = float(np.sum(final_values < historical_mean * 0.9) / len(final_values))
        
        # Skewness and kurtosis
        skewness = float(stats.skew(final_values))
        kurtosis = float(stats.kurtosis(final_values))
        
        return {
            "value_at_risk_95": var_95,
            "conditional_value_at_risk_95": cvar_95,
            "probability_exceed_threshold": prob_exceed,
            "probability_below_threshold": prob_below,
            "skewness": skewness,
            "kurtosis": kurtosis,
            "risk_level": self._assess_risk_level(prob_exceed, prob_below),
        }
    
    def _assess_risk_level(self, prob_exceed: float, prob_below: float) -> str:
        """Assess overall risk level"""
        
        if prob_exceed > 0.5 or prob_below > 0.5:
            return "CRITICAL"
        elif prob_exceed > 0.3 or prob_below > 0.3:
            return "HIGH"
        elif prob_exceed > 0.2 or prob_below > 0.2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def scenario_analysis(
        self,
        historical_data: List[float],
        scenario_adjustments: Dict[str, float],
        num_months: int = 12,
        db: Session = None
    ) -> SimulationResult:
        """
        Run scenario analysis with custom adjustments
        
        Args:
            historical_data: Historical emissions
            scenario_adjustments: Dict with keys like:
                - "volatility_multiplier": 0.5-2.0
                - "trend_strength": -1.0 to 1.0
                - "mean_reversion": 0.0 to 1.0
            num_months: Forecast period
        
        Returns:
            SimulationResult for the scenario
        """
        
        volatility_mult = scenario_adjustments.get("volatility_multiplier", 1.0)
        
        # Determine trend from adjustment
        trend_strength = scenario_adjustments.get("trend_strength", 0)
        if trend_strength > 0.3:
            trend = "increasing"
        elif trend_strength < -0.3:
            trend = "decreasing"
        else:
            trend = "stable"
        
        result = self.run_monte_carlo(
            historical_data=historical_data,
            num_months=num_months,
            volatility_multiplier=volatility_mult,
            trend=trend,
            db=db
        )
        
        # Update scenario name
        result.scenario_name = f"Custom Scenario (Vol:{volatility_mult:.1f}x, Trend:{trend})"
        
        return result
    
    def get_simulation_summary_ai(self, result: SimulationResult) -> Dict[str, Any]:
        """Generate AI-powered summary with insights"""
        
        summary_stats = result.summary_statistics
        risk_metrics = result.risk_metrics
        
        final_mean = summary_stats.get("final_mean", 0)
        initial_value = result.base_case_path[0]
        change_pct = ((final_mean - initial_value) / initial_value * 100) if initial_value != 0 else 0
        
        return {
            "scenario": result.scenario_name,
            "simulations_ran": result.num_simulations,
            "forecast_period_months": result.num_months,
            "base_case_final": round(result.base_case_path[-1], 2),
            "mean_forecast": round(final_mean, 2),
            "median_forecast": round(summary_stats.get("final_median", 0), 2),
            "expected_change_pct": round(change_pct, 1),
            "confidence_range": {
                "low_5th": round(summary_stats.get("final_5th_percentile", 0), 2),
                "high_95th": round(summary_stats.get("final_95th_percentile", 0), 2),
                "range_width": round(summary_stats.get("range_5_95", 0), 2),
            },
            "risk_assessment": {
                "level": risk_metrics.get("risk_level", "UNKNOWN"),
                "value_at_risk_95": round(risk_metrics.get("value_at_risk_95", 0), 2),
                "prob_significant_increase": round(risk_metrics.get("probability_exceed_threshold", 0) * 100, 1),
                "prob_significant_decrease": round(risk_metrics.get("probability_below_threshold", 0) * 100, 1),
            },
            "recommendations": self._generate_simulation_recommendations(result),
        }
    
    def _generate_simulation_recommendations(self, result: SimulationResult) -> List[str]:
        """Generate actionable recommendations from simulation"""
        
        recommendations = []
        risk_level = result.risk_metrics.get("risk_level")
        change_pct = ((result.summary_statistics.get("final_mean", 0) - result.base_case_path[0]) 
                     / result.base_case_path[0] * 100) if result.base_case_path[0] != 0 else 0
        
        if risk_level == "CRITICAL":
            recommendations.append(
                "🔴 CRITICAL RISK: High volatility detected. Implement immediate mitigation measures."
            )
        
        if change_pct > 20:
            recommendations.append(
                f"⚠️ Projected increase of {change_pct:.1f}% - Accelerate emissions reduction initiatives"
            )
        elif change_pct < -20:
            recommendations.append(
                f"✅ Projected reduction of {abs(change_pct):.1f}% - Maintain current trajectory and document success"
            )
        
        prob_exceed = result.risk_metrics.get("probability_exceed_threshold", 0)
        if prob_exceed > 0.4:
            recommendations.append(
                f"High probability ({prob_exceed*100:.0f}%) of exceeding baseline - Review operational constraints"
            )
        
        if not recommendations:
            recommendations.append(
                "✅ Simulation indicates stable trajectory - Continue monitoring"
            )
        
        return recommendations
    
    def _store_simulation_result(self, db: Session, result: SimulationResult) -> None:
        """Store simulation result in database"""
        try:
            from services.database_service import DatabaseService
            
            # Store the base case forecast as prediction
            DatabaseService.store_prediction(
                db=db,
                prediction_type="simulation_monte_carlo",
                predicted_value=result.base_case_path[-1] if result.base_case_path else 0,
                confidence_score=0.95,
                prediction_result={
                    "scenario_name": result.scenario_name,
                    "num_simulations": result.num_simulations,
                    "num_months": result.num_months,
                    "base_case_path": result.base_case_path,
                    "best_case_path": result.best_case_path,
                    "worst_case_path": result.worst_case_path,
                    "summary_statistics": result.summary_statistics,
                    "risk_metrics": result.risk_metrics
                }
            )
        except Exception as e:
            print(f"Database storage error in simulation: {str(e)}")
