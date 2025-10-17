#!/usr/bin/env python3
"""
GeoSpark API Server - Simplified Demo Version
Run this with: python main.py
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,EmailStr
from typing import Dict, Any, List
import json
import asyncio
from datetime import datetime
import uuid
import bcrypt


# Import the demo functionality
from demo import GeoSparkDemo

# In-memory user DB
USERS_DB: Dict[str, Dict] = {}

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
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class AuthenticationRequest(BaseModel):
    username: str
    password: str


# Pydantic models
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
                "analysis_timestamp": result.analysis_timestamp.isoformat(),
                # Protected area flags from demo
                "protected_overlap": getattr(result, "protected_overlap", False),
                "protected_nearby_km": getattr(result, "protected_nearby_km", None),
                "protected_features": getattr(result, "protected_features", []),
                "suitability": getattr(result, "suitability", "suitable"),
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
                r = await client.get("https://nominatim.openstreetmap.org/search", params={
                    "format": "json", "q": req.city, "limit": 1
                })
                data = r.json()
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)