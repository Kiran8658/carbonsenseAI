"""
Benchmark Service - Compare against industry standards & peers
Provides industry averages, regional data, and peer rankings
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class BenchmarkCategory(Enum):
    CARBON_FOOTPRINT = "carbon_footprint"
    ESG_SCORE = "esg_score"
    COST_SAVINGS = "cost_savings"
    RENEWABLE_ADOPTION = "renewable_adoption"


@dataclass
class BenchmarkData:
    your_value: float
    industry_average: float
    industry_percentile: float
    regional_average: float
    regional_percentile: float
    best_in_class: float
    worst_in_class: float
    performance_rating: str  # "Excellent", "Above Average", "Average", "Below Average", "Poor"
    gap_to_average: float  # positive = better, negative = worse
    gap_to_best: float


class BenchmarkService:
    """Provide benchmark comparisons for carbon & ESG metrics"""
    
    # Industry benchmarks (simplified data - in production would be from database)
    INDUSTRY_BENCHMARKS = {
        "retail": {
            "carbon_footprint": {"avg": 850, "min": 200, "max": 2500, "p75": 1200, "p90": 1800},
            "esg_score": {"avg": 58, "min": 20, "max": 95, "p75": 72, "p90": 85},
            "cost_savings": {"avg": 12000, "min": 0, "max": 150000, "p75": 25000, "p90": 80000},
            "renewable_adoption": {"avg": 15, "min": 0, "max": 100, "p75": 35, "p90": 60},
        },
        "manufacturing": {
            "carbon_footprint": {"avg": 3500, "min": 500, "max": 15000, "p75": 5500, "p90": 10000},
            "esg_score": {"avg": 52, "min": 15, "max": 90, "p75": 65, "p90": 80},
            "cost_savings": {"avg": 45000, "min": 5000, "max": 500000, "p75": 100000, "p90": 300000},
            "renewable_adoption": {"avg": 10, "min": 0, "max": 100, "p75": 25, "p90": 50},
        },
        "tech": {
            "carbon_footprint": {"avg": 150, "min": 20, "max": 800, "p75": 250, "p90": 500},
            "esg_score": {"avg": 72, "min": 40, "max": 98, "p75": 82, "p90": 92},
            "cost_savings": {"avg": 8000, "min": 1000, "max": 50000, "p75": 15000, "p90": 35000},
            "renewable_adoption": {"avg": 45, "min": 5, "max": 100, "p75": 70, "p90": 95},
        },
        "energy": {
            "carbon_footprint": {"avg": 8000, "min": 2000, "max": 50000, "p75": 12000, "p90": 35000},
            "esg_score": {"avg": 48, "min": 10, "max": 85, "p75": 58, "p90": 75},
            "cost_savings": {"avg": 120000, "min": 20000, "max": 2000000, "p75": 300000, "p90": 1000000},
            "renewable_adoption": {"avg": 5, "min": 0, "max": 100, "p75": 15, "p90": 40},
        },
        "finance": {
            "carbon_footprint": {"avg": 200, "min": 30, "max": 1200, "p75": 400, "p90": 750},
            "esg_score": {"avg": 65, "min": 30, "max": 95, "p75": 78, "p90": 88},
            "cost_savings": {"avg": 15000, "min": 2000, "max": 100000, "p75": 30000, "p90": 60000},
            "renewable_adoption": {"avg": 20, "min": 0, "max": "100", "p75": 40, "p90": 70},
        },
    }
    
    # Regional averages (simplified)
    REGIONAL_BENCHMARKS = {
        "north_america": {"multiplier": 1.0, "label": "North America"},
        "europe": {"multiplier": 0.85, "label": "Europe"},
        "asia": {"multiplier": 1.3, "label": "Asia"},
        "global": {"multiplier": 1.0, "label": "Global"},
    }
    
    def get_benchmark(
        self,
        value: float,
        category: BenchmarkCategory,
        industry: str,
        region: str = "global"
    ) -> BenchmarkData:
        """
        Get benchmark comparison for a given value
        
        Args:
            value: The metric value to benchmark
            category: Type of metric (carbon, ESG, savings, etc.)
            industry: Industry sector
            region: Geographic region
        
        Returns:
            BenchmarkData with percentiles and comparisons
        """
        
        industry = industry.lower()
        region = region.lower()
        category_key = category.value
        
        # Get industry benchmark data
        industry_data = self.INDUSTRY_BENCHMARKS.get(
            industry, 
            self.INDUSTRY_BENCHMARKS["retail"]  # Default to retail
        )
        
        metric_data = industry_data.get(category_key, {})
        
        if not metric_data:
            raise ValueError(f"No benchmark data for {category_key}")
        
        # Calculate regional adjustment
        regional_mult = self.REGIONAL_BENCHMARKS.get(region, {"multiplier": 1.0})["multiplier"]
        industry_avg = metric_data["avg"] * regional_mult
        
        # Calculate percentiles
        industry_percentile = self._calculate_percentile(
            value, metric_data["min"], metric_data["max"], metric_data["p75"], metric_data["p90"]
        )
        
        regional_avg_adjusted = industry_avg
        regional_percentile = industry_percentile  # Simplified for this demo
        
        # Calculate gaps
        gap_to_average = value - industry_avg
        gap_to_best = value - metric_data["max"]
        
        # Determine performance rating
        performance = self._rate_performance(industry_percentile)
        
        return BenchmarkData(
            your_value=round(value, 2),
            industry_average=round(industry_avg, 2),
            industry_percentile=round(industry_percentile, 1),
            regional_average=round(regional_avg_adjusted, 2),
            regional_percentile=round(regional_percentile, 1),
            best_in_class=metric_data["max"],
            worst_in_class=metric_data["min"],
            performance_rating=performance,
            gap_to_average=round(gap_to_average, 2),
            gap_to_best=round(gap_to_best, 2),
        )
    
    def _calculate_percentile(self, value: float, min_v: float, max_v: float, p75: float, p90: float) -> float:
        """Calculate percentile for a value"""
        if value >= p90:
            return 95.0
        elif value >= p75:
            return 80.0
        elif value >= (min_v + max_v) / 2:
            return 50.0
        else:
            return 25.0
    
    def _rate_performance(self, percentile: float) -> str:
        """Convert percentile to performance rating"""
        if percentile >= 90:
            return "Excellent"
        elif percentile >= 75:
            return "Above Average"
        elif percentile >= 50:
            return "Average"
        elif percentile >= 25:
            return "Below Average"
        else:
            return "Poor"
    
    def get_peer_group(
        self,
        your_value: float,
        category: BenchmarkCategory,
        industry: str,
        region: str = "global"
    ) -> Dict[str, Any]:
        """Get peer group analysis"""
        
        benchmark = self.get_benchmark(value=your_value, category=category, industry=industry, region=region)
        
        return {
            "peer_group": f"{industry.title()} - {region.title()}",
            "your_ranking": f"Top {benchmark.industry_percentile:.0f}%",
            "performance": benchmark.performance_rating,
            "comparison": {
                "your_value": benchmark.your_value,
                "industry_average": benchmark.industry_average,
                "best_performer": benchmark.best_in_class,
                "worst_performer": benchmark.worst_in_class,
            },
            "improvement_potential": {
                "to_reach_average": round(benchmark.gap_to_average, 2) if benchmark.gap_to_average < 0 else 0,
                "to_reach_top_quartile": round(abs(benchmark.gap_to_best) * 0.75, 2),
            }
        }
    
    def get_industry_summary(self, industry: str) -> Dict[str, Any]:
        """Get summary stats for an industry"""
        
        industry = industry.lower()
        industry_data = self.INDUSTRY_BENCHMARKS.get(industry, self.INDUSTRY_BENCHMARKS["retail"])
        
        return {
            "industry": industry.title(),
            "metrics": {
                "carbon_footprint": {
                    "average_kg": industry_data["carbon_footprint"]["avg"],
                    "range": f"{industry_data['carbon_footprint']['min']}-{industry_data['carbon_footprint']['max']} kg",
                    "top_quartile": industry_data["carbon_footprint"]["p75"],
                },
                "esg_score": {
                    "average": industry_data["esg_score"]["avg"],
                    "range": f"{industry_data['esg_score']['min']}-{industry_data['esg_score']['max']}",
                    "top_quartile": industry_data["esg_score"]["p75"],
                },
                "renewable_adoption": {
                    "average_percent": industry_data["renewable_adoption"]["avg"],
                    "range": f"{industry_data['renewable_adoption']['min']}-{industry_data['renewable_adoption']['max']}%",
                    "top_quartile": industry_data["renewable_adoption"]["p75"],
                },
            },
            "regional_variations": [
                {"region": "North America", "multiplier": 1.0},
                {"region": "Europe", "multiplier": 0.85},
                {"region": "Asia", "multiplier": 1.3},
            ]
        }
    
    def compare_industries(self, value: float, category: BenchmarkCategory) -> List[Dict[str, Any]]:
        """Compare a value across all industries"""
        
        results = []
        category_key = category.value
        
        for industry, data in self.INDUSTRY_BENCHMARKS.items():
            metric = data.get(category_key, {})
            if metric:
                percentile = self._calculate_percentile(
                    value, metric["min"], metric["max"], metric["p75"], metric["p90"]
                )
                results.append({
                    "industry": industry.title(),
                    "industry_average": metric["avg"],
                    "your_percentile": percentile,
                    "performance": self._rate_performance(percentile),
                    "gap_to_average": round(value - metric["avg"], 2),
                })
        
        return sorted(results, key=lambda x: x["your_percentile"], reverse=True)
