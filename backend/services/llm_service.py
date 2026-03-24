"""
LLM Service with Gemini (primary) and OpenAI (fallback).
Generates AI insights using real LLM APIs.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# API Keys
GEMINI_API_KEY = "AIzaSyBr2AaDxwo5-s4niA-CxNY-H3m_m7ORXpA"
OPENAI_API_KEY = "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"

# Try importing both libraries
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("⚠️ google-generativeai not installed")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("⚠️ openai not installed")


def init_gemini() -> Optional[Any]:
    """Initialize Gemini model."""
    if not GEMINI_AVAILABLE:
        return None
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        logger.info("✅ Gemini initialized")
        return model
    except Exception as e:
        logger.error(f"❌ Gemini init failed: {e}")
        return None


def init_openai() -> Optional[Any]:
    """Initialize OpenAI client."""
    if not OPENAI_AVAILABLE:
        return None
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("✅ OpenAI initialized")
        return client
    except Exception as e:
        logger.error(f"❌ OpenAI init failed: {e}")
        return None


# Initialize clients
gemini_model = init_gemini()
openai_client = init_openai()


def create_insights_prompt(emission_data: dict, suggestions: list, history: list, forecast: list) -> str:
    """Create prompt for AI insights generation."""
    total_co2 = emission_data.get("total_co2", 0)
    carbon_score = emission_data.get("carbon_score", "Unknown")
    carbon_score_value = emission_data.get("carbon_score_value", 0)
    
    breakdown = emission_data.get("breakdown", {})
    breakdown_pct = emission_data.get("breakdown_percentage", {})
    
    prompt = f"""You are an expert Carbon Footprint Analyst AI. Analyze the following MSME emission data and provide comprehensive insights.

## EMISSION DATA
- Total CO₂ Emissions: {total_co2:.2f} kg
- Carbon Score: {carbon_score} ({carbon_score_value}/100)
- Electricity CO₂: {breakdown.get('electricity_co2', 0):.2f} kg ({breakdown_pct.get('electricity', 0):.1f}%)
- Fuel CO₂: {breakdown.get('fuel_co2', 0):.2f} kg ({breakdown_pct.get('fuel', 0):.1f}%)

## AI SUGGESTIONS ({len(suggestions)} items)
"""
    for i, s in enumerate(suggestions[:5], 1):
        prompt += f"{i}. {s.get('title', 'N/A')} - Impact: {s.get('impact', 'N/A')}, Priority: {s.get('priority', 'N/A')}\n"
    
    if history:
        prompt += f"\n## HISTORICAL DATA ({len(history)} records)\n"
        for h in history[-3:]:
            prompt += f"- {h.get('date', 'N/A')}: {h.get('total_co2', 0):.2f} kg CO₂\n"
    
    if forecast:
        prompt += f"\n## FORECAST (next {len(forecast)} months)\n"
        prompt += f"Predicted emissions: {', '.join([f'{f:.1f}' for f in forecast])} kg\n"
    
    prompt += """
## REQUIRED OUTPUT FORMAT (JSON)
{
    "insights": [
        {
            "model": "Emissions Predictor (Model 1)",
            "type": "analysis",
            "title": "...",
            "content": "...",
            "priority": "high/medium/low"
        },
        {
            "model": "Carbon Scorer (Model 2)",
            "type": "score",
            "title": "...",
            "content": "...",
            "action": "...",
            "priority": "high/medium/low"
        },
        {
            "model": "Trend Forecaster (Model 3)",
            "type": "trend/forecast",
            "title": "...",
            "content": "...",
            "priority": "high/medium/low"
        }
    ],
    "improvements": [
        {
            "category": "Electricity/Fuel/Quick Wins/AI Recommended",
            "recommendation": "...",
            "potential_savings": "X%",
            "roi": "..."
        }
    ],
    "summary": {
        "total_emissions": <number>,
        "carbon_score": "...",
        "score_value": <number>,
        "dominant_source": "electricity/fuel",
        "improvement_potential": "X%",
        "priority_level": "Critical/High/Medium/Low"
    }
}

Generate exactly 3-4 insights (one from each model perspective), 3-4 improvement recommendations, and a summary. Be specific, actionable, and use actual numbers from the data."""
    
    return prompt


def parse_llm_response(response_text: str) -> Optional[Dict]:
    """Parse JSON from LLM response."""
    try:
        # Try to find JSON in the response
        # First, try direct JSON parsing
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown code blocks
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        # Try to find any JSON-like structure
        json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        return None
    except Exception as e:
        logger.error(f"Failed to parse LLM response: {e}")
        return None


def generate_insights_with_gemini(emission_data: dict, suggestions: list, history: list, forecast: list) -> Optional[Dict]:
    """Generate insights using Gemini API."""
    if not gemini_model:
        logger.warning("Gemini not available")
        return None
    
    try:
        prompt = create_insights_prompt(emission_data, suggestions, history, forecast)
        
        response = gemini_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=2048,
            )
        )
        
        result = parse_llm_response(response.text)
        if result:
            logger.info("✅ Gemini insights generated successfully")
            result["model_used"] = "gemini-2.0-flash"
            return result
        return None
    except Exception as e:
        logger.error(f"❌ Gemini generation failed: {e}")
        return None


def generate_insights_with_openai(emission_data: dict, suggestions: list, history: list, forecast: list) -> Optional[Dict]:
    """Generate insights using OpenAI API."""
    if not openai_client:
        logger.warning("OpenAI not available")
        return None
    
    try:
        prompt = create_insights_prompt(emission_data, suggestions, history, forecast)
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert Carbon Footprint Analyst AI. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2048,
            response_format={"type": "json_object"}
        )
        
        result = parse_llm_response(response.choices[0].message.content)
        if result:
            logger.info("✅ OpenAI insights generated successfully")
            result["model_used"] = "gpt-4o-mini"
            return result
        return None
    except Exception as e:
        logger.error(f"❌ OpenAI generation failed: {e}")
        return None


def generate_ai_insights_with_fallback(emission_data: dict, suggestions: list, history: list, forecast: list) -> Dict:
    """
    Generate AI insights with Gemini as primary and OpenAI as fallback.
    Returns structured insights from LLM or falls back to rule-based generation.
    """
    # Try Gemini first
    result = generate_insights_with_gemini(emission_data, suggestions, history, forecast)
    if result:
        return {**result, "api_used": "gemini", "fallback": False}
    
    logger.warning("⚠️ Gemini failed, trying OpenAI fallback...")
    
    # Fallback to OpenAI
    result = generate_insights_with_openai(emission_data, suggestions, history, forecast)
    if result:
        return {**result, "api_used": "openai", "fallback": True}
    
    logger.error("❌ Both APIs failed, using rule-based fallback")
    
    # Return error structure - the reports.py endpoint will handle this
    return {
        "success": False,
        "error": "Both Gemini and OpenAI APIs failed",
        "insights": [],
        "improvements": [],
        "summary": {},
        "api_used": "none",
        "fallback": True
    }


# Backward compatibility alias
get_llm_insights = generate_ai_insights_with_fallback
