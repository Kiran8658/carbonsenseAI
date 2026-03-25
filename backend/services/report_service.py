"""
Report Generation Service - Creates PDF reports with ML predictions and ROI analysis.
"""

from datetime import datetime, timedelta
from io import BytesIO
from typing import List, Dict, Tuple
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import logging

logger = logging.getLogger(__name__)

# ROI Calculation Database
SUGGESTION_ROI_DATA = {
    "Switch to LED Lighting": {
        "investment": 1000,
        "annual_savings": 200,
        "implementation_months": 1,
    },
    "Install Smart Power Strips": {
        "investment": 300,
        "annual_savings": 100,
        "implementation_months": 0.5,
    },
    "Optimize Delivery Routes": {
        "investment": 500,
        "annual_savings": 150,
        "implementation_months": 1,
    },
    "Solar Panel Installation": {
        "investment": 10000,
        "annual_savings": 3000,
        "implementation_months": 3,
    },
    "Energy Audit": {
        "investment": 2000,
        "annual_savings": 1000,
        "implementation_months": 1,
    },
    "Switch to CNG/Electric Vehicles": {
        "investment": 50000,
        "annual_savings": 5000,
        "implementation_months": 2,
    },
    "HVAC Optimization": {
        "investment": 5000,
        "annual_savings": 1500,
        "implementation_months": 2,
    },
    "Renewable Energy PPA": {
        "investment": 20000,
        "annual_savings": 8000,
        "implementation_months": 4,
    },
    "Carbon Offset Program": {
        "investment": 5000,
        "annual_savings": 2000,
        "implementation_months": 1,
    },
    "Process Electrification": {
        "investment": 30000,
        "annual_savings": 6000,
        "implementation_months": 6,
    },
    "ISO 14001 Certification": {
        "investment": 10000,
        "annual_savings": 3000,
        "implementation_months": 3,
    },
    "Power Factor Correction": {
        "investment": 500,
        "annual_savings": 150,
        "implementation_months": 1,
    },
}


def calculate_roi(suggestion: Dict) -> Dict:
    """
    Calculate ROI for a suggestion.
    Returns: {payback_months, roi_percentage, annual_savings, investment}
    """
    title = suggestion.get("title", "")
    roi_data = SUGGESTION_ROI_DATA.get(title, {
        "investment": 5000,
        "annual_savings": 1000,
        "implementation_months": 2,
    })
    
    investment = roi_data.get("investment", 5000)
    annual_savings = roi_data.get("annual_savings", 1000)
    
    # Payback period in months
    if annual_savings > 0:
        payback_months = (investment / annual_savings) * 12
    else:
        payback_months = 999
    
    # ROI percentage
    roi_percentage = ((annual_savings * 3 - investment) / investment * 100) if investment > 0 else 0
    
    return {
        "title": title,
        "investment": investment,
        "annual_savings": annual_savings,
        "payback_months": round(payback_months, 1),
        "roi_percentage": max(0, round(roi_percentage, 1)),
        "savings_percentage": suggestion.get("savings_percentage", 0),
    }


def categorize_suggestions_by_impact(suggestions: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Categorize suggestions by impact level (High/Medium/Low).
    """
    categorized = {
        "High Impact": [],
        "Medium Impact": [],
        "Low Impact": []
    }
    
    for suggestion in suggestions:
        savings = suggestion.get("savings_percentage", 0)
        roi = calculate_roi(suggestion)
        roi_data = {**suggestion, **roi}
        
        if savings >= 30:
            categorized["High Impact"].append(roi_data)
        elif savings >= 10:
            categorized["Medium Impact"].append(roi_data)
        else:
            categorized["Low Impact"].append(roi_data)
    
    return categorized


def format_history_data(history: List[Dict]) -> str:
    """Format history data for report."""
    lines = []
    for entry in history:
        month = entry.get("month", "N/A")
        total = entry.get("total_co2", 0)
        lines.append(f"{month}: {total:.1f} kg CO₂")
    return "\n".join(lines)


def generate_pdf_report(
    emission_data: Dict,
    suggestions: List[Dict],
    summary: str,
    history: List[Dict],
    forecast: List[float] = None,
    models_used: Dict = None,
) -> bytes:
    """
    Generate a comprehensive PDF report.
    Returns: PDF bytes
    """
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#22c55e'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#16a34a'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold',
    )
    
    # Title
    story.append(Paragraph("CarbonSense AI Sustainability Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    
    total_co2 = emission_data.get("total_co2", 0)
    carbon_score = emission_data.get("carbon_score", "N/A")
    score_value = emission_data.get("carbon_score_value", 0)
    
    summary_data = [
        ["Metric", "Value"],
        ["Monthly CO2 Emissions", f"{total_co2:.1f} kg"],
        ["Carbon Score", f"{carbon_score} ({score_value}/100)"],
        ["Electricity Usage", f"{emission_data.get('electricity_co2', 0):.1f} kg CO2"],
        ["Fuel Usage", f"{emission_data.get('fuel_co2', 0):.1f} kg CO2"],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#22c55e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')]),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Emissions Breakdown
    story.append(Paragraph("Emissions Breakdown", heading_style))
    
    electricity_pct = emission_data.get("breakdown_percentage", {}).get("electricity", 0)
    fuel_pct = emission_data.get("breakdown_percentage", {}).get("fuel", 0)
    
    breakdown_data = [
        ["Source", "CO2 (kg)", "Percentage"],
        ["Electricity", f"{emission_data.get('electricity_co2', 0):.1f}", f"{electricity_pct:.1f}%"],
        ["Fuel", f"{emission_data.get('fuel_co2', 0):.1f}", f"{fuel_pct:.1f}%"],
    ]
    
    breakdown_table = Table(breakdown_data, colWidths=[2*inch, 2*inch, 2*inch])
    breakdown_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fffbeb')]),
    ]))
    story.append(breakdown_table)
    story.append(Spacer(1, 0.2*inch))
    
    # 6-Month Trend
    story.append(Paragraph("6-Month Historical Trend", heading_style))
    
    history_data = [["Month", "Total CO2 (kg)"]]
    for entry in history:
        month = entry.get("month", "N/A").replace(" 2024", "").replace(" 2025", "")
        total = entry.get("total_co2", 0)
        history_data.append([month, f"{total:.1f}"])
    
    history_table = Table(history_data, colWidths=[3*inch, 3*inch])
    history_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eff6ff')]),
    ]))
    story.append(history_table)
    story.append(Spacer(1, 0.2*inch))
    
    # ROI Summary
    story.append(PageBreak())
    story.append(Paragraph("ROI Analysis & Investment Summary", heading_style))
    
    total_investment = sum(calculate_roi(s)["investment"] for s in suggestions)
    total_annual_savings = sum(calculate_roi(s)["annual_savings"] for s in suggestions)
    total_payback_months = (total_investment / total_annual_savings * 12) if total_annual_savings > 0 else 999
    total_roi_3year = (((total_annual_savings * 3 - total_investment) / total_investment * 100) if total_investment > 0 else 0)
    
    roi_summary = [
        ["Investment Metric", "Value"],
        ["Total Investment Required", f"${total_investment:,.0f}"],
        ["Total Annual Savings", f"${total_annual_savings:,.0f}"],
        ["Payback Period", f"{total_payback_months:.1f} months ({total_payback_months/12:.1f} years)"],
        ["3-Year ROI", f"{total_roi_3year:.0f}%"],
    ]
    
    roi_table = Table(roi_summary, colWidths=[3*inch, 3*inch])
    roi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#d1fae5')]),
    ]))
    story.append(roi_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Models Used
    story.append(Paragraph("AI Models & Analysis", heading_style))
    
    models_text = "This report was generated using the following ML models:<br/>"
    if models_used:
        models_text += f"• Emissions Predictor: {models_used.get('emissions_model', 'N/A')}<br/>"
        models_text += f"• Carbon Scorer: {models_used.get('scorer_model', 'N/A')}<br/>"
        models_text += f"• Trend Forecaster: {models_used.get('trend_model', 'N/A')}<br/>"
    
    story.append(Paragraph(models_text, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Footer
    footer_text = f"<i>Report generated on {datetime.now().strftime('%B %d, %Y at %H:%M')} | CarbonSense AI v1.0</i>"
    story.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    logger.info("✅ PDF report generated successfully")
    return buffer.getvalue()
