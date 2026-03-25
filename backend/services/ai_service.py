"""
AI Suggestions Service — sector-specific recommendations with Gemini LLM integration.
"""

import os
import json
import logging
from typing import List
from services.ml_service import predict_emissions
from services.pipeline_service import estimate_cost_savings, ELECTRICITY_RATE_INR, DIESEL_RATE_INR

logger = logging.getLogger(__name__)

# ─── Sector-Specific Suggestion Database ─────────────────────────────────────

SECTOR_SUGGESTIONS = {
    "restaurant": [
        {
            "title": "Commercial Kitchen Equipment Upgrade",
            "description": "Replace old commercial fryers, ovens, and grills with ENERGY STAR-rated equivalents. Commercial kitchens waste 80% of energy as heat.",
            "impact": "Reduces kitchen energy use by 20–35%",
            "savings_percentage": 28.0,
            "category": "Electricity",
            "priority": "High",
            "implementation_cost": "₹2–5 lakhs",
            "payback_months": 14,
        },
        {
            "title": "LPG to Induction Cooking Transition",
            "description": "Switch from LPG gas burners to induction cooktops. Induction is 85% efficient vs 40% for gas, with zero direct CO₂ emissions.",
            "impact": "Removes LPG fuel emissions entirely for cooking",
            "savings_percentage": 55.0,
            "category": "Fuel",
            "priority": "High",
            "implementation_cost": "₹80,000–₹2 lakhs",
            "payback_months": 18,
        },
        {
            "title": "Walk-in Cooler Insulation & Door Seals",
            "description": "Improve refrigeration efficiency by sealing door gaskets, adding night curtains, and upgrading compressors. Refrigeration is 35% of restaurant electricity.",
            "impact": "Reduces refrigeration energy by 15–25%",
            "savings_percentage": 18.0,
            "category": "Electricity",
            "priority": "Medium",
            "implementation_cost": "₹20,000–₹60,000",
            "payback_months": 6,
        },
        {
            "title": "Food Waste Biogas System",
            "description": "Install a small-scale biodigester to convert kitchen waste into biogas for cooking. Restaurants generate 2–5 kg waste/day which can offset LPG.",
            "impact": "Offsets 20–30% of cooking fuel use",
            "savings_percentage": 22.0,
            "category": "Fuel",
            "priority": "Medium",
            "implementation_cost": "₹1.5–3 lakhs",
            "payback_months": 24,
        },
        {
            "title": "Solar Rooftop for General Power",
            "description": "Install rooftop solar to power lights, fans, billing systems and AC. Restaurants with 15+ tables can offset 40% of non-kitchen electricity.",
            "impact": "Offsets 40–50% of general electricity use",
            "savings_percentage": 40.0,
            "category": "Electricity",
            "priority": "High",
            "implementation_cost": "₹3–5 lakhs",
            "payback_months": 48,
        },
    ],
    "manufacturing": [
        {
            "title": "Variable Frequency Drives (VFD) on Motors",
            "description": "Install VFDs on conveyor belts, pumps, and fans. Motors run at 100% capacity even at partial loads — VFDs reduce this waste by 30–50%.",
            "impact": "Reduces motor energy consumption by 30–50%",
            "savings_percentage": 38.0,
            "category": "Electricity",
            "priority": "High",
            "implementation_cost": "₹50,000–₹3 lakhs",
            "payback_months": 12,
        },
        {
            "title": "Compressed Air Leak Audit & Repair",
            "description": "Compressed air systems waste 20–30% through leaks. A systematic leak detection and repair program is the highest ROI intervention in any factory.",
            "impact": "Reduces compressor load by 20–30%",
            "savings_percentage": 25.0,
            "category": "Electricity",
            "priority": "High",
            "implementation_cost": "₹15,000–₹50,000",
            "payback_months": 4,
        },
        {
            "title": "Waste Heat Recovery System",
            "description": "Capture heat from furnaces, boilers, and kilns to preheat incoming air or water. Industrial waste heat recovery can cut fuel bills by 20–40%.",
            "impact": "Reduces furnace/boiler fuel use by 20–40%",
            "savings_percentage": 30.0,
            "category": "Fuel",
            "priority": "High",
            "implementation_cost": "₹3–15 lakhs",
            "payback_months": 24,
        },
        {
            "title": "Switch from HFO to Natural Gas / CNG",
            "description": "Replace heavy fuel oil or diesel-powered generators and boilers with CNG or piped gas. CNG emits 25% less CO₂ per unit energy than diesel.",
            "impact": "Reduces fuel CO₂ by 20–30%",
            "savings_percentage": 25.0,
            "category": "Fuel",
            "priority": "Medium",
            "implementation_cost": "₹2–8 lakhs (retrofit)",
            "payback_months": 20,
        },
        {
            "title": "ISO 50001 Energy Management System",
            "description": "Implement an energy management framework that systematically identifies and eliminates waste across all production lines.",
            "impact": "Systematic 15–25% reduction over 18 months",
            "savings_percentage": 20.0,
            "category": "Operations",
            "priority": "Medium",
            "implementation_cost": "₹1–2 lakhs",
            "payback_months": 18,
        },
    ],
    "retail": [
        {
            "title": "LED Retrofit for Display & Store Lighting",
            "description": "Retail lighting runs 12–16 hrs/day. Full LED retrofit with occupancy sensors in stockrooms can cut lighting energy by 60–70%.",
            "impact": "Reduces lighting energy by 60–70%",
            "savings_percentage": 35.0,
            "category": "Electricity",
            "priority": "High",
            "implementation_cost": "₹30,000–₹1.5 lakhs",
            "payback_months": 10,
        },
        {
            "title": "HVAC Smart Zoning & Scheduling",
            "description": "Install programmable thermostats and zone controllers. Pre-cool the store before opening hours using off-peak power rates.",
            "impact": "Reduces HVAC energy by 25–35%",
            "savings_percentage": 28.0,
            "category": "Electricity",
            "priority": "High",
            "implementation_cost": "₹40,000–₹1.2 lakhs",
            "payback_months": 12,
        },
        {
            "title": "Cold Chain Refrigeration Optimisation",
            "description": "Add anti-condensation heater controls, evaporator fan timers, and door strip curtains to open refrigeration units.",
            "impact": "Reduces refrigeration load by 15–20%",
            "savings_percentage": 16.0,
            "category": "Electricity",
            "priority": "Medium",
            "implementation_cost": "₹15,000–₹40,000",
            "payback_months": 8,
        },
        {
            "title": "Delivery Fleet EV Transition",
            "description": "Replace petrol/diesel delivery vehicles with EVs. Last-mile retail deliveries under 100km/day are ideal for EV economics.",
            "impact": "Eliminates direct fuel emissions from delivery",
            "savings_percentage": 60.0,
            "category": "Fuel",
            "priority": "High",
            "implementation_cost": "₹8–15 lakhs per vehicle",
            "payback_months": 36,
        },
        {
            "title": "Rooftop Solar + Battery Storage",
            "description": "Solar covers peak daytime demand when stores are busiest. Battery storage handles evening peak before grid power cheaper at night.",
            "impact": "Offsets 50–70% of daytime electricity use",
            "savings_percentage": 50.0,
            "category": "Electricity",
            "priority": "High",
            "implementation_cost": "₹5–12 lakhs",
            "payback_months": 54,
        },
    ],
    "it_software": [
        {
            "title": "Data Centre Cooling PUE Optimisation",
            "description": "Improve Power Usage Effectiveness (PUE) from 2.0 to 1.3 using hot aisle/cold aisle containment and free cooling coils.",
            "impact": "Reduces cooling energy by 35–50%",
            "savings_percentage": 40.0,
            "category": "Electricity",
            "priority": "High",
            "implementation_cost": "₹2–10 lakhs",
            "payback_months": 18,
        },
        {
            "title": "Server Virtualisation & Consolidation",
            "description": "Consolidate underutilised physical servers onto fewer virtual machines. IT server utilisation averages 12–18% — virtualisation raises this to 70–80%.",
            "impact": "Reduces server energy by 40–60%",
            "savings_percentage": 45.0,
            "category": "Electricity",
            "priority": "High",
            "implementation_cost": "₹1–3 lakhs (software licensing)",
            "payback_months": 12,
        },
        {
            "title": "Green Cloud Migration",
            "description": "Move on-premise workloads to a green cloud provider (AWS, Azure, or GCP powered by renewables) and shut down legacy servers.",
            "impact": "Reduces on-premise electricity to near zero",
            "savings_percentage": 70.0,
            "category": "Electricity",
            "priority": "High",
            "implementation_cost": "₹3–8 lakhs (migration cost)",
            "payback_months": 24,
        },
        {
            "title": "Employee WFH Carbon Policy",
            "description": "Formalise remote work to reduce commute emissions and office energy. A 30% WFH policy can cut office energy by 20%.",
            "impact": "Reduces office energy and commute fuel by 15–25%",
            "savings_percentage": 20.0,
            "category": "Operations",
            "priority": "Medium",
            "implementation_cost": "₹0 (policy change)",
            "payback_months": 1,
        },
        {
            "title": "Renewable Energy Certificate (REC) Purchase",
            "description": "Purchase RECs to match 100% of electricity consumption with renewable energy certificates from Indian wind/solar projects.",
            "impact": "Claims 100% renewable electricity on Scope 2",
            "savings_percentage": 82.0,
            "category": "Electricity",
            "priority": "Medium",
            "implementation_cost": "₹2–5/kWh premium",
            "payback_months": 0,
        },
    ],
    "healthcare": [
        {
            "title": "Medical Waste Autoclave → Microwave Sterilisation",
            "description": "Replace steam autoclaves with microwave sterilisation units which use 70% less energy and eliminate steam boiler fuel.",
            "impact": "Reduces sterilisation energy and fuel by 60–70%",
            "savings_percentage": 60.0,
            "category": "Fuel",
            "priority": "High",
            "implementation_cost": "₹2–5 lakhs",
            "payback_months": 24,
        },
        {
            "title": "LED Lighting in Wards & Corridors",
            "description": "Hospitals run 24/7. LED lighting with daylight harvesting sensors in non-critical areas (corridors, offices, waiting rooms) saves 50–65% on lighting.",
            "impact": "Reduces 24/7 lighting load by 50–65%",
            "savings_percentage": 30.0,
            "category": "Electricity",
            "priority": "High",
            "implementation_cost": "₹50,000–₹2 lakhs",
            "payback_months": 12,
        },
        {
            "title": "HVAC Upgrade with Heat Recovery Ventilation",
            "description": "Healthcare HVAC runs at 100% fresh air for infection control. Heat Recovery Ventilation (HRV) recovers 60–80% of conditioned air energy.",
            "impact": "Reduces HVAC energy by 25–40%",
            "savings_percentage": 32.0,
            "category": "Electricity",
            "priority": "High",
            "implementation_cost": "₹3–8 lakhs",
            "payback_months": 20,
        },
        {
            "title": "Solar Hot Water System for Sterilisation",
            "description": "Install solar thermal collectors to preheat water for sterilisation, laundry, and patient bathing. Replaces diesel/LPG boiler load.",
            "impact": "Reduces boiler fuel use by 40–60%",
            "savings_percentage": 45.0,
            "category": "Fuel",
            "priority": "Medium",
            "implementation_cost": "₹1.5–4 lakhs",
            "payback_months": 30,
        },
        {
            "title": "Green Building Retrofit (BEE Star Rating)",
            "description": "Apply for BEE Star Rating and implement recommendations: insulation, window glazing, shading. HVAC savings of 20–30%.",
            "impact": "Systematic building energy reduction of 15–25%",
            "savings_percentage": 20.0,
            "category": "Operations",
            "priority": "Medium",
            "implementation_cost": "₹5–20 lakhs",
            "payback_months": 36,
        },
    ],
    "education": [
        {
            "title": "Smart Campus Energy Management System",
            "description": "Deploy IoT occupancy sensors across classrooms, labs, and auditoriums to auto-switch off lights and AC when rooms are empty.",
            "impact": "Reduces electricity waste from unoccupied spaces by 30–40%",
            "savings_percentage": 32.0,
            "category": "Electricity",
            "priority": "High",
            "implementation_cost": "₹1–3 lakhs",
            "payback_months": 14,
        },
        {
            "title": "Solar Canopy over Parking & Playgrounds",
            "description": "Install solar panels as shade structures over parking lots and sports courts — dual purpose with no roof space needed.",
            "impact": "Generates 20–40% of campus electricity",
            "savings_percentage": 30.0,
            "category": "Electricity",
            "priority": "High",
            "implementation_cost": "₹8–20 lakhs",
            "payback_months": 60,
        },
        {
            "title": "School Bus Fleet CNG/EV Conversion",
            "description": "Convert diesel school buses to CNG or electric. Many states offer subsidies and FAME-II scheme covers up to 40% of EV cost.",
            "impact": "Reduces transport emissions by 40–100%",
            "savings_percentage": 55.0,
            "category": "Fuel",
            "priority": "High",
            "implementation_cost": "₹5–12 lakhs per bus (net of subsidy)",
            "payback_months": 36,
        },
        {
            "title": "Rainwater Harvesting to Reduce Pump Load",
            "description": "Campus water pumps consume significant electricity. Rainwater harvesting reduces the load on borewells and treatment pumps by 30–50%.",
            "impact": "Reduces water pumping energy by 30–50%",
            "savings_percentage": 10.0,
            "category": "Electricity",
            "priority": "Low",
            "implementation_cost": "₹50,000–₹2 lakhs",
            "payback_months": 24,
        },
        {
            "title": "Digital Classroom Transition",
            "description": "Replace projectors and printed materials with digital displays and e-learning. Reduces printing costs and energy from paper production.",
            "impact": "Reduces printing energy and paper CO₂ by 50%",
            "savings_percentage": 12.0,
            "category": "Operations",
            "priority": "Medium",
            "implementation_cost": "₹1–4 lakhs",
            "payback_months": 18,
        },
    ],
    "textile": [
        {
            "title": "Knitting/Weaving Machine Motor Upgrade",
            "description": "Replace old AC induction motors on looms and knitting machines with IE3-class high-efficiency motors with VFD controls.",
            "impact": "Reduces motor electricity by 20–35%",
            "savings_percentage": 27.0,
            "category": "Electricity",
            "priority": "High",
            "implementation_cost": "₹80,000–₹4 lakhs",
            "payback_months": 16,
        },
        {
            "title": "Steam System Insulation & Trap Maintenance",
            "description": "Textile dyeing uses large volumes of steam. Insulating steam lines and fixing steam traps can cut steam generation fuel by 15–25%.",
            "impact": "Reduces boiler fuel use by 15–25%",
            "savings_percentage": 20.0,
            "category": "Fuel",
            "priority": "High",
            "implementation_cost": "₹30,000–₹2 lakhs",
            "payback_months": 10,
        },
        {
            "title": "ETP Effluent Heat Recovery",
            "description": "Recover heat from hot dyeing wastewater to preheat fresh water entering the dyeing vats. Can offset 20–30% of heating energy.",
            "impact": "Reduces dyeing process heat energy by 20–30%",
            "savings_percentage": 22.0,
            "category": "Fuel",
            "priority": "Medium",
            "implementation_cost": "₹1.5–4 lakhs",
            "payback_months": 20,
        },
        {
            "title": "Natural Dye & Low-Temperature Dyeing",
            "description": "Switch to reactive dyes that work at lower temperatures (40°C vs 90°C). Reduces heating energy by up to 50%.",
            "impact": "Reduces dyeing steam requirement by 30–50%",
            "savings_percentage": 35.0,
            "category": "Fuel",
            "priority": "High",
            "implementation_cost": "₹20,000–₹50,000 (dye sourcing)",
            "payback_months": 6,
        },
        {
            "title": "Solar Power for Spinning Units",
            "description": "Spinning mills run 20+ hrs/day and are ideal solar customers. Grid-scale rooftop solar provides predictable savings for decades.",
            "impact": "Offsets 30–50% of spinning electricity",
            "savings_percentage": 40.0,
            "category": "Electricity",
            "priority": "High",
            "implementation_cost": "₹10–30 lakhs",
            "payback_months": 54,
        },
    ],
    "logistics": [
        {
            "title": "Route Optimisation AI Platform",
            "description": "Deploy AI-based route planning software to minimise empty miles, reduce vehicle stops, and consolidate loads. Reduces fuel by 15–25%.",
            "impact": "Reduces fleet fuel consumption by 15–25%",
            "savings_percentage": 20.0,
            "category": "Fuel",
            "priority": "High",
            "implementation_cost": "₹1,500–₹5,000/vehicle/year (software)",
            "payback_months": 3,
        },
        {
            "title": "Fleet EV Transition (Last-Mile)",
            "description": "Replace diesel 3-wheelers and light commercial vehicles for city last-mile deliveries with EVs. Eligible for FAME-II subsidy of ₹1.5 lakh.",
            "impact": "Eliminates fuel emissions for last-mile fleet",
            "savings_percentage": 65.0,
            "category": "Fuel",
            "priority": "High",
            "implementation_cost": "₹4–8 lakhs per vehicle (net of subsidy)",
            "payback_months": 30,
        },
        {
            "title": "Driver Eco-Driving Training Programme",
            "description": "Aggressive driving (hard braking, rapid acceleration) wastes 20–30% of fuel. Professional eco-driving training achieves 10-15% fuel savings with zero capex.",
            "impact": "Reduces fleet fuel use by 10–15%",
            "savings_percentage": 12.0,
            "category": "Fuel",
            "priority": "Medium",
            "implementation_cost": "₹500–₹2,000/driver",
            "payback_months": 2,
        },
        {
            "title": "CNG Conversion for Long-Haul Trucks",
            "description": "Convert intercity trucks to CNG. CNG costs ₹75–85/kg vs diesel's ₹95/L equivalent, and emits 20–25% less CO₂.",
            "impact": "Reduces long-haul fuel CO₂ by 20–25%",
            "savings_percentage": 22.0,
            "category": "Fuel",
            "priority": "High",
            "implementation_cost": "₹1.5–3 lakhs per truck (retrofit)",
            "payback_months": 18,
        },
        {
            "title": "Warehouse LED + Solar Rooftop",
            "description": "Large warehouse rooftops are ideal for solar. Combined with LED high-bay lighting, reduces warehouse electricity by 60–70%.",
            "impact": "Reduces warehouse electricity by 60–70%",
            "savings_percentage": 55.0,
            "category": "Electricity",
            "priority": "High",
            "implementation_cost": "₹15–40 lakhs",
            "payback_months": 48,
        },
    ],
    "agriculture": [
        {
            "title": "Solar Pump for Irrigation",
            "description": "Replace diesel pump sets with solar water pumps. PM-KUSUM scheme subsidises up to 60% of solar pump cost. Zero fuel, zero electricity cost.",
            "impact": "Eliminates diesel pump fuel use entirely",
            "savings_percentage": 80.0,
            "category": "Fuel",
            "priority": "High",
            "implementation_cost": "₹80,000–₹2 lakhs (post-subsidy)",
            "payback_months": 24,
        },
        {
            "title": "Drip/Micro-Irrigation to Reduce Pump Hours",
            "description": "Drip irrigation reduces water use by 40–50% vs flood irrigation, directly cutting pump runtime, fuel, and electricity costs proportionally.",
            "impact": "Reduces pump energy by 40–50%",
            "savings_percentage": 42.0,
            "category": "Fuel",
            "priority": "High",
            "implementation_cost": "₹40,000–₹1 lakh/acre",
            "payback_months": 18,
        },
        {
            "title": "Crop Residue Biogas Plant",
            "description": "Convert agricultural waste (stubble, husks, dung) into biogas for cooking fuel and electricity. Prevents stubble burning (a major CO₂ source).",
            "impact": "Replaces 30–50% of cooking LPG/fuel use",
            "savings_percentage": 35.0,
            "category": "Fuel",
            "priority": "Medium",
            "implementation_cost": "₹1–4 lakhs",
            "payback_months": 30,
        },
        {
            "title": "Farm Vehicle CNG/Electric Conversion",
            "description": "Convert tillers, small tractors, and transport vehicles to CNG or electric where available. Farm vehicle fuel is 30–40% of total farm emissions.",
            "impact": "Reduces farm vehicle emissions by 25–60%",
            "savings_percentage": 30.0,
            "category": "Fuel",
            "priority": "Medium",
            "implementation_cost": "₹1–3 lakhs per vehicle",
            "payback_months": 24,
        },
        {
            "title": "Cold Storage Solar Hybrid System",
            "description": "Agri cold storage runs 24/7. Install solar + inverter hybrid to power compressors during daytime and reduce diesel generator runtime by 70%.",
            "impact": "Reduces cold storage energy cost by 40–60%",
            "savings_percentage": 45.0,
            "category": "Electricity",
            "priority": "High",
            "implementation_cost": "₹5–15 lakhs",
            "payback_months": 36,
        },
    ],
    "general msme": [
        {
            "title": "Solar Panel Installation",
            "description": "Install rooftop solar. A 10 kW system offsets 40–60% of electricity needs with 5–7 year ROI.",
            "impact": "Reduces electricity CO₂ by 40–60%",
            "savings_percentage": 45.0,
            "category": "Electricity",
            "priority": "High",
            "implementation_cost": "₹4–6 lakhs",
            "payback_months": 60,
        },
        {
            "title": "Professional Energy Audit",
            "description": "A BEE-certified energy audit identifies hidden waste. Most audits pay for themselves within 6 months through the actions they uncover.",
            "impact": "Identifies 15–30% savings opportunities",
            "savings_percentage": 22.0,
            "category": "Electricity",
            "priority": "High",
            "implementation_cost": "₹20,000–₹50,000",
            "payback_months": 6,
        },
        {
            "title": "CNG / Electric Fleet Transition",
            "description": "Transition your fleet to CNG or EVs. EVs emit zero direct CO₂ with lower running costs.",
            "impact": "Reduces fuel CO₂ by 50–100%",
            "savings_percentage": 60.0,
            "category": "Fuel",
            "priority": "High",
            "implementation_cost": "₹3–8 lakhs per vehicle",
            "payback_months": 36,
        },
        {
            "title": "LED Lighting Retrofit",
            "description": "Replace conventional bulbs with LED lights. LEDs use 75% less energy and last 25× longer.",
            "impact": "Reduces lighting energy by 60–75%",
            "savings_percentage": 12.0,
            "category": "Electricity",
            "priority": "Medium",
            "implementation_cost": "₹15,000–₹40,000",
            "payback_months": 8,
        },
        {
            "title": "HVAC Optimisation",
            "description": "Upgrade to energy-efficient HVAC and smart thermostats. Reduces cooling/heating energy by 25%.",
            "impact": "Reduces electricity use by 20–25%",
            "savings_percentage": 22.0,
            "category": "Electricity",
            "priority": "Medium",
            "implementation_cost": "₹80,000–₹2 lakhs",
            "payback_months": 18,
        },
    ],
}


def _normalize_sector(sector: str) -> str:
    """Normalize sector name to dict key."""
    s = sector.lower().strip()
    # Map common variations
    if any(x in s for x in ["restaur", "food", "cafe", "hotel", "dhaba", "canteen"]):
        return "restaurant"
    if any(x in s for x in ["manufactur", "factory", "plant", "industri", "foundry"]):
        return "manufacturing"
    if any(x in s for x in ["retail", "shop", "store", "supermarket", "kirana"]):
        return "retail"
    if any(x in s for x in ["it", "software", "tech", "digital", "saas", "startup"]):
        return "it_software"
    if any(x in s for x in ["health", "hospital", "clinic", "pharmacy", "medical"]):
        return "healthcare"
    if any(x in s for x in ["education", "school", "college", "university", "academ"]):
        return "education"
    if any(x in s for x in ["textile", "garment", "fabric", "yarn", "weav", "dye"]):
        return "textile"
    if any(x in s for x in ["logistic", "transport", "warehouse", "shipping", "courier", "fleet"]):
        return "logistics"
    if any(x in s for x in ["agri", "farm", "crop", "dairy", "horticulture"]):
        return "agriculture"
    return "general msme"


def _enrich_with_cost_savings(suggestions: list, electricity_kwh: float, fuel_litres: float) -> list:
    """Add INR cost_savings field to each suggestion."""
    monthly_elec_cost = electricity_kwh * ELECTRICITY_RATE_INR
    monthly_fuel_cost = fuel_litres * DIESEL_RATE_INR
    total_monthly = monthly_elec_cost + monthly_fuel_cost

    enriched = []
    for s in suggestions:
        s = dict(s)
        pct = s.get("savings_percentage", 0) / 100
        if s.get("category") == "Electricity":
            savings_inr = monthly_elec_cost * pct
        elif s.get("category") == "Fuel":
            savings_inr = monthly_fuel_cost * pct
        else:
            savings_inr = total_monthly * pct * 0.6
        s["cost_savings_inr"] = round(savings_inr, 2)
        s["confidence"] = round(0.75 + pct * 0.15, 2)
        enriched.append(s)
    return enriched


def _generate_llm_summary(total_co2: float, sector: str, suggestions: list,
                           electricity_kwh: float, fuel_litres: float) -> str:
    """Try Gemini LLM for a personalized summary. Falls back to template."""
    try:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("No GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        top_3 = [s["title"] for s in suggestions[:3]]
        prompt = (
            f"You are a carbon sustainability expert advising an Indian MSME in the {sector} sector.\n"
            f"Their monthly emissions: {total_co2:.0f} kg CO₂ "
            f"(electricity: {electricity_kwh:.0f} kWh, fuel: {fuel_litres:.0f} L).\n"
            f"Top recommended actions: {', '.join(top_3)}.\n"
            f"Write a 2-sentence actionable summary starting with the sector name, "
            f"mentioning their biggest emission source and the most impactful first step. "
            f"Keep it concise and motivating. Include an INR savings estimate."
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.warning(f"LLM summary failed, using template: {e}")
        # Fallback template
        top = suggestions[0]["title"] if suggestions else "energy efficiency"
        estimated_reduction = max((s.get("savings_percentage", 0) for s in suggestions[:3]), default=20)
        total_savings = sum(s.get("cost_savings_inr", 0) for s in suggestions[:3])
        return (
            f"For your {sector} business with {total_co2:.0f} kg CO₂/month, "
            f"starting with '{top}' could cut emissions by up to {estimated_reduction:.0f}% "
            f"and save ₹{total_savings:,.0f}/month."
        )


def get_sector_suggestions(
    total_co2: float,
    electricity_kwh: float,
    fuel_litres: float,
    business_type: str,
) -> dict:
    """Return sector-specific, cost-enriched suggestions with LLM summary."""
    sector_key = _normalize_sector(business_type or "general msme")
    raw = list(SECTOR_SUGGESTIONS.get(sector_key, SECTOR_SUGGESTIONS["general msme"]))

    # Sort: high-impact first, then cost-effectiveness
    raw.sort(key=lambda s: (-s.get("savings_percentage", 0), s.get("payback_months", 999)))

    # Bias towards electricity vs fuel suggestions based on actual split
    elec_heavy = electricity_kwh > fuel_litres * 1.5
    if elec_heavy:
        raw = sorted(raw, key=lambda s: (s.get("category") != "Electricity", -s.get("savings_percentage", 0)))

    suggestions = _enrich_with_cost_savings(raw[:5], electricity_kwh, fuel_litres)

    summary = _generate_llm_summary(total_co2, business_type, suggestions, electricity_kwh, fuel_litres)
    estimated_reduction = max(s["savings_percentage"] for s in suggestions[:3]) if suggestions else 0
    total_savings_inr = sum(s.get("cost_savings_inr", 0) for s in suggestions[:3])

    return {
        "success": True,
        "suggestions": suggestions,
        "summary": summary,
        "estimated_reduction": estimated_reduction,
        "model_used": "sector_specific_ai",
        "sector": business_type,
        "total_potential_savings_inr": round(total_savings_inr, 2),
    }


async def get_ai_suggestions(
    total_co2: float, electricity_kwh: float, fuel_litres: float, business_type: str
) -> dict:
    """Main entry: get sector-specific AI suggestions. Falls back to general."""
    try:
        return get_sector_suggestions(total_co2, electricity_kwh, fuel_litres, business_type or "General MSME")
    except Exception as e:
        logger.error(f"Sector suggestions failed: {e}")
        # Fallback: simple suggestions
        fallback = list(SECTOR_SUGGESTIONS["general msme"])
        suggestions = _enrich_with_cost_savings(fallback[:4], electricity_kwh, fuel_litres)
        return {
            "success": True,
            "suggestions": suggestions,
            "summary": f"Based on {total_co2:.0f} kg CO₂/month, focus on your top emission sources first.",
            "estimated_reduction": 30,
            "model_used": "fallback",
            "total_potential_savings_inr": sum(s.get("cost_savings_inr", 0) for s in suggestions),
        }
