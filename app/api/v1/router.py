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
from app.agents.site_selection import SiteSelectionAgent

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Create router
router = APIRouter()

# Initialize agent communication manager and site selection agent
agent_comm_manager = AgentCommunicationManager()
site_agent = SiteSelectionAgent(agent_comm_manager)

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
    """Analyze a location for renewable energy potential using real data from NASA POWER API"""
    try:
        logger.info(f"Site analysis request for lat: {request.location.latitude}, lon: {request.location.longitude}")
        
        # Prepare location data for the agent
        location_data = {
            "latitude": request.location.latitude,
            "longitude": request.location.longitude,
            "area_km2": request.location.area_km2
        }
        
        # Use the SiteSelectionAgent to perform actual analysis with real APIs
        analysis = await site_agent.analyze_location(location_data)
        
        # Convert the dataclass to a dictionary
        analysis_result = {
            "site_id": analysis.site_id,
            "location": analysis.location,
            "area_km2": analysis.area_km2,
            "project_type": request.project_type,
            "analysis_depth": request.analysis_depth,
            "solar_potential": analysis.solar_potential,
            "wind_potential": analysis.wind_potential,
            "environmental_score": analysis.environmental_score,
            "regulatory_score": analysis.regulatory_score,
            "accessibility_score": analysis.accessibility_score,
            "overall_score": analysis.overall_score,
            "recommendations": analysis.recommendations,
            "risks": analysis.risks,
            "estimated_capacity_mw": analysis.estimated_capacity_mw,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
        # Log the analysis completion
        logger.info(f"Site analysis completed - Overall score: {analysis.overall_score:.2f}, Capacity: {analysis.estimated_capacity_mw:.1f}MW")
        
        return {
            "success": True,
            "analysis": analysis_result,
            "message": "Site analysis completed successfully using real data from NASA POWER API"
        }
        
    except ValueError as ve:
        logger.error(f"Validation error in site analysis: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in site analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/resource-estimation")
async def estimate_resources(
    request: ResourceEstimationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Estimate renewable energy resources for a location using real data"""
    try:
        logger.info(f"Resource estimation request for {request.resource_type} at lat: {request.location.latitude}, lon: {request.location.longitude}")
        
        location_data = {
            "latitude": request.location.latitude,
            "longitude": request.location.longitude,
            "area_km2": request.location.area_km2
        }
        
        # Use the SiteSelectionAgent to get actual solar and wind data
        analysis = await site_agent.analyze_location(location_data)
        
        # Extract the relevant potential data
        if request.resource_type == "solar":
            solar_potential = analysis.solar_potential
            capacity_factor = solar_potential.get("capacity_factor", 0.20)
            peak_sun_hours = solar_potential.get("peak_sun_hours", 4.5)
            
            # Calculate realistic capacity based on area
            # Utility-scale solar: 100-150 MW/km²
            solar_capacity_mw = request.location.area_km2 * 130 * capacity_factor / 0.2
            
            # Annual generation: Capacity × Capacity Factor × 8760 hours
            annual_generation_gwh = solar_capacity_mw * capacity_factor * 8.76  # 8760/1000
            
            # Seasonal variation based on latitude
            lat = abs(request.location.latitude)
            if lat < 23.5:  # Tropics
                seasonal_var = {"summer": 1.05, "winter": 0.95, "spring": 1.0, "fall": 1.0}
            elif lat < 45:  # Temperate
                seasonal_var = {"summer": 1.3, "winter": 0.7, "spring": 1.0, "fall": 1.0}
            else:  # High latitude
                seasonal_var = {"summer": 1.5, "winter": 0.5, "spring": 1.0, "fall": 1.0}
            
            estimation_result = {
                "resource_type": "solar",
                "annual_generation_gwh": round(annual_generation_gwh, 2),
                "capacity_factor": round(capacity_factor, 3),
                "peak_power_mw": round(solar_capacity_mw, 2),
                "peak_sun_hours": round(peak_sun_hours, 2),
                "annual_irradiance_kwh_m2": solar_potential.get("annual_irradiance_kwh_m2", 4.5),
                "seasonal_variation": seasonal_var,
                "uncertainty_range": [
                    round(annual_generation_gwh * 0.9, 2),
                    round(annual_generation_gwh * 1.1, 2)
                ],
                "confidence_level": 0.85 if solar_potential.get("solar_score", 0) > 0.7 else 0.75,
                "data_quality_score": 0.90,
                "data_source": "NASA POWER API satellite measurements"
            }
            
        elif request.resource_type == "wind":
            wind_potential = analysis.wind_potential
            capacity_factor = wind_potential.get("capacity_factor", 0.30)
            wind_speed = wind_potential.get("average_wind_speed_ms", 6.0)
            
            # Calculate realistic capacity based on area
            # Wind farms: 5-10 MW/km² (modern turbines)
            wind_capacity_mw = request.location.area_km2 * 7.5 * capacity_factor / 0.3
            
            # Annual generation: Capacity × Capacity Factor × 8760 hours
            annual_generation_gwh = wind_capacity_mw * capacity_factor * 8.76
            
            # Seasonal variation - wind is typically stronger in winter
            seasonal_var = {
                "summer": 0.85,
                "winter": 1.25,
                "spring": 1.05,
                "fall": 0.95
            }
            
            estimation_result = {
                "resource_type": "wind",
                "annual_generation_gwh": round(annual_generation_gwh, 2),
                "capacity_factor": round(capacity_factor, 3),
                "peak_power_mw": round(wind_capacity_mw, 2),
                "average_wind_speed_ms": wind_speed,
                "wind_speed_10m": wind_potential.get("wind_speed_10m", wind_speed * 0.74),
                "seasonal_variation": seasonal_var,
                "uncertainty_range": [
                    round(annual_generation_gwh * 0.85, 2),
                    round(annual_generation_gwh * 1.15, 2)
                ],
                "confidence_level": 0.80 if wind_potential.get("wind_score", 0) > 0.6 else 0.70,
                "data_quality_score": 0.85,
                "data_source": "NASA POWER API satellite measurements"
            }
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported resource type: {request.resource_type}. Supported types: solar, wind"
            )
        
        logger.info(f"Resource estimation completed - {request.resource_type}: {annual_generation_gwh:.1f} GWh/year")
        
        return {
            "success": True,
            "estimation": estimation_result,
            "message": f"{request.resource_type.title()} resource estimation completed using real NASA data"
        }
        
    except ValueError as ve:
        logger.error(f"Validation error in resource estimation: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in resource estimation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Resource estimation failed: {str(e)}")

@router.post("/cost-evaluation")
async def evaluate_costs(
    request: CostEvaluationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Evaluate project costs and financial viability using industry-standard formulas"""
    try:
        logger.info("Cost evaluation request received")
        
        project_type = request.project_data.get("project_type", "solar")
        capacity_mw = request.project_data.get("capacity_mw", 100)
        capacity_factor = request.project_data.get("capacity_factor", 0.22 if project_type == "solar" else 0.30)
        
        # 2024-2025 Industry-standard costs (USD)
        # Source: NREL, IRENA, BloombergNEF
        if project_type == "solar":
            # Utility-scale solar PV costs
            capex_per_mw = 900000    # $900k/MW (2024 average, down from $1M)
            opex_per_mw_year = 12000  # $12k/MW/year (O&M)
            lifetime_years = 25
        elif project_type == "wind":
            # Onshore wind costs
            capex_per_mw = 1350000   # $1.35M/MW (2024 average)
            opex_per_mw_year = 42000  # $42k/MW/year (higher maintenance)
            lifetime_years = 25
        else:
            # Generic renewable energy project
            capex_per_mw = 1000000
            opex_per_mw_year = 20000
            lifetime_years = 25
        
        # Calculate total costs
        total_capex = capacity_mw * capex_per_mw
        annual_opex = capacity_mw * opex_per_mw_year
        
        # Calculate revenue
        electricity_price = request.financial_params.get("electricity_price_usd_mwh", 60)  # Updated 2024 avg
        
        # Annual generation = Capacity (MW) × Capacity Factor × 8760 hours
        annual_generation_mwh = capacity_mw * capacity_factor * 8760
        annual_generation_gwh = annual_generation_mwh / 1000
        annual_revenue = annual_generation_mwh * electricity_price
        
        # Financial parameters
        project_lifetime = request.financial_params.get("project_lifetime", lifetime_years)
        discount_rate = request.financial_params.get("discount_rate", 0.08)
        inflation_rate = request.financial_params.get("inflation_rate", 0.02)
        
        # Calculate Net Present Value (NPV)
        npv = -total_capex
        cumulative_cash_flow = -total_capex
        payback_year = None
        
        for year in range(1, project_lifetime + 1):
            # Account for inflation in electricity prices
            year_revenue = annual_revenue * ((1 + inflation_rate) ** year)
            year_opex = annual_opex * ((1 + inflation_rate) ** year)
            net_cash_flow = year_revenue - year_opex
            
            # Discount to present value
            pv_cash_flow = net_cash_flow / ((1 + discount_rate) ** year)
            npv += pv_cash_flow
            
            # Track payback period
            cumulative_cash_flow += net_cash_flow
            if payback_year is None and cumulative_cash_flow > 0:
                payback_year = year
        
        # Calculate Internal Rate of Return (IRR) using Newton-Raphson
        def calculate_npv_at_rate(rate):
            npv_calc = -total_capex
            for year in range(1, project_lifetime + 1):
                year_revenue = annual_revenue * ((1 + inflation_rate) ** year)
                year_opex = annual_opex * ((1 + inflation_rate) ** year)
                npv_calc += (year_revenue - year_opex) / ((1 + rate) ** year)
            return npv_calc
        
        # Simple IRR approximation
        irr_guess = 0.10
        for _ in range(20):  # Newton-Raphson iterations
            npv_at_guess = calculate_npv_at_rate(irr_guess)
            npv_at_guess_plus = calculate_npv_at_rate(irr_guess + 0.001)
            derivative = (npv_at_guess_plus - npv_at_guess) / 0.001
            if abs(derivative) < 0.01:
                break
            irr_guess = irr_guess - npv_at_guess / derivative
            if irr_guess < -0.5 or irr_guess > 1.0:
                irr_guess = (annual_revenue - annual_opex) / total_capex  # Fallback
                break
        
        irr = max(0, min(1, irr_guess))
        
        # Calculate Levelized Cost of Energy (LCOE)
        total_lifetime_generation = annual_generation_mwh * project_lifetime
        total_lifetime_costs_pv = total_capex
        for year in range(1, project_lifetime + 1):
            year_opex = annual_opex * ((1 + inflation_rate) ** year)
            total_lifetime_costs_pv += year_opex / ((1 + discount_rate) ** year)
        
        lcoe = (total_lifetime_costs_pv / total_lifetime_generation) if total_lifetime_generation > 0 else 0
        
        # Payback period (simple)
        net_annual_cash_flow = annual_revenue - annual_opex
        simple_payback = total_capex / net_annual_cash_flow if net_annual_cash_flow > 0 else 999
        
        evaluation_result = {
            "project_type": project_type,
            "capacity_mw": capacity_mw,
            "capacity_factor": capacity_factor,
            "total_capex_usd": round(total_capex, 2),
            "annual_opex_usd": round(annual_opex, 2),
            "annual_generation_gwh": round(annual_generation_gwh, 2),
            "annual_revenue_usd": round(annual_revenue, 2),
            "net_annual_cash_flow_usd": round(net_annual_cash_flow, 2),
            "project_lifetime_years": project_lifetime,
            "electricity_price_usd_mwh": electricity_price,
            "discount_rate": discount_rate,
            "financial_metrics": {
                "net_present_value_usd": round(npv, 2),
                "internal_rate_of_return": round(irr, 4),
                "payback_period_years": round(simple_payback, 1) if simple_payback < 999 else "N/A",
                "discounted_payback_years": payback_year if payback_year else "N/A",
                "levelized_cost_of_energy_usd_mwh": round(lcoe, 2),
                "return_on_investment": round((annual_revenue - annual_opex) / total_capex, 4)
            },
            "cost_breakdown": {
                "equipment_usd": round(total_capex * 0.55, 2),  # Panels/turbines
                "installation_usd": round(total_capex * 0.20, 2),  # Labor, construction
                "grid_connection_usd": round(total_capex * 0.12, 2),  # Transmission infrastructure
                "permitting_legal_usd": round(total_capex * 0.06, 2),  # Permits, legal fees
                "engineering_development_usd": round(total_capex * 0.07, 2)  # Design, project dev
            },
            "risk_assessment": {
                "resource_risk": "low" if capacity_factor > 0.25 else "medium",
                "regulatory_risk": "medium",  # Always some uncertainty
                "market_risk": "low" if electricity_price > 50 else "medium",
                "technology_risk": "low",  # Proven technologies
                "financial_viability": "good" if npv > 0 and irr > discount_rate else "marginal" if npv > -total_capex * 0.2 else "poor"
            },
            "recommendations": [
                "✅ Project is financially viable" if npv > 0 else "⚠️ Project shows negative NPV",
                f"💰 LCOE of ${lcoe:.2f}/MWh vs market price ${electricity_price}/MWh",
                f"📊 IRR of {irr*100:.1f}% vs discount rate {discount_rate*100:.1f}%",
                "🔋 Consider battery storage for additional revenue" if capacity_factor < 0.3 else "⚡ Excellent capacity factor"
            ],
            "data_source": "Industry-standard 2024-2025 cost data (NREL, IRENA, BloombergNEF)"
        }
        
        logger.info(f"Cost evaluation completed - NPV: ${npv:,.0f}, IRR: {irr*100:.1f}%")
        
        return {
            "success": True,
            "evaluation": evaluation_result,
            "message": "Cost evaluation completed using industry-standard formulas and 2024-2025 cost data"
        }
        
    except ZeroDivisionError:
        logger.error("Invalid input: Division by zero in financial calculations")
        raise HTTPException(status_code=400, detail="Invalid financial parameters: Check capacity and generation values")
    except Exception as e:
        logger.error(f"Error in cost evaluation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Cost evaluation failed: {str(e)}")

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
