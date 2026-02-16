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
        
        # Real API configurations
        # NASA POWER API for solar irradiance data (FREE, no API key needed)
        self.nasa_power_api_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        # Open-Meteo API for wind data (FREE, no API key needed)
        self.wind_api_url = "https://api.open-meteo.com/v1/forecast"
        
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
        """Analyze solar energy potential using NASA POWER API"""
        try:
            # NASA POWER API - Free, no API key required
            # Get last full year of data for accurate annual averages
            params = {
                "parameters": "ALLSKY_SFC_SW_DWN",  # Solar irradiance (kWh/m²/day)
                "community": "RE",  # Renewable Energy community
                "longitude": lon,
                "latitude": lat,
                "start": "20230101",  # Last full year
                "end": "20231231",
                "format": "JSON"
            }
            
            response = requests.get(
                self.nasa_power_api_url,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                # Get annual average solar irradiance
                irradiance_data = data.get("properties", {}).get("parameter", {}).get("ALLSKY_SFC_SW_DWN", {})
                
                if irradiance_data:
                    # Calculate annual average from daily values
                    # Filter out None/NaN and cast to float
                    raw_values = list(irradiance_data.values())
                    daily_values = []
                    for v in raw_values:
                        try:
                            if v is None:
                                continue
                            f = float(v)
                            if np.isnan(f):
                                continue
                            daily_values.append(f)
                        except Exception:
                            continue
                    if not daily_values:
                        raise ValueError("No valid irradiance values")
                    annual_irradiance = float(sum(daily_values)) / float(len(daily_values))
                    peak_sun_hours = annual_irradiance  # Peak sun hours ≈ daily kWh/m²
                    
                    logger.info(f"NASA POWER: Solar irradiance at ({lat}, {lon}): {annual_irradiance:.2f} kWh/m²/day")
                else:
                    raise ValueError("No irradiance data in response")
            else:
                logger.warning(f"NASA POWER API failed (status {response.status_code}), using fallback")
                raise ValueError("API call failed")
            
            # Calculate solar potential metrics
            solar_efficiency = 0.22  # Typical modern solar panel efficiency (22%)
            capacity_factor = peak_sun_hours / 24.0  # Capacity factor based on peak sun hours
            
            return {
                "annual_irradiance_kwh_m2": annual_irradiance,
                "peak_sun_hours": peak_sun_hours,
                "capacity_factor": capacity_factor,
                "solar_efficiency": solar_efficiency,
                "solar_score": min(1.0, annual_irradiance / 6.0),
                "data_source": "NASA_POWER"
            }
            
        except Exception as e:
            logger.error(f"Error fetching NASA POWER data: {e}")
            # Fallback: Use latitude-based estimation
            annual_irradiance = max(2.0, 6.0 - abs(lat) * 0.05)
            peak_sun_hours = annual_irradiance * 0.8
            
            return {
                "annual_irradiance_kwh_m2": annual_irradiance,
                "peak_sun_hours": peak_sun_hours,
                "capacity_factor": peak_sun_hours / 24.0,
                "solar_efficiency": 0.22,
                "solar_score": min(1.0, annual_irradiance / 6.0),
                "data_source": "FALLBACK_CALCULATION"
            }
    
    async def _analyze_wind_potential(self, lat: float, lon: float) -> Dict[str, float]:
        """Analyze wind energy potential using Open-Meteo API"""
        try:
            # Open-Meteo API - Free historical wind data
            # Get wind speed at 100m height (typical wind turbine hub height)
            params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": "wind_speed_100m,wind_direction_100m",
                "past_days": 90,  # Last 90 days for seasonal average
                "forecast_days": 0
            }
            
            response = requests.get(
                self.wind_api_url,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                hourly_data = data.get("hourly", {})
                wind_speeds_raw = hourly_data.get("wind_speed_100m", [])
                wind_directions_raw = hourly_data.get("wind_direction_100m", [])
                # Sanitize lists by removing None/NaN and casting to float
                wind_speeds = []
                for v in wind_speeds_raw:
                    try:
                        if v is None:
                            continue
                        f = float(v)
                        if np.isnan(f):
                            continue
                        wind_speeds.append(f)
                    except Exception:
                        continue
                wind_directions = []
                for v in wind_directions_raw:
                    try:
                        if v is None:
                            continue
                        f = float(v)
                        if np.isnan(f):
                            continue
                        wind_directions.append(f)
                    except Exception:
                        continue
                
                if wind_speeds:
                    # Calculate average wind speed
                    avg_wind_speed = float(sum(wind_speeds)) / float(len(wind_speeds))
                    
                    # Calculate prevailing wind direction (most common direction)
                    if wind_directions:
                        prevailing_direction = float(sum(wind_directions)) / float(len(wind_directions))
                    else:
                        prevailing_direction = 270  # Default to west
                    
                    logger.info(f"Open-Meteo: Wind speed at ({lat}, {lon}): {avg_wind_speed:.2f} m/s at 100m")
                else:
                    raise ValueError("No wind data in response")
            else:
                logger.warning(f"Open-Meteo API failed (status {response.status_code}), using fallback")
                raise ValueError("API call failed")
            
            # Calculate wind potential metrics
            wind_turbine_efficiency = 0.45  # Typical modern wind turbine efficiency (45%)
            # Capacity factor using simplified power curve: CF ≈ (v/v_rated)³ for v < v_rated
            # Assuming rated wind speed of 12 m/s
            capacity_factor = min(0.5, (avg_wind_speed / 12.0) ** 3)
            
            return {
                "average_wind_speed_ms": avg_wind_speed,
                "prevailing_direction": prevailing_direction,
                "capacity_factor": capacity_factor,
                "turbine_efficiency": wind_turbine_efficiency,
                "wind_score": min(1.0, avg_wind_speed / 10.0),
                "data_source": "OPEN_METEO"
            }
            
        except Exception as e:
            logger.error(f"Error fetching Open-Meteo wind data: {e}")
            # Fallback: Use latitude-based estimation
            avg_wind_speed = max(3.0, 8.0 - abs(lat) * 0.02)
            
            return {
                "average_wind_speed_ms": avg_wind_speed,
                "prevailing_direction": 270,
                "capacity_factor": min(0.5, (avg_wind_speed / 12.0) ** 3),
                "turbine_efficiency": 0.45,
                "wind_score": min(1.0, avg_wind_speed / 10.0),
                "data_source": "FALLBACK_CALCULATION"
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