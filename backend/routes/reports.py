"""
Reports API Routes - Generate and manage PDF reports.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from services.report_service import generate_pdf_report
from services.ml_service import get_model_status
from services.llm_service import generate_ai_insights_with_fallback
from io import BytesIO
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["Reports"])

# Simple in-memory report storage (in production, use database)
REPORTS = {}
REPORT_COUNTER = 0


@router.post("/generate")
async def generate_report(payload: dict):
    """
    Generate a PDF report and return report_id (stored on server).
    Use /generate-download to get a direct blob response instead.
    """
    try:
        global REPORT_COUNTER
        
        emission_data = payload.get("emission_data", {})
        suggestions = payload.get("suggestions", [])
        summary = payload.get("summary", "")
        history = payload.get("history", [])
        forecast = payload.get("forecast", [])
        models_used = payload.get("models_used", {})
        
        if not emission_data:
            raise ValueError("emission_data is required")
        
        logger.info("📄 Generating PDF report...")
        pdf_bytes = generate_pdf_report(
            emission_data=emission_data,
            suggestions=suggestions,
            summary=summary,
            history=history,
            forecast=forecast,
            models_used=models_used,
        )
        
        REPORT_COUNTER += 1
        report_id = f"report_{REPORT_COUNTER}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        report_filename = f"{report_id}.pdf"
        report_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", report_filename)
        
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, "wb") as f:
            f.write(pdf_bytes)
        
        REPORTS[report_id] = {
            "id": report_id,
            "filename": report_filename,
            "path": report_path,
            "date": datetime.now().isoformat(),
            "co2": emission_data.get("total_co2", 0),
            "score": emission_data.get("carbon_score", "N/A"),
        }
        
        logger.info(f"✅ Report generated: {report_id}")
        
        return {
            "success": True,
            "report_id": report_id,
            "message": "Report generated successfully",
            "download_url": f"/api/reports/download/{report_id}",
        }
    
    except Exception as e:
        logger.error(f"❌ Report generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.post("/generate-download")
async def generate_and_download_report(payload: dict):
    """
    Generate a PDF report and stream it directly as a downloadable blob response.
    Frontend receives the binary PDF directly — no two-step generate+download needed.
    """
    try:
        emission_data = payload.get("emission_data", {})
        suggestions = payload.get("suggestions", [])
        summary = payload.get("summary", "")
        history = payload.get("history", []) or []
        forecast = payload.get("forecast", []) or []
        models_used = payload.get("models_used", {}) or {}
        
        if not emission_data:
            raise ValueError("emission_data is required")
        
        # Validate essential fields
        if not isinstance(emission_data, dict):
            raise ValueError("emission_data must be a dictionary")
        
        logger.info("📄 Generating PDF report for download...")
        
        # Generate PDF
        pdf_bytes = generate_pdf_report(
            emission_data=emission_data,
            suggestions=suggestions if suggestions else [],
            summary=summary if summary else "",
            history=history,
            forecast=forecast,
            models_used=models_used,
        )
        
        if not pdf_bytes or len(pdf_bytes) == 0:
            raise ValueError("PDF generation returned empty bytes")
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"CarbonSense_Report_{date_str}.pdf"
        
        logger.info(f"✅ Streaming PDF report: {filename} ({len(pdf_bytes)} bytes)")
        
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(pdf_bytes)),
                "Access-Control-Expose-Headers": "Content-Disposition, Content-Length",
                "Cache-Control": "no-cache, no-store, must-revalidate",
            },
        )
    
    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Generate-download failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


        summary = payload.get("summary", "")
        history = payload.get("history", [])
        forecast = payload.get("forecast", [])
        models_used = payload.get("models_used", {})
        
        # Validate essential data
        if not emission_data:
            raise ValueError("emission_data is required")
        
        # Generate PDF
        logger.info("📄 Generating PDF report...")
        pdf_bytes = generate_pdf_report(
            emission_data=emission_data,
            suggestions=suggestions,
            summary=summary,
            history=history,
            forecast=forecast,
            models_used=models_used,
        )
        
        # Store report
        REPORT_COUNTER += 1
        report_id = f"report_{REPORT_COUNTER}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        report_filename = f"{report_id}.pdf"
        report_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", report_filename)
        
        # Create reports directory if needed
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        # Save PDF to file
        with open(report_path, "wb") as f:
            f.write(pdf_bytes)
        
        # Store metadata
        REPORTS[report_id] = {
            "id": report_id,
            "filename": report_filename,
            "path": report_path,
            "date": datetime.now().isoformat(),
            "co2": emission_data.get("total_co2", 0),
            "score": emission_data.get("carbon_score", "N/A"),
        }
        
        logger.info(f"✅ Report generated: {report_id}")
        
        return {
            "success": True,
            "report_id": report_id,
            "message": "Report generated successfully",
            "download_url": f"/api/reports/download/{report_id}",
        }
    
    except Exception as e:
        logger.error(f"❌ Report generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("/download/{report_id}")
async def download_report(report_id: str):
    """
    Download a generated report PDF.
    """
    try:
        if report_id not in REPORTS:
            raise HTTPException(status_code=404, detail="Report not found")
        
        report_info = REPORTS[report_id]
        report_path = report_info["path"]
        
        if not os.path.exists(report_path):
            raise HTTPException(status_code=404, detail="Report file not found")
        
        logger.info(f"📥 Downloading report: {report_id}")
        
        return FileResponse(
            path=report_path,
            filename=f"CarbonSense_Report_{report_info['date'].split('T')[0]}.pdf",
            media_type="application/pdf",
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Download failed: {e}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.get("/list")
async def list_reports():
    """
    List all generated reports.
    """
    try:
        reports_list = [
            {
                "id": report_id,
                "date": report["date"],
                "co2": report["co2"],
                "score": report["score"],
                "filename": report["filename"],
                "download_url": f"/api/reports/download/{report_id}",
            }
            for report_id, report in sorted(REPORTS.items(), key=lambda x: x[1]["date"], reverse=True)
        ]
        
        return {
            "success": True,
            "reports": reports_list,
            "total": len(reports_list),
        }
    
    except Exception as e:
        logger.error(f"❌ List reports failed: {e}")
        raise HTTPException(status_code=500, detail=f"List reports failed: {str(e)}")


@router.delete("/delete/{report_id}")
async def delete_report(report_id: str):
    """
    Delete a generated report.
    """
    try:
        if report_id not in REPORTS:
            raise HTTPException(status_code=404, detail="Report not found")
        
        report_info = REPORTS[report_id]
        report_path = report_info["path"]
        
        # Delete file
        if os.path.exists(report_path):
            os.remove(report_path)
            logger.info(f"🗑️ Deleted report file: {report_path}")
        
        # Delete from memory
        del REPORTS[report_id]
        
        logger.info(f"✅ Report deleted: {report_id}")
        
        return {
            "success": True,
            "message": "Report deleted successfully",
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Delete failed: {e}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.get("/status")
async def report_status():
    """
    Get report generation status and models info.
    """
    try:
        ml_status = get_model_status()
        
        return {
            "success": True,
            "reports_generated": len(REPORTS),
            "models": ml_status,
            "ready": all(v.startswith("✅") for v in ml_status.values()),
        }
    
    except Exception as e:
        logger.error(f"❌ Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.post("/ai-insights")
async def generate_ai_insights(payload: dict):
    """
    Generate comprehensive AI insights using Gemini (primary) and OpenAI (fallback).
    
    Payload:
    {
        "emission_data": {...},
        "suggestions": [...],
        "history": [...],
        "forecast": [...]
    }
    
    Returns AI insights with analysis and improvement recommendations.
    """
    try:
        emission_data = payload.get("emission_data", {})
        suggestions = payload.get("suggestions", [])
        history = payload.get("history", [])
        forecast = payload.get("forecast", [])
        
        logger.info("🤖 Generating AI insights with LLM...")
        
        # Use LLM service with Gemini primary, OpenAI fallback
        result = generate_ai_insights_with_fallback(emission_data, suggestions, history, forecast)
        
        # Check if LLM APIs failed
        if not result.get("success", True):
            logger.warning("⚠️ LLM APIs failed, using rule-based fallback")
            # Fall back to rule-based generation
            result = generate_rule_based_insights(emission_data, suggestions, history, forecast)
        
        logger.info(f"✅ AI insights generated using: {result.get('api_used', 'rule-based')}")
        return result
        
    except Exception as e:
        logger.error(f"❌ AI insights generation failed: {e}")
        # Final fallback to rule-based
        try:
            emission_data = payload.get("emission_data", {})
            suggestions = payload.get("suggestions", [])
            history = payload.get("history", [])
            forecast = payload.get("forecast", [])
            return generate_rule_based_insights(emission_data, suggestions, history, forecast)
        except Exception as e2:
            logger.error(f"❌ Even rule-based fallback failed: {e2}")
            raise HTTPException(status_code=500, detail=f"AI insights generation failed: {str(e)}")


def generate_rule_based_insights(emission_data: dict, suggestions: list, history: list, forecast: list) -> dict:
    """Rule-based fallback for when LLM APIs fail."""
    total_co2 = emission_data.get("total_co2", 0)
    electricity_co2 = emission_data.get("electricity_co2", 0)
    fuel_co2 = emission_data.get("fuel_co2", 0)
    carbon_score = emission_data.get("carbon_score", "Unknown")
    carbon_score_value = emission_data.get("carbon_score_value", 0)
    
    insights = []
    electricity_pct = emission_data.get("breakdown_percentage", {}).get("electricity", 0)
    fuel_pct = emission_data.get("breakdown_percentage", {}).get("fuel", 0)
    
    dominant_source = "electricity" if electricity_pct > fuel_pct else "fuel"
    dominant_pct = electricity_pct if electricity_pct > fuel_pct else fuel_pct
    
    # Model 1: Emissions Analysis
    insights.append({
        "model": "Emissions Predictor (Model 1)",
        "type": "analysis",
        "title": "Emission Source Analysis",
        "content": f"Your {dominant_source} consumption contributes {dominant_pct:.1f}% of total emissions ({total_co2:.1f} kg CO₂). "
                  f"{'Electricity usage is your primary focus area for reduction.' if dominant_source == 'electricity' else 'Fuel consumption is your main emission driver.'}",
        "priority": "high"
    })
    
    # Model 2: Carbon Score Analysis
    score_actions = {
        "Excellent": ("Outstanding! Your emissions are well below MSME benchmarks.", "Maintain practices and help others reduce their footprint."),
        "Good": ("Good performance! Your emissions are below average for MSMEs.", "Small improvements can push you into excellent category."),
        "Average": ("Your emissions are at MSME average levels.", "Prioritize high-impact reduction strategies."),
        "Poor": ("Your emissions are above average. Immediate action recommended.", "Implement critical priority suggestions."),
    }
    score_message, score_action = score_actions.get(carbon_score, ("Critical emission levels detected.", "Immediate implementation essential."))
    
    insights.append({
        "model": "Carbon Scorer (Model 2)",
        "type": "score",
        "title": f"Carbon Score: {carbon_score} ({carbon_score_value}/100)",
        "content": score_message,
        "action": score_action,
        "priority": "high" if carbon_score_value < 50 else "medium"
    })
    
    # Model 3: Trend Analysis
    if history and len(history) >= 3:
        recent_trend = [h["total_co2"] for h in history[-3:]]
        trend_direction = "increasing" if recent_trend[-1] > recent_trend[0] else "decreasing" if recent_trend[-1] < recent_trend[0] else "stable"
        trend_messages = {
            "increasing": "Emissions show an upward trend over recent months. Intervention recommended.",
            "decreasing": "Positive trend! Your emissions are declining. Keep up the good work.",
            "stable": "Emissions are stable. Opportunity for reduction exists."
        }
        insights.append({
            "model": "Trend Forecaster (Model 3)",
            "type": "trend",
            "title": "Emission Trend Analysis",
            "content": trend_messages.get(trend_direction, "Trend analysis available."),
            "priority": "high" if trend_direction == "increasing" else "medium"
        })
    
    if forecast and len(forecast) > 0:
        avg_forecast = sum(forecast) / len(forecast)
        trend_pct = ((avg_forecast - total_co2) / total_co2 * 100) if total_co2 > 0 else 0
        if trend_pct > 5:
            forecast_message = f"Forecast predicts {trend_pct:.1f}% increase in coming months without intervention."
        elif trend_pct < -5:
            forecast_message = f"Forecast predicts {abs(trend_pct):.1f}% decrease if current practices continue."
        else:
            forecast_message = "Forecast shows stable emissions with minor fluctuations expected."
        
        insights.append({
            "model": "Trend Forecaster (Model 3)",
            "type": "forecast",
            "title": "Future Projection",
            "content": forecast_message,
            "priority": "medium"
        })
    
    # Improvement recommendations
    improvements = []
    if electricity_pct > 40:
        improvements.append({
            "category": "Electricity",
            "recommendation": "Switch to LED lighting and install smart power management systems",
            "potential_savings": "15-20%",
            "roi": "6-12 months payback"
        })
    
    if fuel_pct > 40:
        improvements.append({
            "category": "Fuel",
            "recommendation": "Optimize delivery routes and consider fuel-efficient vehicles or EVs",
            "potential_savings": "20-30%",
            "roi": "12-24 months payback"
        })
    
    if carbon_score_value < 70:
        improvements.append({
            "category": "Quick Wins",
            "recommendation": "Conduct energy audit and fix air leaks in compressed air systems",
            "potential_savings": "10-15%",
            "roi": "Immediate to 3 months"
        })
    
    if suggestions:
        top_suggestion = suggestions[0]
        improvements.append({
            "category": "AI Recommended",
            "recommendation": top_suggestion["title"],
            "potential_savings": f"{top_suggestion['savings_percentage']:.0f}%",
            "roi": top_suggestion["impact"]
        })
    
    summary = {
        "total_emissions": total_co2,
        "carbon_score": carbon_score,
        "score_value": carbon_score_value,
        "dominant_source": dominant_source,
        "improvement_potential": f"{sum(float(i['potential_savings'].replace('%', '')) for i in improvements if '%' in i['potential_savings']):.0f}%" if improvements else "N/A",
        "priority_level": "Critical" if carbon_score_value < 30 else "High" if carbon_score_value < 50 else "Medium" if carbon_score_value < 75 else "Low"
    }
    
    return {
        "success": True,
        "insights": insights,
        "improvements": improvements,
        "summary": summary,
        "models_used": ["Emissions Predictor", "Carbon Scorer", "Trend Forecaster"],
        "api_used": "rule-based",
        "fallback": True
    }
