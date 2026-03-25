"""
Advanced Reports Service
========================
Generate comprehensive emissions reports with visualizations and insights
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Advanced report generation"""
    
    def generate_executive_summary(
        self,
        data: Dict,
        period: str = "monthly"
    ) -> Dict:
        """
        Generate executive summary report
        
        Args:
            data: Emissions data
            period: Report period
        
        Returns:
            Executive summary dictionary
        """
        try:
            total_emissions = data.get("total_emissions", 0)
            baseline = data.get("baseline", total_emissions)
            trend = data.get("trend", "stable")
            
            # Calculate metrics
            variance_pct = ((total_emissions - baseline) / baseline * 100) if baseline > 0 else 0
            target_pct = data.get("target_pct", 10)  # 10% reduction target
            progress = min(100, max(0, (-variance_pct / target_pct * 100))) if target_pct > 0 else 0
            
            return {
                "report_type": "executive_summary",
                "period": period,
                "generated_at": datetime.now().isoformat(),
                "key_metrics": {
                    "total_emissions": total_emissions,
                    "baseline": baseline,
                    "variance": total_emissions - baseline,
                    "variance_pct": round(variance_pct, 2),
                    "trend": trend,
                    "reduction_target_pct": target_pct,
                    "progress_toward_target": round(progress, 2)
                },
                "status": self._get_status(variance_pct),
                "recommendations": self._generate_recommendations(variance_pct, trend),
                "next_actions": self._generate_actions(progress)
            }
        except Exception as e:
            logger.error(f"Executive summary generation failed: {e}")
            return {"error": str(e)}
    
    def generate_detailed_analysis(
        self,
        historical_data: List[float],
        categories: Dict[str, List[float]],
        period_days: int = 30
    ) -> Dict:
        """
        Generate detailed analysis report
        
        Args:
            historical_data: Historical emissions
            categories: Breakdown by source (electricity, fuel, etc)
            period_days: Analysis period
        
        Returns:
            Detailed analysis
        """
        try:
            total = sum(historical_data) if historical_data else 0
            avg = total / len(historical_data) if historical_data else 0
            peak = max(historical_data) if historical_data else 0
            min_val = min(historical_data) if historical_data else 0
            
            # Category analysis
            category_breakdown = {}
            for cat_name, cat_data in categories.items():
                cat_total = sum(cat_data) if cat_data else 0
                category_breakdown[cat_name] = {
                    "total": cat_total,
                    "percentage": (cat_total / total * 100) if total > 0 else 0,
                    "average": (cat_total / len(cat_data)) if cat_data else 0,
                    "peak": max(cat_data) if cat_data else 0
                }
            
            # Trend analysis
            first_half = historical_data[:len(historical_data)//2]
            second_half = historical_data[len(historical_data)//2:]
            first_avg = sum(first_half) / len(first_half) if first_half else 0
            second_avg = sum(second_half) / len(second_half) if second_half else 0
            trend_direction = "increasing" if second_avg > first_avg else ("decreasing" if second_avg < first_avg else "stable")
            trend_magnitude = (second_avg - first_avg) / first_avg * 100 if first_avg > 0 else 0
            
            return {
                "report_type": "detailed_analysis",
                "period_days": period_days,
                "generated_at": datetime.now().isoformat(),
                "overall_statistics": {
                    "total_emissions": round(total, 2),
                    "average_daily": round(avg, 2),
                    "peak_value": round(peak, 2),
                    "min_value": round(min_val, 2),
                    "std_deviation": round(self._calculate_std_dev(historical_data), 2)
                },
                "category_breakdown": category_breakdown,
                "trend_analysis": {
                    "direction": trend_direction,
                    "magnitude_pct": round(trend_magnitude, 2),
                    "first_period_avg": round(first_avg, 2),
                    "second_period_avg": round(second_avg, 2)
                },
                "key_insights": self._extract_insights(historical_data, category_breakdown, trend_direction)
            }
        except Exception as e:
            logger.error(f"Detailed analysis generation failed: {e}")
            return {"error": str(e)}
    
    def generate_comparative_report(
        self,
        current_period: float,
        previous_period: float,
        industry_average: float,
        your_percentile: float
    ) -> Dict:
        """
        Generate comparative analysis
        
        Args:
            current_period: Current emissions
            previous_period: Previous period emissions
            industry_average: Industry benchmark
            your_percentile: Your percentile ranking
        
        Returns:
            Comparative analysis
        """
        try:
            period_change = current_period - previous_period
            period_change_pct = (period_change / previous_period * 100) if previous_period > 0 else 0
            vs_industry = current_period - industry_average
            vs_industry_pct = (vs_industry / industry_average * 100) if industry_average > 0 else 0
            
            return {
                "report_type": "comparative",
                "generated_at": datetime.now().isoformat(),
                "period_over_period": {
                    "current": round(current_period, 2),
                    "previous": round(previous_period, 2),
                    "change": round(period_change, 2),
                    "change_pct": round(period_change_pct, 2),
                    "status": "improved" if period_change < 0 else "worsened"
                },
                "vs_industry": {
                    "your_emissions": round(current_period, 2),
                    "industry_average": round(industry_average, 2),
                    "difference": round(vs_industry, 2),
                    "difference_pct": round(vs_industry_pct, 2),
                    "status": "below_average" if current_period < industry_average else "above_average",
                    "percentile_rank": round(your_percentile, 1),
                    "interpretation": f"Better than {100 - your_percentile:.0f}% of industry" if your_percentile > 50 else f"Worse than {your_percentile:.0f}% of industry"
                },
                "performance_rating": self._get_performance_rating(
                    period_change_pct,
                    vs_industry_pct
                ),
                "recommendations": self._get_comparative_recommendations(
                    period_change_pct,
                    vs_industry_pct,
                    your_percentile
                )
            }
        except Exception as e:
            logger.error(f"Comparative report generation failed: {e}")
            return {"error": str(e)}
    
    def generate_forecast_report(
        self,
        forecast_data: Dict,
        current_value: float
    ) -> Dict:
        """
        Generate forecast-based report
        
        Args:
            forecast_data: Forecast results
            current_value: Current emissions
        
        Returns:
            Forecast report
        """
        try:
            forecast_list = forecast_data.get("forecast", [])
            lower_bound = forecast_data.get("lower_bound", [])
            upper_bound = forecast_data.get("upper_bound", [])
            
            if not forecast_list:
                return {"error": "No forecast data"}
            
            forecast_change = forecast_list[-1] - current_value if forecast_list else 0
            trend = forecast_data.get("trend", "unknown")
            
            # 90-day projection
            projection_3m = sum(forecast_list[:min(3, len(forecast_list))]) / min(3, len(forecast_list))
            
            return {
                "report_type": "forecast",
                "generated_at": datetime.now().isoformat(),
                "current_value": round(current_value, 2),
                "forecast_summary": {
                    "periods_ahead": len(forecast_list),
                    "forecast_trend": trend,
                    "final_forecast": round(forecast_list[-1], 2) if forecast_list else 0,
                    "total_change": round(forecast_change, 2),
                    "change_pct": round((forecast_change / current_value * 100), 2) if current_value > 0 else 0
                },
                "confidence_intervals": {
                    "method": "95% CI",
                    "lower_bound_min": round(min(lower_bound), 2) if lower_bound else 0,
                    "upper_bound_max": round(max(upper_bound), 2) if upper_bound else 0
                },
                "projections": {
                    "3_month_average": round(projection_3m, 2),
                    "best_case": round(min(lower_bound), 2) if lower_bound else 0,
                    "worst_case": round(max(upper_bound), 2) if upper_bound else 0
                },
                "risk_assessment": self._assess_forecast_risk(forecast_list, current_value),
                "action_items": self._forecast_action_items(trend, forecast_change, current_value)
            }
        except Exception as e:
            logger.error(f"Forecast report generation failed: {e}")
            return {"error": str(e)}
    
    def generate_full_report(
        self,
        data: Dict,
        db: Session = None
    ) -> Dict:
        """
        Generate comprehensive full report
        
        Args:
            data: All required data
        
        Returns:
            Complete report bundle
        """
        try:
            report = {
                "report_id": f"report_{int(datetime.now().timestamp())}",
                "generated_at": datetime.now().isoformat(),
                "report_type": "comprehensive",
                "executive_summary": self.generate_executive_summary(data),
                "detailed_analysis": self.generate_detailed_analysis(
                    data.get("historical", []),
                    data.get("categories", {})
                ),
                "comparative": self.generate_comparative_report(
                    data.get("current", 0),
                    data.get("previous", 0),
                    data.get("industry_avg", 0),
                    data.get("percentile", 50)
                ),
                "forecast": self.generate_forecast_report(
                    data.get("forecast", {}),
                    data.get("current", 0)
                ),
                "summary": {
                    "pages": 4,
                    "sections": [
                        "Executive Summary",
                        "Detailed Analysis",
                        "Comparative Performance",
                        "Future Projections"
                    ]
                }
            }
            
            # Store in database if session provided
            if db:
                self._store_report(db, report)
            
            return report
        except Exception as e:
            logger.error(f"Full report generation failed: {e}")
            return {"error": str(e)}
    
    def _store_report(self, db: Session, report: Dict) -> None:
        """Store report in database"""
        try:
            from services.database_service import DatabaseService
            
            DatabaseService.store_report(
                db=db,
                report_type=report.get("report_type", "comprehensive"),
                report_content=report,
                period_start=report.get("generated_at"),
                period_end=report.get("generated_at")
            )
        except Exception as e:
            logger.error(f"Database storage error in report generation: {str(e)}")
    
    # Helper methods
    
    def _get_status(self, variance_pct: float) -> str:
        """Get status based on variance"""
        if variance_pct < -10:
            return "excellent"
        elif variance_pct < 0:
            return "good"
        elif variance_pct < 10:
            return "acceptable"
        elif variance_pct < 20:
            return "warning"
        else:
            return "critical"
    
    def _generate_recommendations(self, variance_pct: float, trend: str) -> List[str]:
        """Generate recommendations"""
        recs = []
        if variance_pct > 15:
            recs.append("Implement immediate emissions reduction measures")
        if trend == "increasing":
            recs.append("Current trend is increasing - investigate root causes")
        if variance_pct < 0:
            recs.append("Excellent performance - maintain current practices")
        return recs
    
    def _generate_actions(self, progress: float) -> List[str]:
        """Generate action items"""
        if progress >= 100:
            return ["Set new reduction targets"]
        elif progress > 50:
            return ["Continue current initiatives", "Monitor progress"]
        elif progress > 0:
            return ["Accelerate reduction efforts", "Review mitigation strategies"]
        else:
            return ["Urgent: Launch emissions reduction program"]
    
    def _calculate_std_dev(self, data: List[float]) -> float:
        """Calculate standard deviation"""
        if not data or len(data) < 2:
            return 0
        mean = sum(data) / len(data)
        variance = sum((x - mean) ** 2 for x in data) / len(data)
        return variance ** 0.5
    
    def _extract_insights(self, data: List[float], categories: Dict, trend: str) -> List[str]:
        """Extract key insights"""
        insights = []
        if trend == "decreasing":
            insights.append("Positive trend: emissions are decreasing")
        
        # Find largest category
        if categories:
            largest = max(categories.items(), key=lambda x: x[1]["percentage"])
            insights.append(f"Largest contributor: {largest[0]} ({largest[1]['percentage']:.1f}%)")
        
        return insights
    
    def _get_performance_rating(self, period_change_pct: float, vs_industry_pct: float) -> str:
        """Get performance rating"""
        if period_change_pct < -10 and vs_industry_pct < -20:
            return "Excellent"
        elif period_change_pct < 0 and vs_industry_pct < 0:
            return "Good"
        elif period_change_pct > 0 and vs_industry_pct > 0:
            return "Needs Improvement"
        else:
            return "Fair"
    
    def _get_comparative_recommendations(self, period_change_pct: float, vs_industry_pct: float, percentile: float) -> List[str]:
        """Generate comparative recommendations"""
        recs = []
        if period_change_pct > 0:
            recs.append("Focus on reversing recent increase in emissions")
        if vs_industry_pct > 20:
            recs.append("Benchmark against industry leaders for best practices")
        if percentile < 40:
            recs.append("Priority: Meet industry standards")
        return recs
    
    def _assess_forecast_risk(self, forecast: List[float], current: float) -> str:
        """Assess forecast risk"""
        if not forecast:
            return "unknown"
        max_forecast = max(forecast)
        if max_forecast > current * 1.5:
            return "high"
        elif max_forecast > current * 1.2:
            return "medium"
        else:
            return "low"
    
    def _forecast_action_items(self, trend: str, change: float, current: float) -> List[str]:
        """Generate forecast action items"""
        items = []
        if trend == "increasing":
            items.append("Prepare mitigation strategies for increasing emissions")
        elif trend == "decreasing":
            items.append("Continue successful reduction initiatives")
        return items


# Global instance
report_generator = ReportGenerator()


def generate_executive_summary(data: Dict, period: str = "monthly") -> Dict:
    """Generate executive summary"""
    return report_generator.generate_executive_summary(data, period)


def generate_full_report(data: Dict) -> Dict:
    """Generate complete report"""
    return report_generator.generate_full_report(data)
