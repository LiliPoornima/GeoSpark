"""
API Routes for GeoSpark Renewable Energy System
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field ,EmailStr
import asyncio

from app.core.security import get_current_user, security_manager
from app.core.database import get_db
from app.services.llm_service import llm_manager
from app.services.nlp_service import nlp_processor
from app.services.ir_service import ir_engine, QueryType, DataSource
from app.agents.communication import AgentCommunicationManager

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Create router
router = APIRouter()

# Initialize agent communication manager
agent_comm_manager = AgentCommunicationManager()

# Pydantic models for API requests/responses
class LocationRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    area_km2: float = Field(default=1.0, gt=0, description="Area in square kilometers")

class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to analyze")
    analysis_type: str = Field(default="comprehensive", description="Type of analysis to perform")

class DataSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    query_type: str = Field(default="site_analysis", description="Type of data to search")
    location: Optional[LocationRequest] = Field(default=None, description="Location filter")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of results")

class AuthenticationRequest(BaseModel):
    username: str = Field(..., min_length=1, description="Username")
    password: str = Field(..., min_length=1, description="Password")

# API Endpoints

@router.post("/text-analysis")
async def analyze_text(
    request: TextAnalysisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Analyze text using NLP techniques"""
    try:
        # Sanitize input
        clean_text, sanitized_text, scan_result = await security_manager.scan_input(
            request.text, "text_analysis", "unknown"
        )
        
        if not clean_text:
            raise HTTPException(status_code=400, detail="Text contains malicious content")
        
        # Perform NLP analysis
        analysis_result = await nlp_processor.process_renewable_energy_document(sanitized_text)
        
        return {
            "success": True,
            "analysis": analysis_result,
            "scan_result": scan_result,
            "message": "Text analysis completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error in text analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/data-search")
async def search_data(
    request: DataSearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Search for renewable energy data"""
    try:
        # Convert query type string to enum
        query_type_map = {
            "solar_resource": QueryType.SOLAR_RESOURCE,
            "wind_resource": QueryType.WIND_RESOURCE,
            "weather_data": QueryType.WEATHER_DATA,
            "grid_connection": QueryType.GRID_CONNECTION,
            "regulatory_info": QueryType.REGULATORY_INFO,
            "environmental_data": QueryType.ENVIRONMENTAL_DATA,
            "financial_data": QueryType.FINANCIAL_DATA,
            "site_analysis": QueryType.SITE_ANALYSIS
        }
        
        query_type = query_type_map.get(request.query_type, QueryType.SITE_ANALYSIS)
        
        # Prepare location filter
        location_filter = None
        if request.location:
            location_filter = {
                "latitude": request.location.latitude,
                "longitude": request.location.longitude
            }
        
        # Perform search
        search_result = await ir_engine.search_data(
            query=request.query,
            query_type=query_type,
            location=location_filter,
            limit=request.limit
        )
        
        # Convert results to API format
        results = []
        for data_point in search_result.results:
            results.append({
                "id": data_point.id,
                "source": data_point.source.value,
                "data_type": data_point.data_type,
                "location": data_point.location,
                "timestamp": data_point.timestamp.isoformat(),
                "data": data_point.data,
                "metadata": data_point.metadata,
                "quality_score": data_point.quality_score
            })
        
        return {
            "success": True,
            "query": request.query,
            "query_type": request.query_type,
            "results": results,
            "total_results": search_result.total_results,
            "search_time_ms": search_result.search_time_ms,
            "confidence_score": search_result.confidence_score,
            "message": "Data search completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error in data search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/llm-analysis")
async def llm_analysis(
    request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Perform LLM-based analysis"""
    try:
        analysis_type = request.get("analysis_type", "comprehensive")
        data = request.get("data", {})
        
        # Perform LLM analysis
        analysis_result = await llm_manager.analyze_renewable_energy_data(data, analysis_type)
        
        return {
            "success": True,
            "analysis": analysis_result,
            "analysis_type": analysis_type,
            "message": "LLM analysis completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error in LLM analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-report")
async def generate_report(
    request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate comprehensive project report"""
    try:
        project_data = request.get("project_data", {})
        
        # Generate report using LLM
        report_content = await llm_manager.generate_project_report(project_data)
        
        return {
            "success": True,
            "report": report_content,
            "generated_at": datetime.utcnow().isoformat(),
            "message": "Report generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/authenticate")
async def authenticate_user(request: AuthenticationRequest):
    """Authenticate user"""
    try:
        credentials = {
            "username": request.username,
            "password": request.password
        }
        
        # Use security manager for authentication
        success, token, result = await security_manager.authenticate_user(
            credentials, "unknown"  # IP would be extracted from request in real implementation
        )
        
        if success:
            return {
                "success": True,
                "token": token,
                "user_id": result.get("user_id"),
                "expires_at": result.get("expires_at"),
                "message": "Authentication successful"
            }
        else:
            raise HTTPException(status_code=401, detail=result.get("error", "Authentication failed"))
            
    except Exception as e:
        logger.error(f"Error in authentication: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-status")
async def get_system_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get system status and health"""
    try:
        # Get data statistics
        data_stats = await ir_engine.get_data_statistics()
        
        # Get LLM usage stats
        llm_stats = llm_manager.get_usage_stats()
        
        # Get available models
        available_models = llm_manager.get_available_models()
        
        status = {
            "system_status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "llm_service": {
                    "status": "operational",
                    "providers_available": len(available_models),
                    "usage_stats": llm_stats
                },
                "nlp_service": {
                    "status": "operational" if nlp_processor.initialized else "error",
                    "models_loaded": nlp_processor.nlp is not None
                },
                "ir_service": {
                    "status": "operational" if ir_engine.initialized else "error",
                    "data_statistics": data_stats
                },
                "security_service": {
                    "status": "operational",
                    "active_policies": len(security_manager.security_policies)
                }
            },
            "available_models": available_models
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data-statistics")
async def get_data_statistics(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get data statistics"""
    try:
        stats = await ir_engine.get_data_statistics()
        return {
            "success": True,
            "statistics": stats,
            "message": "Data statistics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting data statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-cache")
async def clear_cache(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Clear system cache"""
    try:
        await ir_engine.clear_cache()
        return {
            "success": True,
            "message": "Cache cleared successfully"
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    from pydantic import BaseModel, EmailStr
from fastapi import status

# For demo, simple in-memory store
USERS_DB = {}

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(request: RegisterRequest):
    if request.username in USERS_DB:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Save user in the in-memory DB (replace with real DB logic)
    USERS_DB[request.username] = {
        "username": request.username,
        "email": request.email,
        "password": request.password,  # For production: hash this!
    }
    return {
        "success": True,
        "message": "User registered successfully",
        "user": {
            "username": request.username,
            "email": request.email
        }
    }
