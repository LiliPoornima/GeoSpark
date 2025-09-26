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

@app.post("/api/v1/data-search")
async def search_data(request: DataSearchRequest):
    """Search renewable energy data"""
    try:
        result = await demo.search_data(request.query)
        return {"success": True, "results": result}
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