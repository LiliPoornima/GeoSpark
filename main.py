#!/usr/bin/env python3
"""
GeoSpark API Server - Simplified Demo Version
Run this with: python main.py
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import json
import asyncio
from datetime import datetime
import uuid

# Import the demo functionality
from demo import GeoSparkDemo

app = FastAPI(
    title="GeoSpark Demo API",
    description="AI-powered renewable energy analysis platform - Demo Version",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize demo
demo = GeoSparkDemo()

# Pydantic models
class Location(BaseModel):
    latitude: float
    longitude: float
    area_km2: float = 100

class SiteAnalysisRequest(BaseModel):
    location: Location
    project_type: str = "solar"
    analysis_depth: str = "comprehensive"

class ResourceEstimationRequest(BaseModel):
    location: Location
    resource_type: str = "solar"
    system_config: Dict[str, Any] = {}

class TextAnalysisRequest(BaseModel):
    text: str
    analysis_type: str = "general"

class DataSearchRequest(BaseModel):
    query: str
    limit: int = 5

class CostEvaluationRequest(BaseModel):
    project_data: Dict[str, Any]
    financial_params: Dict[str, Any] = {}

class GenerateReportRequest(BaseModel):
    project_data: Dict[str, Any] = {}

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Welcome to GeoSpark Demo API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

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
    """Analyze text using NLP"""
    try:
        result = await demo.analyze_text(request.text, request.analysis_type)
        return {"success": True, "analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/resource-estimation")
async def estimate_resources(request: ResourceEstimationRequest):
    """Estimate renewable energy resources for a location (demo)."""
    try:
        lat = float(request.location.latitude)
        lon = float(request.location.longitude)
        area = float(request.location.area_km2 or 1.0)

        # Simple deterministic factors from location to vary results
        latitude_factor = 1.0 - min(abs(lat), 90.0) / 90.0 * 0.4  # 1.0 to 0.6
        longitude_variation = (abs(lon) % 30) / 30.0  # 0..1 periodic

        if request.resource_type == "solar":
            density_mw_per_km2 = 5.0
            capacity_factor = round(0.18 + 0.1 * latitude_factor, 2)  # ~0.18 - 0.28
            peak_power_mw = round(max(10.0, area * density_mw_per_km2 * (0.8 + 0.4 * longitude_variation)), 1)
            annual_generation_gwh = round(peak_power_mw * capacity_factor * 8760 / 1000, 1)
            estimation_result = {
                "resource_type": "solar",
                "annual_generation_gwh": annual_generation_gwh,
                "capacity_factor": capacity_factor,
                "peak_power_mw": peak_power_mw,
                "seasonal_variation": {"summer": 1.1 + 0.2 * latitude_factor, "winter": 0.8, "spring": 1.0, "fall": 0.9},
                "uncertainty_range": [round(annual_generation_gwh * 0.9, 1), round(annual_generation_gwh * 1.1, 1)],
                "confidence_level": round(0.8 + 0.1 * latitude_factor, 2),
                "data_quality_score": round(0.85 - 0.05 * (1 - latitude_factor), 2),
            }
        elif request.resource_type == "wind":
            density_mw_per_km2 = 2.0
            wind_factor = 0.9 - 0.3 * (abs(lat) / 90.0) + 0.2 * longitude_variation  # coastal-ish
            capacity_factor = round(0.28 + 0.12 * max(0.5, min(wind_factor, 1.2)), 2)
            peak_power_mw = round(max(10.0, area * density_mw_per_km2 * (0.8 + 0.4 * wind_factor)), 1)
            annual_generation_gwh = round(peak_power_mw * capacity_factor * 8760 / 1000, 1)
            estimation_result = {
                "resource_type": "wind",
                "annual_generation_gwh": annual_generation_gwh,
                "capacity_factor": capacity_factor,
                "peak_power_mw": peak_power_mw,
                "seasonal_variation": {"summer": 0.95, "winter": 1.2, "spring": 1.1, "fall": 1.0},
                "uncertainty_range": [round(annual_generation_gwh * 0.87, 1), round(annual_generation_gwh * 1.13, 1)],
                "confidence_level": round(0.78 + 0.1 * wind_factor, 2),
                "data_quality_score": round(0.82 + 0.03 * wind_factor, 2),
            }
        elif request.resource_type == "hybrid":
            # Compute solar and wind, then combine
            # Solar
            s_density = 5.0
            s_cf = 0.18 + 0.1 * latitude_factor
            s_peak = max(10.0, area * s_density * (0.8 + 0.4 * longitude_variation))
            s_gen = s_peak * s_cf * 8760 / 1000
            # Wind
            w_density = 2.0
            w_factor = 0.9 - 0.3 * (abs(lat) / 90.0) + 0.2 * longitude_variation
            w_cf = 0.28 + 0.12 * max(0.5, min(w_factor, 1.2))
            w_peak = max(10.0, area * w_density * (0.8 + 0.4 * w_factor))
            w_gen = w_peak * w_cf * 8760 / 1000

            annual_generation_gwh = round(s_gen + w_gen, 1)
            peak_power_mw = round(s_peak + w_peak, 1)
            capacity_factor = round(((s_cf + w_cf) / 2), 2)
            estimation_result = {
                "resource_type": "hybrid",
                "annual_generation_gwh": annual_generation_gwh,
                "capacity_factor": capacity_factor,
                "peak_power_mw": peak_power_mw,
                "seasonal_variation": {"summer": 1.0, "winter": 1.0, "spring": 1.05, "fall": 0.95},
                "uncertainty_range": [round(annual_generation_gwh * 0.9, 1), round(annual_generation_gwh * 1.1, 1)],
                "confidence_level": 0.82,
                "data_quality_score": 0.86,
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported resource type: {request.resource_type}")

        return {
            "success": True,
            "estimation": estimation_result,
            "message": f"{request.resource_type.title()} resource estimation completed"
        }
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

@app.post("/api/v1/cost-evaluation")
async def evaluate_costs(request: CostEvaluationRequest):
    """Evaluate project costs and financial viability (demo)."""
    try:
        project_type = request.project_data.get("project_type", "solar")
        capacity_mw = float(request.project_data.get("capacity_mw", 100))

        override_capex = request.financial_params.get("capex_per_mw_override")
        override_opex = request.financial_params.get("opex_per_mw_override")
        if override_capex is not None and override_opex is not None:
            capex_per_mw = float(override_capex)
            opex_per_mw = float(override_opex)
        else:
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

        irr = (annual_revenue - annual_opex) / total_capex if total_capex else 0.0

        evaluation_result = {
            "project_type": project_type,
            "capacity_mw": capacity_mw,
            "total_capex_usd": total_capex,
            "annual_opex_usd": annual_opex,
            "annual_revenue_usd": annual_revenue,
            "net_annual_cash_flow_usd": annual_revenue - annual_opex,
            "project_lifetime_years": project_lifetime,
            "discount_rate": discount_rate,
            "financial_metrics": {
                "net_present_value_usd": npv,
                "internal_rate_of_return": irr,
                "payback_period_years": (total_capex / (annual_revenue - annual_opex)) if (annual_revenue - annual_opex) > 0 else None,
                "levelized_cost_of_energy_usd_mwh": (total_capex / (annual_generation_gwh * project_lifetime)) if (annual_generation_gwh * project_lifetime) > 0 else None,
                "return_on_investment": ((annual_revenue - annual_opex) / total_capex) if total_capex else None,
            },
            "cost_breakdown": {
                "equipment": total_capex * 0.6,
                "installation": total_capex * 0.2,
                "grid_connection": total_capex * 0.1,
                "permitting": total_capex * 0.05,
                "engineering": total_capex * 0.05,
            },
            "risk_assessment": {
                "resource_risk": "low",
                "regulatory_risk": "medium",
                "market_risk": "low",
                "technology_risk": "low",
            },
        }

        return {"success": True, "evaluation": evaluation_result, "message": "Cost evaluation completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/generate-report")
async def generate_report(request: GenerateReportRequest):
    """Generate a simple project report (demo)."""
    try:
        project_type = request.project_data.get("project_type", "solar").title()
        capacity_mw = request.project_data.get("capacity_mw", 100)
        location = request.project_data.get("location", {"latitude": None, "longitude": None})
        financials = request.project_data.get("financials", {})
        npv = financials.get("npv")
        irr = financials.get("irr")
        lcoe = financials.get("lcoe")
        payback = financials.get("payback")
        revenue = financials.get("annual_revenue")
        summary = (
            f"Project Report: {project_type} Facility\n"
            f"Planned Capacity: {capacity_mw} MW\n"
            f"Location: lat={location.get('latitude')}, lon={location.get('longitude')}\n"
            + (f"Annual Revenue: ${revenue:,.0f}\n" if revenue is not None else "")
            + (f"NPV: ${npv:,.0f}\n" if npv is not None else "")
            + (f"IRR: {irr*100:.1f}%\n" if irr is not None else "")
            + (f"LCOE: ${lcoe:,.2f}/MWh\n" if lcoe is not None else "")
            + (f"Payback: {payback:.1f} years\n" if payback is not None else "")
            + f"Summary: The {project_type.lower()} project demonstrates strong potential based on site analysis, "
            f"with favorable capacity factors and manageable risks."
        )

        return {
            "success": True,
            "report": summary,
            "generated_at": datetime.now().isoformat(),
            "message": "Report generated successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@app.post("/api/v1/authenticate")
async def authenticate(credentials: Dict[str, str]):
    """Mock authentication for demo"""
    username = credentials.get("username", "")
    password = credentials.get("password", "")
    
    # Demo credentials
    if username == "demo" and password == "demo123":
        return {
            "success": True,
            "token": "demo_token_" + str(uuid.uuid4()),
            "user": {
                "id": "1",
                "username": username,
                "email": f"{username}@geospark.com",
                "role": "user"
            }
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

if __name__ == "__main__":
    print("🚀 Starting GeoSpark Demo API...")
    print("=" * 40)
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("=" * 40)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
