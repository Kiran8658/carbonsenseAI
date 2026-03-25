"""
ESG (Environmental, Social, Governance) Scoring Module
Calculates comprehensive ESG scores for organizations
"""

from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum


class ESGCategory(Enum):
    ENVIRONMENTAL = "environmental"
    SOCIAL = "social"
    GOVERNANCE = "governance"


@dataclass
class ESGScore:
    environmental_score: float  # 0-100
    social_score: float  # 0-100
    governance_score: float  # 0-100
    overall_score: float  # 0-100 (weighted average)
    grade: str  # A+, A, B+, B, C+, C, D, F
    recommendations: list


class ESGScoringService:
    """Calculate ESG scores based on organizational metrics"""
    
    def __init__(self):
        self.weights = {
            ESGCategory.ENVIRONMENTAL: 0.5,  # 50% - carbon focus
            ESGCategory.SOCIAL: 0.3,  # 30%
            ESGCategory.GOVERNANCE: 0.2,  # 20%
        }
    
    def calculate_esg_score(self, data: Dict[str, Any]) -> ESGScore:
        """
        Calculate ESG score from organizational data
        
        Args:
            data: Dictionary containing ESG metrics
                - co2_kg: Total CO2 emissions (kg)
                - annual_savings_reduction: % reduction target
                - employees: Number of employees
                - renewable_usage_pct: % renewable energy
                - carbon_offset_tons: Carbon offset purchased (tons)
                - certified_emissions_plan: Boolean
                - esg_report_published: Boolean
                - third_party_audit: Boolean
        
        Returns:
            ESGScore object with comprehensive scoring
        """
        
        # Calculate E (Environmental) score
        e_score = self._calculate_environmental_score(data)
        
        # Calculate S (Social) score
        s_score = self._calculate_social_score(data)
        
        # Calculate G (Governance) score
        g_score = self._calculate_governance_score(data)
        
        # Calculate weighted overall score
        overall = (
            e_score * self.weights[ESGCategory.ENVIRONMENTAL] +
            s_score * self.weights[ESGCategory.SOCIAL] +
            g_score * self.weights[ESGCategory.GOVERNANCE]
        )
        
        # Normalize to 0-100
        overall = max(0, min(100, overall))
        
        # Generate grade
        grade = self._score_to_grade(overall)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(e_score, s_score, g_score, data)
        
        return ESGScore(
            environmental_score=round(e_score, 2),
            social_score=round(s_score, 2),
            governance_score=round(g_score, 2),
            overall_score=round(overall, 2),
            grade=grade,
            recommendations=recommendations
        )
    
    def _calculate_environmental_score(self, data: Dict[str, Any]) -> float:
        """Score environmental performance (50% weight in overall)"""
        score = 50.0  # Start at baseline
        
        # Emissions reduction (max +30 points)
        co2_kg = data.get('co2_kg', 1000)
        if co2_kg < 500:
            score += 30
        elif co2_kg < 1000:
            score += 20
        elif co2_kg < 2000:
            score += 10
        
        # Renewable energy usage (max +15 points)
        renewable = data.get('renewable_usage_pct', 0)
        score += (renewable / 100) * 15
        
        # Carbon offset (max +10 points)
        offset = data.get('carbon_offset_tons', 0)
        score += min(10, offset / 10)
        
        # Reduction commitment (max +5 points)
        if data.get('annual_savings_reduction', 0) > 0:
            score += 5
        
        return min(100, score)
    
    def _calculate_social_score(self, data: Dict[str, Any]) -> float:
        """Score social responsibility performance"""
        score = 50.0  # Start at baseline
        
        # Employee count (larger = better for scale)
        employees = data.get('employees', 10)
        if employees >= 100:
            score += 15
        elif employees >= 50:
            score += 10
        elif employees >= 20:
            score += 5
        
        # ESG commitment (if stated)
        if data.get('sustainability_commitment'):
            score += 15
        
        # Community engagement
        if data.get('community_programs'):
            score += 10
        
        # Diversity & inclusion programs
        if data.get('dei_programs'):
            score += 10
        
        return min(100, score)
    
    def _calculate_governance_score(self, data: Dict[str, Any]) -> float:
        """Score governance & compliance"""
        score = 50.0  # Start at baseline
        
        # Certified emissions plan (max +20 points)
        if data.get('certified_emissions_plan'):
            score += 20
        
        # ESG report published (max +20 points)
        if data.get('esg_report_published'):
            score += 20
        
        # Third-party audit (max +15 points)
        if data.get('third_party_audit'):
            score += 15
        
        # Data transparency
        if data.get('data_transparency'):
            score += 10
        
        return min(100, score)
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "B+"
        elif score >= 80:
            return "B"
        elif score >= 75:
            return "C+"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _generate_recommendations(
        self, e_score: float, s_score: float, g_score: float, data: Dict[str, Any]
    ) -> list:
        """Generate actionable recommendations based on scores"""
        recommendations = []
        
        # Environmental recommendations
        if e_score < 70:
            recommendations.append({
                "category": "Environmental",
                "priority": "HIGH",
                "action": "Increase renewable energy adoption or offset carbon emissions",
                "impact": "Reduce carbon footprint by 10-30%"
            })
        
        if data.get('renewable_usage_pct', 0) < 50:
            recommendations.append({
                "category": "Environmental",
                "priority": "MEDIUM",
                "action": "Transition to renewable energy sources",
                "impact": "Improve environmental score by 15+"
            })
        
        # Social recommendations
        if s_score < 65:
            recommendations.append({
                "category": "Social",
                "priority": "MEDIUM",
                "action": "Establish sustainability commitment & community programs",
                "impact": "Enhance social responsibility score"
            })
        
        # Governance recommendations
        if not data.get('esg_report_published'):
            recommendations.append({
                "category": "Governance",
                "priority": "MEDIUM",
                "action": "Publish annual ESG report",
                "impact": "Improve transparency & governance score"
            })
        
        if not data.get('third_party_audit'):
            recommendations.append({
                "category": "Governance",
                "priority": "LOW",
                "action": "Conduct third-party ESG audit",
                "impact": "Build credibility & gain 15+ points"
            })
        
        return recommendations
    
    def benchmark_against_industry(self, esg_score: float, industry: str) -> Dict[str, Any]:
        """
        Benchmark ESG score against industry averages
        (Simple mock data - could be extended with real benchmarks)
        """
        industry_benchmarks = {
            "retail": {"avg": 58, "high": 85},
            "manufacturing": {"avg": 52, "high": 80},
            "tech": {"avg": 72, "high": 95},
            "energy": {"avg": 48, "high": 75},
            "finance": {"avg": 65, "high": 90},
            "general": {"avg": 60, "high": 85}
        }
        
        benchmark = industry_benchmarks.get(industry.lower(), industry_benchmarks["general"])
        percentile = (esg_score - 0) / (benchmark["high"] - 0) * 100
        
        return {
            "industry": industry,
            "your_score": esg_score,
            "industry_average": benchmark["avg"],
            "industry_leader_score": benchmark["high"],
            "percentile": min(100, max(0, percentile)),
            "vs_average": esg_score - benchmark["avg"],
            "performance": "Above Average" if esg_score > benchmark["avg"] else "Below Average"
        }
