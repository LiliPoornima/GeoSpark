#!/usr/bin/env python3
"""
GeoSpark API Server - Simplified Demo Version
Run this with: python main.py
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
import asyncio
from datetime import datetime
import uuid
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app first
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

# Pydantic models
class Location(BaseModel):
    latitude: float
    longitude: float
    area_km2: float = 100

class SiteAnalysisRequest(BaseModel):
    location: Location
    project_type: str = "solar"
    analysis_depth: str = "comprehensive"

class ResourceLocation(BaseModel):
    latitude: float
    longitude: float
    area_km2: float = 100

class ResourceEstimationRequest(BaseModel):
    location: ResourceLocation
    resource_type: str = "solar"
    system_config: Dict[str, Any] = {}

class TextAnalysisRequest(BaseModel):
    text: str
    analysis_type: str = "general"

class DataSearchRequest(BaseModel):
    query: str
    limit: int = 5

class SiteAnalysisResult(BaseModel):
    site_id: str
    location: Dict[str, Any]
    overall_score: float
    solar_potential: float
    wind_potential: float
    environmental_score: float
    regulatory_score: float
    accessibility_score: float
    recommendations: List[str]
    risks: List[str]
    estimated_capacity_mw: float
    analysis_timestamp: datetime

# Demo GeoSpark class (inline implementation)
class GeoSparkDemo:
    def __init__(self):
        logger.info("Initializing GeoSpark Demo...")
        self.system_status = {
            "status": "operational",
            "last_updated": datetime.now(),
            "version": "1.0.0-demo"
        }
        
    async def analyze_site(self, request: SiteAnalysisRequest) -> SiteAnalysisResult:
        """Mock site analysis for demo purposes"""
        # Simulate processing time
        await asyncio.sleep(0.5)
        
        # Generate mock data based on location
        lat = request.location.latitude
        lon = request.location.longitude
        
        # Simple scoring based on latitude (closer to equator = better solar)
        solar_potential = max(0.1, 1.0 - abs(lat) / 90.0)
        wind_potential = 0.3 + (abs(lat) / 90.0) * 0.7  # Higher latitudes = better wind
        
        result = SiteAnalysisResult(
            site_id=f"site_{uuid.uuid4().hex[:8]}",
            location=request.location.dict(),
            overall_score=round((solar_potential + wind_potential) / 2, 2),
            solar_potential=round(solar_potential, 2),
            wind_potential=round(wind_potential, 2),
            environmental_score=0.8,
            regulatory_score=0.7,
            accessibility_score=0.6,
            recommendations=[
                f"Optimal for {request.project_type} energy generation",
                "Consider environmental impact assessment",
                "Verify local regulations and permits"
            ],
            risks=[
                "Weather variability",
                "Regulatory changes",
                "Grid connection challenges"
            ],
            estimated_capacity_mw=round(request.location.area_km2 * 0.5, 2),
            analysis_timestamp=datetime.now()
        )
        
        return result
    
    async def analyze_text(self, text: str, analysis_type: str) -> Dict[str, Any]:
        """Mock text analysis"""
        await asyncio.sleep(0.3)
        
        # Simple text analysis
        word_count = len(text.split())
        char_count = len(text)
        
        # Mock sentiment (based on common positive/negative words)
        positive_words = ["good", "excellent", "great", "positive", "efficient", "sustainable"]
        negative_words = ["bad", "poor", "terrible", "negative", "inefficient", "problematic"]
        
        text_lower = text.lower()
        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)
        
        sentiment = "neutral"
        if positive_score > negative_score:
            sentiment = "positive"
        elif negative_score > positive_score:
            sentiment = "negative"
        
        return {
            "word_count": word_count,
            "character_count": char_count,
            "sentiment": sentiment,
            "positive_indicators": positive_score,
            "negative_indicators": negative_score,
            "analysis_type": analysis_type,
            "processed_at": datetime.now().isoformat()
        }
    
    async def search_data(self, query: str) -> List[Dict[str, Any]]:
        """Mock data search"""
        await asyncio.sleep(0.2)
        
        # Mock search results
        mock_results = [
            {
                "id": f"result_{i}",
                "title": f"Renewable Energy Dataset {i}",
                "description": f"Data related to {query} - Sample dataset {i}",
                "relevance_score": round(1.0 - (i * 0.1), 2),
                "last_updated": datetime.now().isoformat(),
                "source": f"geospark_db_{i}"
            }
            for i in range(1, 6)
        ]
        
        return mock_results
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "status": "operational",
            "uptime": "99.9%",
            "last_updated": datetime.now().isoformat(),
            "version": "1.0.0-demo",
            "active_analyses": 0,
            "total_sites_analyzed": 1247,
            "data_sources_online": 12
        }
    
    def get_data_statistics(self) -> Dict[str, Any]:
        """Get data statistics"""
        return {
            "total_datasets": 156,
            "total_sites": 1247,
            "countries_covered": 89,
            "last_data_update": datetime.now().isoformat(),
            "data_quality_score": 0.94,
            "storage_used_gb": 2.4
        }

# Initialize demo instance
demo = GeoSparkDemo()

# Include full v1 API router if available (enables resource-estimation, cost-evaluation, reports)
try:
    from app.api.v1.router import router as v1_router
    app.include_router(v1_router, prefix="/api/v1")
    logger.info("Loaded v1 API router from app.api.v1.router")
except Exception as e:
    logger.warning(f"v1 router not loaded: {e}")
    # Minimal fallback endpoints for resource estimation to avoid 404 in demo mode
    from fastapi import Body

    class _ResLoc(BaseModel):
        latitude: float
        longitude: float
        area_km2: float = 100

    class _ResReq(BaseModel):
        location: _ResLoc
        resource_type: str = "solar"
        system_config: Dict[str, Any] = {}

    @app.post("/api/v1/resource-estimation")
    async def _fallback_resource_estimation(request: _ResReq = Body(...)):
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
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=f"Unsupported resource type: {rt}")

        return {"success": True, "estimation": estimation, "message": f"{rt.title()} resource estimation completed"}

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Welcome to GeoSpark Demo API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "site_analysis": "/api/v1/site-analysis",
            "text_analysis": "/api/v1/text-analysis",
            "data_search": "/api/v1/data-search",
            "system_status": "/api/v1/system-status",
            "data_statistics": "/api/v1/data-statistics",
            "authenticate": "/api/v1/authenticate"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/site-analysis")
async def analyze_site(request: SiteAnalysisRequest):
    """Analyze a site for renewable energy potential"""
    try:
        logger.info(f"Analyzing site at {request.location.latitude}, {request.location.longitude}")
        result = await demo.analyze_site(request)
        
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
        logger.error(f"Error analyzing site: {e}")
        raise HTTPException(status_code=500, detail=f"Site analysis failed: {str(e)}")

@app.post("/api/v1/text-analysis")
async def analyze_text(request: TextAnalysisRequest):
    """Analyze text using NLP"""
    try:
        logger.info(f"Analyzing text of length {len(request.text)}")
        result = await demo.analyze_text(request.text, request.analysis_type)
        return {"success": True, "analysis": result}
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        raise HTTPException(status_code=500, detail=f"Text analysis failed: {str(e)}")

@app.post("/api/v1/data-search")
async def search_data(request: DataSearchRequest):
    """Search renewable energy data"""
    try:
        logger.info(f"Searching data for: {request.query}")
        result = await demo.search_data(request.query)
        return {"success": True, "results": result[:request.limit]}
    except Exception as e:
        logger.error(f"Error searching data: {e}")
        raise HTTPException(status_code=500, detail=f"Data search failed: {str(e)}")

@app.get("/api/v1/system-status")
async def get_system_status():
    """Get system status"""
    try:
        status = demo.get_system_status()
        return {"success": True, "status": status}
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=f"System status check failed: {str(e)}")

@app.get("/api/v1/data-statistics")
async def get_data_statistics():
    """Get data statistics"""
    try:
        stats = demo.get_data_statistics()
        return {"success": True, "statistics": stats}
    except Exception as e:
        logger.error(f"Error getting data statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Data statistics failed: {str(e)}")

@app.post("/api/v1/authenticate")
async def authenticate(credentials: Dict[str, str]):
    """Mock authentication for demo"""
    try:
        username = credentials.get("username", "")
        password = credentials.get("password", "")
        
        # Demo credentials
        if username == "demo" and password == "demo123":
            logger.info(f"Successful authentication for user: {username}")
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
            logger.warning(f"Failed authentication attempt for user: {username}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=500, detail="Authentication service error")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=404, content={"error": "Not found", "message": "The requested resource was not found"})

@app.exception_handler(500)
async def server_error_handler(request, exc):
    from fastapi.responses import JSONResponse
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(status_code=500, content={"error": "Internal server error", "message": "An unexpected error occurred"})

if __name__ == "__main__":
    print("🚀 Starting GeoSpark Demo API...")
    print("=" * 50)
    print("API Documentation: http://localhost:8000/docs")
    print("Interactive API: http://localhost:8000/redoc")
    print("Health Check: http://localhost:8000/health")
    print("Root Endpoint: http://localhost:8000/")
    print("=" * 50)
    print("Demo Credentials:")
    print("  Username: demo")
    print("  Password: demo123")
    print("=" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )