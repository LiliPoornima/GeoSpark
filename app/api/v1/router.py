"""
API Routes for GeoSpark Renewable Energy System
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
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

# Pydantic models for API requests/responses
class LocationRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    area_km2: float = Field(default=1.0, gt=0, description="Area in square kilometers")

class SiteAnalysisRequest(BaseModel):
    location: LocationRequest
    project_type: str = Field(default="solar", description="Type of renewable energy project")
    analysis_depth: str = Field(default="comprehensive", description="Depth of analysis")

class ResourceEstimationRequest(BaseModel):
    location: LocationRequest
    resource_type: str = Field(default="solar", description="Type of renewable resource")
    system_config: Dict[str, Any] = Field(default={}, description="System configuration parameters")

class CostEvaluationRequest(BaseModel):
    project_data: Dict[str, Any] = Field(..., description="Project data for cost evaluation")
    financial_params: Dict[str, Any] = Field(default={}, description="Financial parameters")

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

@router.post("/site-analysis")
async def analyze_site(
    request: SiteAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Analyze a location for renewable energy potential"""
    try:
        # Get agent manager from global context (would be injected in real implementation)
        # For now, simulate the analysis
        
        location_data = {
            "latitude": request.location.latitude,
            "longitude": request.location.longitude,
            "area_km2": request.location.area_km2
        }
        
        # Simulate site analysis
        analysis_result = {
            "site_id": f"site_{request.location.latitude}_{request.location.longitude}",
            "location": location_data,
            "project_type": request.project_type,
            "analysis_depth": request.analysis_depth,
            "solar_potential": {
                "annual_irradiance_kwh_m2": 4.5,
                "peak_sun_hours": 5.2,
                "capacity_factor": 0.22,
                "solar_score": 0.8
            },
            "wind_potential": {
                "average_wind_speed_ms": 6.5,
                "capacity_factor": 0.35,
                "wind_score": 0.7
            },
            "environmental_score": 0.85,
            "regulatory_score": 0.9,
            "accessibility_score": 0.8,
            "overall_score": 0.8,
            "recommendations": [
                "Excellent solar potential - recommend solar farm development",
                "Good wind potential - consider hybrid renewable energy system"
            ],
            "risks": [
                "Environmental restrictions may limit development",
                "Regulatory challenges may delay project timeline"
            ],
            "estimated_capacity_mw": 100.0,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
        # Log the analysis request
        logger.info(f"Site analysis completed for user {current_user.get('user_id', 'unknown')}")
        
        return {
            "success": True,
            "analysis": analysis_result,
            "message": "Site analysis completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error in site analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resource-estimation")
async def estimate_resources(
    request: ResourceEstimationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Estimate renewable energy resources for a location"""
    try:
        location_data = {
            "latitude": request.location.latitude,
            "longitude": request.location.longitude,
            "area_km2": request.location.area_km2
        }
        
        # Simulate resource estimation
        if request.resource_type == "solar":
            estimation_result = {
                "resource_type": "solar",
                "annual_generation_gwh": 200.0,
                "capacity_factor": 0.22,
                "peak_power_mw": 100.0,
                "seasonal_variation": {
                    "summer": 1.2,
                    "winter": 0.8,
                    "spring": 1.0,
                    "fall": 0.9
                },
                "uncertainty_range": [180.0, 220.0],
                "confidence_level": 0.85,
                "data_quality_score": 0.9
            }
        elif request.resource_type == "wind":
            estimation_result = {
                "resource_type": "wind",
                "annual_generation_gwh": 150.0,
                "capacity_factor": 0.35,
                "peak_power_mw": 50.0,
                "seasonal_variation": {
                    "summer": 0.9,
                    "winter": 1.3,
                    "spring": 1.1,
                    "fall": 1.0
                },
                "uncertainty_range": [130.0, 170.0],
                "confidence_level": 0.80,
                "data_quality_score": 0.85
            }
        elif request.resource_type == "hybrid":
            # Combine solar and wind simple estimates for a hybrid system
            solar = {
                "annual_generation_gwh": 200.0,
                "capacity_factor": 0.22,
                "peak_power_mw": 100.0,
                "seasonal_variation": {
                    "summer": 1.2,
                    "winter": 0.8,
                    "spring": 1.0,
                    "fall": 0.9
                },
                "uncertainty_range": [180.0, 220.0],
                "confidence_level": 0.85,
                "data_quality_score": 0.9
            }
            wind = {
                "annual_generation_gwh": 150.0,
                "capacity_factor": 0.35,
                "peak_power_mw": 50.0,
                "seasonal_variation": {
                    "summer": 0.9,
                    "winter": 1.3,
                    "spring": 1.1,
                    "fall": 1.0
                },
                "uncertainty_range": [130.0, 170.0],
                "confidence_level": 0.80,
                "data_quality_score": 0.85
            }

            estimation_result = {
                "resource_type": "hybrid",
                "annual_generation_gwh": solar["annual_generation_gwh"] + wind["annual_generation_gwh"],
                "capacity_factor": round((solar["capacity_factor"] + wind["capacity_factor"]) / 2, 2),
                "peak_power_mw": solar["peak_power_mw"] + wind["peak_power_mw"],
                "seasonal_variation": {
                    "summer": round((solar["seasonal_variation"]["summer"] + wind["seasonal_variation"]["summer"]) / 2, 2),
                    "winter": round((solar["seasonal_variation"]["winter"] + wind["seasonal_variation"]["winter"]) / 2, 2),
                    "spring": round((solar["seasonal_variation"]["spring"] + wind["seasonal_variation"]["spring"]) / 2, 2),
                    "fall": round((solar["seasonal_variation"]["fall"] + wind["seasonal_variation"]["fall"]) / 2, 2)
                },
                "uncertainty_range": [
                    round(solar["uncertainty_range"][0] + wind["uncertainty_range"][0], 2),
                    round(solar["uncertainty_range"][1] + wind["uncertainty_range"][1], 2)
                ],
                "confidence_level": round((solar["confidence_level"] + wind["confidence_level"]) / 2, 2),
                "data_quality_score": round((solar["data_quality_score"] + wind["data_quality_score"]) / 2, 2)
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported resource type: {request.resource_type}")
        
        return {
            "success": True,
            "estimation": estimation_result,
            "message": f"{request.resource_type.title()} resource estimation completed"
        }
        
    except Exception as e:
        logger.error(f"Error in resource estimation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cost-evaluation")
async def evaluate_costs(
    request: CostEvaluationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Evaluate project costs and financial viability"""
    try:
        # Simulate cost evaluation
        project_type = request.project_data.get("project_type", "solar")
        capacity_mw = request.project_data.get("capacity_mw", 100)
        
        # Calculate costs based on project type and capacity
        if project_type == "solar":
            capex_per_mw = 1000000  # $1M per MW
            opex_per_mw = 15000     # $15K per MW per year
        elif project_type == "wind":
            capex_per_mw = 1500000  # $1.5M per MW
            opex_per_mw = 25000     # $25K per MW per year
        else:
            capex_per_mw = 1200000
            opex_per_mw = 20000
        
        total_capex = capacity_mw * capex_per_mw
        annual_opex = capacity_mw * opex_per_mw
        
        # Calculate revenue (simplified)
        electricity_price = request.financial_params.get("electricity_price_usd_mwh", 50)
        annual_generation_gwh = request.project_data.get("annual_generation_gwh", 200)
        annual_revenue = annual_generation_gwh * electricity_price * 1000  # Convert to USD
        
        # Calculate financial metrics
        project_lifetime = request.financial_params.get("project_lifetime", 25)
        discount_rate = request.financial_params.get("discount_rate", 0.08)
        
        # Simple NPV calculation
        npv = -total_capex
        for year in range(1, project_lifetime + 1):
            npv += (annual_revenue - annual_opex) / ((1 + discount_rate) ** year)
        
        # Simple IRR calculation (simplified)
        irr = (annual_revenue - annual_opex) / total_capex
        
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
                "payback_period_years": total_capex / (annual_revenue - annual_opex),
                "levelized_cost_of_energy_usd_mwh": total_capex / (annual_generation_gwh * project_lifetime),
                "return_on_investment": (annual_revenue - annual_opex) / total_capex,
                "net_annual_cash_flow_usd": annual_revenue - annual_opex
            },
            "cost_breakdown": {
                "equipment": total_capex * 0.6,
                "installation": total_capex * 0.2,
                "grid_connection": total_capex * 0.1,
                "permitting": total_capex * 0.05,
                "engineering": total_capex * 0.05
            },
            "risk_assessment": {
                "resource_risk": "low",
                "regulatory_risk": "medium",
                "market_risk": "low",
                "technology_risk": "low"
            }
        }
        
        return {
            "success": True,
            "evaluation": evaluation_result,
            "message": "Cost evaluation completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error in cost evaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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