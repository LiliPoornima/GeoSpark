#!/usr/bin/env python3
"""
GeoSpark API Server - Enhanced Professional Version
Run this with: python main.py
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, List, Optional
import json
import asyncio
from datetime import datetime
import uuid
import bcrypt
import random
import math

# Import the demo functionality
from demo import GeoSparkDemo

# Import Stripe routes
from app.api.v1.stripe_routes import router as stripe_router

# In-memory user DB
USERS_DB: Dict[str, Dict] = {}

app = FastAPI(
    title="GeoSpark AI Analytics Platform",
    description="AI-powered renewable energy analysis platform - Professional Version",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Stripe payment routes
app.include_router(stripe_router, prefix="/api/v1")

# Initialize demo
demo = GeoSparkDemo()

# Pydantic models
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class AuthenticationRequest(BaseModel):
    username: str
    password: str

class Location(BaseModel):
    latitude: float
    longitude: float
    area_km2: float = 100

class SiteAnalysisRequest(BaseModel):
    location: Location
    project_type: str = "solar"
    analysis_depth: str = "comprehensive"

class TextAnalysisRequest(BaseModel):
    text: str
    analysis_type: str = "general"

class DataSearchRequest(BaseModel):
    query: str
    limit: int = 5

# Resource Estimation models
class ResourceLocation(BaseModel):
    latitude: float
    longitude: float
    area_km2: float = 100

class ResourceEstimationRequest(BaseModel):
    location: ResourceLocation
    resource_type: str = "solar"
    system_config: Dict[str, Any] = {}

class CostEvaluationRequest(BaseModel):
    project_data: Dict[str, Any]
    financial_params: Dict[str, Any] = {}

class AgentChatRequest(BaseModel):
    message: str
    city: str | None = None
    resource_type: str | None = None
    mode: str | None = None  # 'workflow' or 'chat'

# Enhanced Reporting Models
class ReportMetrics(BaseModel):
    npv: float  # Net Present Value in million USD
    irr: float  # Internal Rate of Return
    payback: float  # Payback period in years
    lcoe: float  # Levelized Cost of Energy in USD/MWh
    annual_generation: float  # GWh per year
    capacity_factor: float  # Percentage
    carbon_reduction: float  # tons CO2 per year

class ComprehensiveReportRequest(BaseModel):
    project_name: str
    location: Dict[str, float]
    resource_type: str
    capacity_mw: float
    developer: str = "Unknown Developer"
    country: str = "Unknown Country"
    report_type: str = "executive"  # executive, investor, technical, environmental
    estimated_cost: Optional[float] = None
    timeline_months: Optional[int] = None

# Enhanced calculation functions for realistic metrics
def calculate_realistic_metrics(request: ComprehensiveReportRequest) -> ReportMetrics:
    """Calculate realistic financial and technical metrics based on ACTUAL project parameters"""
    capacity = request.capacity_mw
    resource_type = request.resource_type.lower()
    
    # Industry standard cost per MW (USD) - more realistic
    cost_per_mw = {
        "solar": 1200000,    # $1.2M per MW
        "wind": 1800000,     # $1.8M per MW  
        "hybrid": 1500000,   # $1.5M per MW
        "hydro": 2500000,    # $2.5M per MW
    }
    
    # Use provided cost or calculate realistic one
    if request.estimated_cost and request.estimated_cost >= capacity * 500000:
        total_capex = request.estimated_cost
    else:
        total_capex = capacity * cost_per_mw.get(resource_type, 1200000)
    
    # Realistic capacity factors based on resource type and location
    base_capacity_factors = {
        "solar": 0.18,  # 18% base for solar
        "wind": 0.32,   # 32% base for wind
        "hybrid": 0.25, # 25% for hybrid
        "hydro": 0.45,  # 45% for hydro
    }
    
    # Add location-based variation (latitude affects solar, etc.)
    lat = abs(request.location.get('latitude', 0))
    if resource_type == "solar":
        # Solar performs better near equator
        lat_factor = max(0.8, 1.2 - (lat / 45))
        capacity_factor = base_capacity_factors["solar"] * lat_factor
    elif resource_type == "wind":
        # Wind varies less with latitude
        capacity_factor = base_capacity_factors["wind"] * (0.9 + random.random() * 0.2)
    else:
        capacity_factor = base_capacity_factors.get(resource_type, 0.25)
    
    # Clamp capacity factor to realistic ranges
    capacity_factor = max(0.15, min(capacity_factor, 0.50))
    
    # Calculate annual generation (GWh)
    annual_generation_mwh = capacity * capacity_factor * 8760  # hours per year
    annual_generation_gwh = annual_generation_mwh / 1000
    
    # Carbon reduction (tons CO2 per GWh displaced from fossil fuels)
    carbon_intensity_displaced = 0.6  # tons CO2 per MWh from natural gas
    carbon_reduction = annual_generation_mwh * carbon_intensity_displaced
    
    # Financial calculations
    electricity_price = 65  # USD per MWh (current market rates)
    annual_revenue = annual_generation_mwh * electricity_price
    annual_opex = total_capex * 0.025  # 2.5% of CAPEX for O&M
    
    # Project parameters
    project_lifetime = 25
    discount_rate = 0.07
    
    # Calculate NPV
    npv = -total_capex
    for year in range(1, project_lifetime + 1):
        npv += (annual_revenue - annual_opex) / ((1 + discount_rate) ** year)
    
    # Calculate IRR (simplified)
    if total_capex > 0 and (annual_revenue - annual_opex) > 0:
        irr = (annual_revenue - annual_opex) / total_capex
    else:
        irr = 0.12
    
    # Calculate payback period
    annual_cash_flow = annual_revenue - annual_opex
    if annual_cash_flow > 0:
        payback = total_capex / annual_cash_flow
    else:
        payback = project_lifetime
    
    # Calculate LCOE properly
    total_generation_mwh = annual_generation_mwh * project_lifetime
    if total_generation_mwh > 0:
        # Present value of costs
        pv_costs = total_capex + sum(annual_opex / ((1 + discount_rate) ** year) 
                                   for year in range(1, project_lifetime + 1))
        lcoe = pv_costs / total_generation_mwh
    else:
        lcoe = 80.0
    
    return ReportMetrics(
        npv=npv / 1000000,  # Convert to million USD
        irr=max(0.08, min(irr, 0.25)),  # Realistic IRR range 8-25%
        payback=min(payback, project_lifetime),
        lcoe=max(40, min(lcoe, 120)),  # Realistic LCOE range $40-120/MWh
        annual_generation=annual_generation_gwh,
        capacity_factor=capacity_factor,
        carbon_reduction=carbon_reduction
    )

def generate_dynamic_charts(request: ComprehensiveReportRequest, metrics: ReportMetrics) -> Dict:
    """Generate dynamic charts that reflect actual project parameters"""
    capacity = request.capacity_mw
    
    # CAPEX breakdown based on actual project scale
    equipment_ratio = 0.45 + (capacity / 1000) * 0.1  # Larger projects have higher equipment ratio
    installation_ratio = 0.25 - (capacity / 1000) * 0.05
    grid_ratio = 0.12
    development_ratio = 0.10
    contingency_ratio = 0.08
    
    capex_data = [
        metrics.annual_generation * equipment_ratio * 1000,
        metrics.annual_generation * installation_ratio * 1000,
        metrics.annual_generation * grid_ratio * 1000,
        metrics.annual_generation * development_ratio * 1000,
        metrics.annual_generation * contingency_ratio * 1000
    ]
    
    # Revenue forecast with realistic growth
    base_revenue = metrics.annual_generation * 0.055  # $55/MWh average
    revenue_forecast = [base_revenue * (1 + 0.03 * i) for i in range(5)]
    
    # Monthly generation with seasonal patterns
    if request.resource_type == "solar":
        # Solar: higher in summer months
        monthly_pattern = [0.08, 0.09, 0.10, 0.11, 0.12, 0.12, 0.11, 0.10, 0.09, 0.08, 0.07, 0.07]
    elif request.resource_type == "wind":
        # Wind: often higher in winter
        monthly_pattern = [0.11, 0.10, 0.09, 0.08, 0.07, 0.06, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11]
    else:
        # Hybrid/Hydro: more consistent
        monthly_pattern = [0.09, 0.09, 0.09, 0.09, 0.09, 0.09, 0.09, 0.09, 0.09, 0.09, 0.09, 0.09]
    
    monthly_generation = [metrics.annual_generation * factor for factor in monthly_pattern]
    
    return {
        "financial": {
            "capex_breakdown": {
                "labels": ['Equipment', 'Installation', 'Grid Connection', 'Development', 'Contingency'],
                "data": capex_data,
                "colors": ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'],
                "label": "Cost (USD)"
            },
            "revenue_forecast": {
                "labels": ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5'],
                "data": revenue_forecast,
                "label": "Revenue (Million USD)"
            }
        },
        "technical": {
            "monthly_generation": {
                "labels": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                "data": monthly_generation,
                "label": "Generation (GWh)"
            }
        }
    }

def generate_professional_report_content(request: ComprehensiveReportRequest, metrics: ReportMetrics) -> str:
    """Generate detailed, professional report content with GeoSpark branding"""
    
    report_templates = {
        "executive": f"""
GEO SPARK AI - EXECUTIVE SUMMARY REPORT
Project: {request.project_name}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

EXECUTIVE OVERVIEW
------------------
{request.project_name} is a {request.capacity_mw} MW {request.resource_type} energy project located in {request.country}. 
Developed by {request.developer}, this project represents a significant investment in renewable energy infrastructure.

KEY FINANCIAL METRICS
• Net Present Value: ${metrics.npv:.1f} Million
• Internal Rate of Return: {metrics.irr*100:.1f}%
• Payback Period: {metrics.payback:.1f} Years
• Levelized Cost of Energy: ${metrics.lcoe:.1f}/MWh

TECHNICAL PERFORMANCE
• Annual Generation: {metrics.annual_generation:.0f} GWh
• Capacity Factor: {metrics.capacity_factor*100:.1f}%
• Carbon Reduction: {metrics.carbon_reduction:,.0f} tons CO2/year

STRATEGIC RECOMMENDATIONS
1. Proceed with project development given strong financial returns
2. Implement phased construction over {request.timeline_months or 24} months
3. Secure power purchase agreements at competitive rates
4. Monitor regulatory developments in {request.country}

This project demonstrates excellent viability with robust financial metrics and significant environmental benefits.

---
GeoSpark AI Analytics • Confidential Business Report
        """,
        
        "investor": f"""
GEO SPARK AI - INVESTOR REPORT
Project: {request.project_name}

INVESTMENT HIGHLIGHTS
• {request.capacity_mw} MW {request.resource_type} Project in {request.country}
• NPV: ${metrics.npv:.1f}M | IRR: {metrics.irr*100:.1f}% | Payback: {metrics.payback:.1f} Years
• Annual Revenue Potential: ${metrics.annual_generation * 55:,.0f}
• Carbon Credits: {metrics.carbon_reduction:,.0f} tons/year

FINANCIAL ANALYSIS
CAPEX Breakdown: ${request.estimated_cost or metrics.npv*1000000:,.0f}
- Equipment: {metrics.annual_generation * 0.45:,.0f}
- Installation: {metrics.annual_generation * 0.25:,.0f}
- Grid Connection: {metrics.annual_generation * 0.15:,.0f}

Revenue Streams:
1. Electricity Sales: ${metrics.annual_generation * 55:,.0f}/year
2. Carbon Credits: ${metrics.carbon_reduction * 25:,.0f}/year
3. Government Incentives: Available

RISK ASSESSMENT: Low to Moderate
• Technology Risk: Low ({request.resource_type} is proven)
• Regulatory Risk: Medium (dependent on {request.country} policies)
• Market Risk: Low (growing demand for renewables)

EXIT STRATEGY
• Project sale after 5-7 years of operation
• IPO potential for portfolio of projects
• Infrastructure fund acquisition

---
GeoSpark AI Analytics • Investor Confidential
        """,
        
        "technical": f"""
GEO SPARK AI - TECHNICAL REPORT
Project: {request.project_name}

TECHNICAL SPECIFICATIONS
• Capacity: {request.capacity_mw} MW {request.resource_type}
• Location: {request.location['latitude']:.4f}°, {request.location['longitude']:.4f}°
• Annual Generation: {metrics.annual_generation:.0f} GWh
• Capacity Factor: {metrics.capacity_factor*100:.1f}%
• System Availability: 98% target

DESIGN PARAMETERS
{request.resource_type.upper()} SYSTEM CONFIGURATION:
- Panel/Turbine Efficiency: {85 + random.randint(0,10)}%
- Inverter Efficiency: 98%
- System Losses: 8-12%
- Land Requirement: {request.capacity_mw * 5} acres

PERFORMANCE ANALYSIS
Monthly Generation Profile:
- Peak: {max(metrics.annual_generation * 0.12, metrics.annual_generation * 0.08):.1f} GWh
- Average: {metrics.annual_generation / 12:.1f} GWh
- Capacity Utilization: Excellent

MAINTENANCE SCHEDULE
• Quarterly inspections
• Annual major maintenance
• 25-year design life

---
GeoSpark AI Analytics • Technical Specifications
        """,
        
        "environmental": f"""
GEO SPARK AI - ENVIRONMENTAL IMPACT REPORT
Project: {request.project_name}

ENVIRONMENTAL BENEFITS
• Annual CO2 Reduction: {metrics.carbon_reduction:,.0f} tons
• Equivalent to: {metrics.carbon_reduction / 5:,.0f} cars removed from roads
• Equivalent Trees Planted: {metrics.carbon_reduction * 22.4:,.0f}
• Homes Powered: {metrics.annual_generation * 100:,.0f}

SUSTAINABILITY METRICS
• Carbon Intensity: 0 g CO2/kWh (vs. 600 g CO2/kWh for natural gas)
• Water Savings: {metrics.annual_generation * 1000:,.0f} gallons/year vs. thermal generation
• Land Impact: Minimal (compatible with agricultural use)

COMMUNITY IMPACT
• Job Creation: {int(request.capacity_mw * 2)} construction jobs, {int(request.capacity_mw * 0.3)} permanent jobs
• Local Economic Benefits: ${request.capacity_mw * 50000:,.0f}/year in local spending
• Energy Security: Reduces dependence on imported fuels

COMPLIANCE & CERTIFICATIONS
• Meets {request.country} renewable energy targets
• Eligible for carbon credit programs
• Aligns with UN Sustainable Development Goals

---
GeoSpark AI Analytics • Environmental Impact Assessment
        """
    }
    
    return report_templates.get(request.report_type, report_templates["executive"])

def generate_keywords(resource_type: str, report_type: str) -> List[str]:
    """Generate relevant keywords for the report"""
    base_keywords = ["renewable energy", "sustainability", "clean technology", "GeoSpark AI"]
    resource_keywords = {
        "solar": ["photovoltaic", "solar farm", "PV system", "solar panels"],
        "wind": ["wind turbine", "wind farm", "turbine technology", "wind power"],
        "hybrid": ["hybrid system", "energy storage", "battery", "smart grid"],
        "hydro": ["hydroelectric", "water power", "dam", "turbine"]
    }
    report_keywords = {
        "executive": ["strategic", "investment", "business case", "management"],
        "investor": ["ROI", "financial", "investment thesis", "returns"],
        "technical": ["engineering", "specifications", "performance", "design"],
        "environmental": ["sustainability", "carbon", "ESG", "climate"]
    }
    
    keywords = base_keywords + resource_keywords.get(resource_type, []) + report_keywords.get(report_type, [])
    return keywords[:8]  # Return top 8 keywords

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Welcome to GeoSpark AI Analytics Platform",
        "version": "2.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/comprehensive-report")
async def generate_comprehensive_report(request: ComprehensiveReportRequest):
    """Generate comprehensive project reports with dynamic metrics and professional content"""
    try:
        # Calculate realistic metrics based on ALL user inputs
        metrics = calculate_realistic_metrics(request)
        
        # Generate dynamic charts based on actual metrics
        charts_data = generate_dynamic_charts(request, metrics)
        
        # Generate professional report content
        report_content = generate_professional_report_content(request, metrics)
        
        # Generate relevant keywords
        keywords = generate_keywords(request.resource_type, request.report_type)
        
        return JSONResponse({
            "success": True,
            "report": {
                "content": report_content,
                "type": request.report_type,
                "project": {
                    "name": request.project_name,
                    "location": request.location,
                    "resource_type": request.resource_type,
                    "capacity_mw": request.capacity_mw,
                    "developer": request.developer,
                    "country": request.country,
                    "estimated_cost": request.estimated_cost,
                    "timeline_months": request.timeline_months
                },
                "metrics": metrics.dict(),
                "charts": charts_data,
                "sentiment": "positive",
                "keywords": keywords,
                "generated_at": datetime.now().isoformat(),
                "confidence": 0.95
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@app.post("/api/v1/site-analysis")
async def analyze_site(request: SiteAnalysisRequest):
    """Analyze a site for renewable energy potential"""
    try:
        from demo import SiteAnalysisRequest as DemoRequest
        
        demo_request = DemoRequest(
            location=request.location.dict(),
            project_type=request.project_type,
            analysis_depth=request.analysis_depth
        )
        
        result = await demo.analyze_site(demo_request)
        
        return {
            "success": True,
            "analysis": {
                "site_id": result.site_id,
                "location": result.location,
                "overall_score": result.overall_score,
                "solar_potential": result.solar_potential,
                "wind_potential": result.wind_potential,
                "environmental_score": result.environmental_score,
                "regulatory_score": result.regulatory_score,
                "accessibility_score": result.accessibility_score,
                "recommendations": result.recommendations,
                "risks": result.risks,
                "estimated_capacity_mw": result.estimated_capacity_mw,
                "analysis_timestamp": result.analysis_timestamp.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/text-analysis")
async def analyze_text(request: TextAnalysisRequest):
    """Enhanced text analysis that handles comprehensive reports"""
    try:
        if request.analysis_type == "comprehensive_report":
            # Simulate comprehensive report analysis
            return {
                "success": True,
                "analysis": {
                    "analysis_type": "comprehensive_report",
                    "summary": f"COMPREHENSIVE ANALYSIS COMPLETED\n\n{request.text}\n\n---\nThis comprehensive analysis includes financial metrics, technical specifications, and strategic recommendations for the renewable energy project.",
                    "sentiment": "positive",
                    "keywords": ["renewable energy", "financial analysis", "technical feasibility", "sustainability"],
                    "confidence": 0.94,
                    "word_count": len(request.text.split()),
                    "processed_at": datetime.now().isoformat(),
                    "llm_analysis": {
                        "summary": f"COMPREHENSIVE ANALYSIS COMPLETED\n\n{request.text}\n\n---\nThis comprehensive analysis includes financial metrics, technical specifications, and strategic recommendations for the renewable energy project.",
                        "sentiment": "positive",
                        "keywords": ["renewable energy", "financial analysis", "technical feasibility", "sustainability"]
                    }
                }
            }
        else:
            # Use existing analysis logic
            result = await demo.analyze_text(request.text, request.analysis_type)
            return {"success": True, "analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/data-search")
async def search_data(request: DataSearchRequest):
    """Search renewable energy data"""
    try:
        result = await demo.search_data(request.query)
        return {"success": True, "results": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/resource-estimation")
async def estimate_resources(request: ResourceEstimationRequest):
    """Simplified resource estimation for demo (solar/wind/hybrid)."""
    rt = request.resource_type
    if rt == "solar":
        estimation = {
            "resource_type": "solar",
            "annual_generation_gwh": 200.0,
            "capacity_factor": 0.22,
            "peak_power_mw": 100.0,
            "seasonal_variation": {"summer": 1.2, "winter": 0.8, "spring": 1.0, "fall": 0.9},
            "uncertainty_range": [180.0, 220.0],
            "confidence_level": 0.85,
            "data_quality_score": 0.9,
        }
    elif rt == "wind":
        estimation = {
            "resource_type": "wind",
            "annual_generation_gwh": 150.0,
            "capacity_factor": 0.35,
            "peak_power_mw": 50.0,
            "seasonal_variation": {"summer": 0.9, "winter": 1.3, "spring": 1.1, "fall": 1.0},
            "uncertainty_range": [130.0, 170.0],
            "confidence_level": 0.80,
            "data_quality_score": 0.85,
        }
    elif rt == "hybrid":
        solar = {"annual_generation_gwh": 200.0, "capacity_factor": 0.22, "peak_power_mw": 100.0,
                 "seasonal_variation": {"summer": 1.2, "winter": 0.8, "spring": 1.0, "fall": 0.9},
                 "uncertainty_range": [180.0, 220.0], "confidence_level": 0.85, "data_quality_score": 0.9}
        wind = {"annual_generation_gwh": 150.0, "capacity_factor": 0.35, "peak_power_mw": 50.0,
                "seasonal_variation": {"summer": 0.9, "winter": 1.3, "spring": 1.1, "fall": 1.0},
                "uncertainty_range": [130.0, 170.0], "confidence_level": 0.80, "data_quality_score": 0.85}
        peak_power_mw = solar["peak_power_mw"] + wind["peak_power_mw"]
        capacity_factor = (solar["capacity_factor"] * solar["peak_power_mw"] + wind["capacity_factor"] * wind["peak_power_mw"]) / peak_power_mw
        estimation = {
            "resource_type": "hybrid",
            "annual_generation_gwh": solar["annual_generation_gwh"] + wind["annual_generation_gwh"],
            "capacity_factor": capacity_factor,
            "peak_power_mw": peak_power_mw,
            "seasonal_variation": {k: (solar["seasonal_variation"][k] + wind["seasonal_variation"][k]) / 2 for k in ["summer", "winter", "spring", "fall"]},
            "uncertainty_range": [solar["uncertainty_range"][0] + wind["uncertainty_range"][0], solar["uncertainty_range"][1] + wind["uncertainty_range"][1]],
            "confidence_level": min(solar["confidence_level"], wind["confidence_level"]),
            "data_quality_score": (solar["data_quality_score"] + wind["data_quality_score"]) / 2,
        }
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported resource type: {rt}")

    return {"success": True, "estimation": estimation, "message": f"{rt.title()} resource estimation completed"}

@app.post("/api/v1/cost-evaluation")
async def evaluate_costs(request: CostEvaluationRequest):
    project_type = request.project_data.get("project_type", "solar")
    capacity_mw = float(request.project_data.get("capacity_mw", 100))
    if project_type == "solar":
        capex_per_mw = 1000000
        opex_per_mw = 15000
    elif project_type == "wind":
        capex_per_mw = 1500000
        opex_per_mw = 25000
    else:
        capex_per_mw = 1200000
        opex_per_mw = 20000
    total_capex = capacity_mw * capex_per_mw
    annual_opex = capacity_mw * opex_per_mw
    electricity_price = float(request.financial_params.get("electricity_price_usd_mwh", 50))
    annual_generation_gwh = float(request.project_data.get("annual_generation_gwh", 200))
    annual_revenue = annual_generation_gwh * electricity_price * 1000
    project_lifetime = int(request.financial_params.get("project_lifetime", 25))
    discount_rate = float(request.financial_params.get("discount_rate", 0.08))
    npv = -total_capex
    for year in range(1, project_lifetime + 1):
        npv += (annual_revenue - annual_opex) / ((1 + discount_rate) ** year)
    irr = (annual_revenue - annual_opex) / total_capex if total_capex else 0
    evaluation_result = {
        "project_type": project_type,
        "capacity_mw": capacity_mw,
        "total_capex_usd": total_capex,
        "annual_opex_usd": annual_opex,
        "annual_revenue_usd": annual_revenue,
        "project_lifetime_years": project_lifetime,
        "discount_rate": discount_rate,
        "financial_metrics": {
            "net_present_value_usd": npv,
            "internal_rate_of_return": irr,
            "payback_period_years": (total_capex / (annual_revenue - annual_opex)) if (annual_revenue - annual_opex) else None,
            "levelized_cost_of_energy_usd_mwh": (total_capex / (annual_generation_gwh * project_lifetime)) if (annual_generation_gwh and project_lifetime) else None,
        },
    }
    return {"success": True, "evaluation": evaluation_result, "message": "Cost evaluation completed"}

@app.post("/api/v1/agent-chat")
async def agent_chat(req: AgentChatRequest):
    """Lightweight agent that can answer questions and run workflows based on the prompt.
    It optionally geocodes the provided city (client may also pass lat/lon later).
    """
    msg = (req.message or "").lower()
    resource_type = (req.resource_type or "solar").lower()

    # Try to geocode if city provided
    lat = None
    lon = None
    if req.city:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"format": "json", "q": req.city, "limit": 1},
                    headers={"User-Agent": "geospark-demo"}  # ✅ required
                )
                data = await r.json()  # ✅ must await here
                if data:
                    lat = float(data[0]["lat"])
                    lon = float(data[0]["lon"])
        except Exception:
            pass

    # If user forces chat mode, answer directly
    if (req.mode or "").lower() == "chat":
        from app.services.llm_service import LLMProvider, LLMRequest, llm_manager, TaskType
        content = (
            f"User asked: {req.message}."
        )
        response = await llm_manager.process_request(LLMRequest(
            task_type=TaskType.NATURAL_LANGUAGE_QUERY,
            prompt=content,
            context={"city": req.city, "resource_type": resource_type},
            provider=LLMProvider.GEMINI,
            model="gemini-1.5-flash",
            max_tokens=800,
            temperature=0.5
        ))
        return {"success": True, "mode": "chat", "message": response.content}

    # If we have coordinates, run the full workflow
    results: Dict[str, Any] = {}
    if lat is not None and lon is not None and ("analy" in msg or "estimate" in msg or "cost" in msg or "report" in msg):
        site_resp = await analyze_site(SiteAnalysisRequest(
            location=Location(latitude=lat, longitude=lon, area_km2=100),
            project_type=resource_type,
            analysis_depth="comprehensive"
        ))
        results["site_analysis"] = site_resp.get("analysis")

        res_resp = await estimate_resources(ResourceEstimationRequest(
            location=ResourceLocation(latitude=lat, longitude=lon, area_km2=100),
            resource_type=resource_type,
            system_config={}
        ))
        results["resource_estimation"] = res_resp.get("estimation")

        cost_resp = await evaluate_costs(CostEvaluationRequest(
            project_data={
                "project_type": resource_type,
                "capacity_mw": results["site_analysis"]["estimated_capacity_mw"],
                "annual_generation_gwh": results["resource_estimation"]["annual_generation_gwh"],
            },
            financial_params={"electricity_price_usd_mwh": 50, "project_lifetime": 25, "discount_rate": 0.08}
        ))
        results["cost_evaluation"] = cost_resp.get("evaluation")

        # Simple text-based report using existing text-analysis
        report_text = (
            f"Generate a brief project report for {req.city} ({lat}, {lon}). Resource: {resource_type}. "
            f"Capacity: {results['site_analysis']['estimated_capacity_mw']} MW. "
            f"Generation: {results['resource_estimation']['annual_generation_gwh']} GWh."
        )
        ta = await analyze_text(TextAnalysisRequest(text=report_text, analysis_type="report"))
        results["report"] = ta.get("analysis")

        return {"success": True, "mode": "workflow", "results": results}

    # Otherwise provide a generic informative response using simple rules
    help_text = (
        "You can ask me to analyze a city (e.g., 'Analyze Kandy solar'), estimate resources, "
        "evaluate costs, or generate a report by including a city name."
    )
    return {"success": True, "mode": "chat", "message": help_text}

@app.get("/api/v1/system-status")
async def get_system_status():
    """Get system status"""
    try:
        status = demo.get_system_status()
        return {"success": True, "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/data-statistics")
async def get_data_statistics():
    """Get data statistics"""
    try:
        stats = demo.get_data_statistics()
        return {"success": True, "statistics": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Register endpoint
@app.post("/api/v1/register")
async def register_user(request: RegisterRequest):
    if request.username in USERS_DB:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Hash password
    hashed_pw = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    USERS_DB[request.username] = {
        "username": request.username,
        "email": request.email,
        "password": hashed_pw
    }
    return {"success": True, "message": "User registered successfully"}

# Authenticate endpoint
@app.post("/api/v1/authenticate")
async def authenticate_user(request: AuthenticationRequest):
    user = USERS_DB.get(request.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not bcrypt.checkpw(request.password.encode('utf-8'), user["password"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate token
    token = str(uuid.uuid4())
    
    return {
        "success": True,
        "token": token,
        "user": {
            "id": "1",  # Demo ID
            "username": user["username"],
            "email": user["email"],
            "role": "user"
        }
    }

@app.post("/api/v1/full-analysis")
async def full_analysis(request: SiteAnalysisRequest):
    """
    Run the full workflow: site analysis, resource estimation, cost evaluation, and report summary.
    Returns plain JSON suitable for frontend consumption.
    """
    try:
        # --- Site Analysis ---
        site_resp = await analyze_site(request)
        site_analysis = site_resp.get("analysis", {})

        # --- Resource Estimation ---
        res_request = ResourceEstimationRequest(
            location=ResourceLocation(**request.location.model_dump()),  # Pydantic v2
            resource_type=request.project_type,
            system_config={}
        )
        res_resp = await estimate_resources(res_request)
        resource_estimation = res_resp.get("estimation", {})

        # --- Cost Evaluation ---
        cost_request = CostEvaluationRequest(
            project_data={
                "project_type": request.project_type,
                "capacity_mw": site_analysis.get("estimated_capacity_mw", 0),
                "annual_generation_gwh": resource_estimation.get("annual_generation_gwh", 0),
            },
            financial_params={"electricity_price_usd_mwh": 50, "project_lifetime": 25, "discount_rate": 0.08}
        )
        cost_resp = await evaluate_costs(cost_request)
        cost_evaluation = cost_resp.get("evaluation", {})

        # --- Simple Text Report ---
        report_text = (
            f"Project report: {request.project_type} project at "
            f"({request.location.latitude}, {request.location.longitude}). "
            f"Capacity: {site_analysis.get('estimated_capacity_mw', 0)} MW. "
            f"Generation: {resource_estimation.get('annual_generation_gwh', 0)} GWh."
        )
        ta_resp = await analyze_text(TextAnalysisRequest(text=report_text, analysis_type="report"))
        report_summary = ta_resp.get("analysis", "")

        # --- Compose workflow ---
        workflow = {
        "site_analysis": dict(site_analysis),          # convert Pydantic to dict
        "resource_estimation": dict(resource_estimation),
        "cost_evaluation": dict(cost_evaluation),
        "report_summary": str(report_summary),
        }
        return {"success": True, "workflow": workflow}


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Full analysis failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)