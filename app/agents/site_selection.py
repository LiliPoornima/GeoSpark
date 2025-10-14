"""
Site Selection Agent for Renewable Energy Analysis
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, Polygon
import requests
from dataclasses import dataclass

from app.agents.communication import BaseAgent, AgentMessage, MessagePriority
from app.core.logging import agent_logger

logger = logging.getLogger(__name__)

@dataclass
class SiteCriteria:
    """Criteria for site selection"""
    min_area_km2: float = 1.0
    max_area_km2: float = 1000.0
    min_solar_irradiance: float = 4.0  # kWh/m²/day
    min_wind_speed: float = 5.0  # m/s
    max_distance_to_grid: float = 50.0  # km
    min_distance_to_residential: float = 1.0  # km
    max_elevation: float = 2000.0  # meters
    min_flatness_score: float = 0.7  # 0-1 scale
    environmental_sensitivity: bool = True
    regulatory_restrictions: bool = True

@dataclass
class SiteAnalysis:
    """Results of site analysis"""
    site_id: str
    location: Dict[str, float]  # lat, lon
    area_km2: float
    solar_potential: Dict[str, float]
    wind_potential: Dict[str, float]
    environmental_score: float
    regulatory_score: float
    accessibility_score: float
    overall_score: float
    recommendations: List[str]
    risks: List[str]
    estimated_capacity_mw: float

class SiteSelectionAgent(BaseAgent):
    """Agent responsible for analyzing and selecting optimal renewable energy sites"""
    
    def __init__(self, communication_manager):
        super().__init__("site_selection", communication_manager)
        
        # Define capabilities
        self.capabilities.add_capability("geospatial_analysis")
        self.capabilities.add_capability("site_evaluation")
        self.capabilities.add_capability("environmental_assessment")
        self.capabilities.add_capability("regulatory_compliance")
        
        # Register message handlers
        self.register_handler("analyze_location", self._handle_analyze_location)
        self.register_handler("evaluate_site", self._handle_evaluate_site)
        self.register_handler("compare_sites", self._handle_compare_sites)
        self.register_handler("get_site_recommendations", self._handle_get_recommendations)
        
        # External API configurations
        self.solar_api_url = "https://api.solar.com/v1/irradiance"
        self.wind_api_url = "https://api.wind.com/v1/speed"
        self.elevation_api_url = "https://api.elevation.com/v1/elevation"
        
    async def analyze_location(self, location_data: Dict[str, Any]) -> SiteAnalysis:
        """Analyze a specific location for renewable energy potential"""
        try:
            # Extract location information
            lat = location_data.get("latitude")
            lon = location_data.get("longitude")
            area_km2 = location_data.get("area_km2", 1.0)
            
            if not lat or not lon:
                raise ValueError("Latitude and longitude are required")
            
            # Create site ID
            site_id = f"site_{lat}_{lon}_{datetime.utcnow().timestamp()}"
            
            # Perform comprehensive analysis
            solar_data = await self._analyze_solar_potential(lat, lon)
            wind_data = await self._analyze_wind_potential(lat, lon)
            environmental_score = await self._assess_environmental_factors(lat, lon, area_km2)
            regulatory_score = await self._assess_regulatory_compliance(lat, lon)
            accessibility_score = await self._assess_accessibility(lat, lon)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(
                solar_data, wind_data, environmental_score, 
                regulatory_score, accessibility_score
            )
            
            # Generate recommendations and identify risks
            recommendations = self._generate_recommendations(
                solar_data, wind_data, environmental_score, regulatory_score
            )
            risks = self._identify_risks(
                solar_data, wind_data, environmental_score, regulatory_score
            )
            
            # Estimate capacity
            estimated_capacity = self._estimate_capacity(
                area_km2, solar_data, wind_data
            )
            
            # Log decision
            agent_logger.log_agent_decision(
                self.agent_id,
                f"Site analysis completed for {lat}, {lon}",
                f"Overall score: {overall_score:.2f}, Capacity: {estimated_capacity:.1f}MW"
            )
            
            return SiteAnalysis(
                site_id=site_id,
                location={"latitude": lat, "longitude": lon},
                area_km2=area_km2,
                solar_potential=solar_data,
                wind_potential=wind_data,
                environmental_score=environmental_score,
                regulatory_score=regulatory_score,
                accessibility_score=accessibility_score,
                overall_score=overall_score,
                recommendations=recommendations,
                risks=risks,
                estimated_capacity_mw=estimated_capacity
            )
            
        except Exception as e:
            logger.error(f"Error analyzing location: {e}")
            agent_logger.log_agent_error(self.agent_id, str(e), location_data)
            raise
    
    async def _analyze_solar_potential(self, lat: float, lon: float) -> Dict[str, float]:
        """Analyze solar energy potential for a location"""
        try:
            # In a real implementation, this would call external APIs
            # For now, we'll use simplified calculations
            
            # Simulate API call for solar irradiance
            response = requests.get(
                f"{self.solar_api_url}?lat={lat}&lon={lon}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                annual_irradiance = data.get("annual_irradiance", 4.5)
                peak_sun_hours = data.get("peak_sun_hours", 5.2)
            else:
                # Fallback calculation based on latitude
                annual_irradiance = max(2.0, 6.0 - abs(lat) * 0.05)
                peak_sun_hours = annual_irradiance * 0.8
            
            # Calculate solar potential metrics
            solar_efficiency = 0.22  # Typical solar panel efficiency
            capacity_factor = peak_sun_hours / 24.0
            
            return {
                "annual_irradiance_kwh_m2": annual_irradiance,
                "peak_sun_hours": peak_sun_hours,
                "capacity_factor": capacity_factor,
                "solar_efficiency": solar_efficiency,
                "solar_score": min(1.0, annual_irradiance / 6.0)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing solar potential: {e}")
            # Return default values
            return {
                "annual_irradiance_kwh_m2": 4.0,
                "peak_sun_hours": 4.5,
                "capacity_factor": 0.19,
                "solar_efficiency": 0.22,
                "solar_score": 0.7
            }
    
    async def _analyze_wind_potential(self, lat: float, lon: float) -> Dict[str, float]:
        """Analyze wind energy potential for a location"""
        try:
            # Simulate API call for wind data
            response = requests.get(
                f"{self.wind_api_url}?lat={lat}&lon={lon}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                avg_wind_speed = data.get("average_wind_speed", 6.0)
                wind_direction = data.get("prevailing_direction", 270)
            else:
                # Fallback calculation
                avg_wind_speed = max(3.0, 8.0 - abs(lat) * 0.02)
                wind_direction = 270  # West
            
            # Calculate wind potential metrics
            wind_turbine_efficiency = 0.45  # Typical wind turbine efficiency
            capacity_factor = min(0.5, (avg_wind_speed / 12.0) ** 3)
            
            return {
                "average_wind_speed_ms": avg_wind_speed,
                "prevailing_direction": wind_direction,
                "capacity_factor": capacity_factor,
                "turbine_efficiency": wind_turbine_efficiency,
                "wind_score": min(1.0, avg_wind_speed / 10.0)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing wind potential: {e}")
            return {
                "average_wind_speed_ms": 5.5,
                "prevailing_direction": 270,
                "capacity_factor": 0.25,
                "turbine_efficiency": 0.45,
                "wind_score": 0.6
            }
    
    async def _assess_environmental_factors(self, lat: float, lon: float, area_km2: float) -> float:
        """Assess environmental factors affecting site suitability"""
        try:
            # Check for protected areas, wetlands, etc.
            # This would typically involve GIS analysis
            
            # Simulate environmental assessment
            protected_area_penalty = 0.0
            wetland_penalty = 0.0
            forest_penalty = 0.0
            
            # Distance to sensitive areas
            distance_to_protected = 10.0  # km
            distance_to_wetland = 5.0  # km
            
            if distance_to_protected < 5.0:
                protected_area_penalty = 0.3
            if distance_to_wetland < 2.0:
                wetland_penalty = 0.2
            
            # Calculate environmental score
            environmental_score = 1.0 - protected_area_penalty - wetland_penalty - forest_penalty
            
            return max(0.0, environmental_score)
            
        except Exception as e:
            logger.error(f"Error assessing environmental factors: {e}")
            return 0.8  # Default score
    
    async def _assess_regulatory_compliance(self, lat: float, lon: float) -> float:
        """Assess regulatory compliance and restrictions"""
        try:
            # Check zoning regulations, permits required, etc.
            # This would typically involve database queries
            
            # Simulate regulatory assessment
            zoning_score = 0.9  # Most areas allow renewable energy
            permit_complexity = 0.1  # Low complexity
            environmental_review = 0.2  # Standard review required
            
            regulatory_score = zoning_score - permit_complexity - environmental_review
            
            return max(0.0, regulatory_score)
            
        except Exception as e:
            logger.error(f"Error assessing regulatory compliance: {e}")
            return 0.7  # Default score
    
    async def _assess_accessibility(self, lat: float, lon: float) -> float:
        """Assess site accessibility and infrastructure"""
        try:
            # Check distance to roads, transmission lines, etc.
            distance_to_road = 2.0  # km
            distance_to_transmission = 15.0  # km
            terrain_difficulty = 0.1  # 0-1 scale
            
            # Calculate accessibility score
            road_score = max(0.0, 1.0 - distance_to_road / 10.0)
            transmission_score = max(0.0, 1.0 - distance_to_transmission / 50.0)
            terrain_score = 1.0 - terrain_difficulty
            
            accessibility_score = (road_score + transmission_score + terrain_score) / 3.0
            
            return accessibility_score
            
        except Exception as e:
            logger.error(f"Error assessing accessibility: {e}")
            return 0.8  # Default score
    
    def _calculate_overall_score(self, solar_data: Dict[str, float], 
                                wind_data: Dict[str, float],
                                environmental_score: float,
                                regulatory_score: float,
                                accessibility_score: float) -> float:
        """Calculate overall site suitability score"""
        # Weighted scoring system
        weights = {
            "solar": 0.3,
            "wind": 0.2,
            "environmental": 0.2,
            "regulatory": 0.15,
            "accessibility": 0.15
        }
        
        overall_score = (
            solar_data["solar_score"] * weights["solar"] +
            wind_data["wind_score"] * weights["wind"] +
            environmental_score * weights["environmental"] +
            regulatory_score * weights["regulatory"] +
            accessibility_score * weights["accessibility"]
        )
        
        return min(1.0, max(0.0, overall_score))
    
    def _generate_recommendations(self, solar_data: Dict[str, float],
                                 wind_data: Dict[str, float],
                                 environmental_score: float,
                                 regulatory_score: float) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if solar_data["solar_score"] > 0.8:
            recommendations.append("Excellent solar potential - recommend solar farm development")
        elif solar_data["solar_score"] > 0.6:
            recommendations.append("Good solar potential - consider solar development")
        
        if wind_data["wind_score"] > 0.8:
            recommendations.append("Excellent wind potential - recommend wind farm development")
        elif wind_data["wind_score"] > 0.6:
            recommendations.append("Good wind potential - consider wind development")
        
        if environmental_score < 0.7:
            recommendations.append("Environmental concerns - conduct detailed environmental impact assessment")
        
        if regulatory_score < 0.7:
            recommendations.append("Regulatory complexity - engage with local authorities early")
        
        if not recommendations:
            recommendations.append("Site shows moderate potential - consider hybrid renewable energy system")
        
        return recommendations
    
    def _identify_risks(self, solar_data: Dict[str, float],
                       wind_data: Dict[str, float],
                       environmental_score: float,
                       regulatory_score: float) -> List[str]:
        """Identify potential risks"""
        risks = []
        
        if solar_data["solar_score"] < 0.5:
            risks.append("Low solar irradiance may impact project economics")
        
        if wind_data["wind_score"] < 0.5:
            risks.append("Low wind speeds may impact project economics")
        
        if environmental_score < 0.6:
            risks.append("Environmental restrictions may limit development")
        
        if regulatory_score < 0.6:
            risks.append("Regulatory challenges may delay project timeline")
        
        return risks
    
    def _estimate_capacity(self, area_km2: float, solar_data: Dict[str, float],
                          wind_data: Dict[str, float]) -> float:
        """Estimate renewable energy capacity for the site"""
        # Solar capacity estimation
        solar_area_efficiency = 0.8  # 80% of area usable for solar
        solar_power_density = 200  # W/m²
        solar_capacity = (area_km2 * 1000000 * solar_area_efficiency * solar_power_density) / 1000000
        
        # Wind capacity estimation
        wind_area_efficiency = 0.1  # 10% of area usable for wind turbines
        wind_power_density = 5  # MW/km²
        wind_capacity = area_km2 * wind_area_efficiency * wind_power_density
        
        # Return the higher capacity option
        return max(solar_capacity, wind_capacity)
    
    # Message handlers
    async def _handle_analyze_location(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle location analysis requests"""
        location_data = message.content
        analysis = await self.analyze_location(location_data)
        
        return {
            "site_analysis": {
                "site_id": analysis.site_id,
                "location": analysis.location,
                "area_km2": analysis.area_km2,
                "solar_potential": analysis.solar_potential,
                "wind_potential": analysis.wind_potential,
                "environmental_score": analysis.environmental_score,
                "regulatory_score": analysis.regulatory_score,
                "accessibility_score": analysis.accessibility_score,
                "overall_score": analysis.overall_score,
                "recommendations": analysis.recommendations,
                "risks": analysis.risks,
                "estimated_capacity_mw": analysis.estimated_capacity_mw
            }
        }
    
    async def _handle_evaluate_site(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle site evaluation requests"""
        site_data = message.content
        criteria = SiteCriteria(**site_data.get("criteria", {}))
        
        # Perform evaluation based on criteria
        # This would involve more detailed analysis
        return {"evaluation": "Site evaluation completed"}
    
    async def _handle_compare_sites(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle site comparison requests"""
        sites_data = message.content.get("sites", [])
        
        comparisons = []
        for site in sites_data:
            analysis = await self.analyze_location(site)
            comparisons.append({
                "site_id": analysis.site_id,
                "overall_score": analysis.overall_score,
                "estimated_capacity_mw": analysis.estimated_capacity_mw
            })
        
        return {"comparisons": comparisons}
    
    async def _handle_get_recommendations(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle recommendation requests"""
        location_data = message.content
        analysis = await self.analyze_location(location_data)
        
        return {
            "recommendations": analysis.recommendations,
            "risks": analysis.risks,
            "overall_score": analysis.overall_score
        }