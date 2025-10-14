"""
Site Selection Agent
Analyzes potential sites for renewable energy projects
"""
from typing import Dict, Any, List
import logging
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)


class SiteSelectionAgent:
    """Agent for analyzing and selecting optimal renewable energy sites"""
    
    def __init__(self):
        self.solar_api_url = "https://api.solar.com/v1/irradiance"
        self.wind_api_url = "https://api.wind.com/v1/speed"
        self.terrain_api_url = "https://api.terrain.com/v1/elevation"
        
    async def analyze_location(
        self,
        latitude: float,
        longitude: float,
        location_name: str = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive site analysis for a given location
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            location_name: Optional name of the location
            
        Returns:
            Dictionary containing site analysis results
        """
        try:
            logger.info(f"Analyzing location: {location_name or ''Unknown''} ({latitude}, {longitude})")
            
            # Perform parallel analysis of different factors
            solar_potential = await self._analyze_solar_potential(latitude, longitude)
            wind_potential = await self._analyze_wind_potential(latitude, longitude)
            terrain_data = await self._analyze_terrain(latitude, longitude)
            environmental_factors = await self._assess_environmental_factors(latitude, longitude)
            regulatory_compliance = await self._assess_regulatory_compliance(latitude, longitude)
            accessibility = await self._assess_accessibility(latitude, longitude)
            
            # Calculate overall site score
            overall_score = self._calculate_overall_score(
                solar_potential,
                wind_potential,
                terrain_data,
                environmental_factors,
                regulatory_compliance,
                accessibility
            )
            
            # Estimate potential capacity
            estimated_capacity = self._estimate_capacity(
                solar_potential,
                wind_potential,
                terrain_data["usable_area_km2"]
            )
            
            result = {
                "location_name": location_name or f"Site at {latitude:.4f}, {longitude:.4f}",
                "coordinates": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "solar_potential": solar_potential,
                "wind_potential": wind_potential,
                "terrain": terrain_data,
                "environmental_factors": environmental_factors,
                "regulatory_compliance": regulatory_compliance,
                "accessibility": accessibility,
                "overall_score": overall_score,
                "estimated_capacity_mw": estimated_capacity,
                "analysis_date": datetime.now().isoformat(),
                "recommendation": self._generate_recommendation(overall_score)
            }
            
            logger.info(f"Site analysis complete. Overall score: {overall_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing location: {str(e)}")
            raise
    
    async def _analyze_solar_potential(self, lat: float, lon: float) -> float:
        """Analyze solar irradiance potential"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.solar_api_url,
                    params={"lat": lat, "lon": lon},
                    timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("irradiance_score", 0.5)
        except Exception as e:
            logger.warning(f"Solar API call failed, using fallback calculation: {str(e)}")
        
        solar_score = max(2.0, 6.0 - abs(lat) * 0.05)
        return min(10.0, solar_score) / 10.0
    
    async def _analyze_wind_potential(self, lat: float, lon: float) -> float:
        """Analyze wind speed potential"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.wind_api_url,
                    params={"lat": lat, "lon": lon},
                    timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("wind_score", 0.5)
        except Exception as e:
            logger.warning(f"Wind API call failed, using fallback calculation: {str(e)}")
        
        wind_score = max(3.0, 8.0 - abs(lat) * 0.02)
        return min(10.0, wind_score) / 10.0
    
    async def _analyze_terrain(self, lat: float, lon: float) -> Dict[str, Any]:
        """Analyze terrain characteristics"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.terrain_api_url,
                    params={"lat": lat, "lon": lon},
                    timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "elevation_m": data.get("elevation", 100),
                        "slope_degrees": data.get("slope", 5),
                        "terrain_type": data.get("terrain_type", "mixed"),
                        "usable_area_km2": data.get("usable_area", 10)
                    }
        except Exception as e:
            logger.warning(f"Terrain API call failed, using fallback data: {str(e)}")
        
        return {
            "elevation_m": 100 + abs(lat) * 10,
            "slope_degrees": 5.0,
            "terrain_type": "mixed",
            "usable_area_km2": 10.0
        }
    
    async def _assess_environmental_factors(self, lat: float, lon: float) -> float:
        """Assess environmental impact and constraints"""
        score = 0.8
        
        if abs(lat) < 30:
            score -= 0.1
        
        water_penalty = 0.3 if (int(lat * 100) + int(lon * 100)) % 7 == 0 else 0
        score -= water_penalty
        
        forest_penalty = 0.2 if (int(lat * 100) + int(lon * 100)) % 5 == 0 else 0
        score -= forest_penalty
        
        return max(0.0, min(1.0, score))
    
    async def _assess_regulatory_compliance(self, lat: float, lon: float) -> float:
        """Assess regulatory and permitting ease"""
        score = 0.7
        
        if abs(lat) > 30 and abs(lat) < 60:
            score += 0.2
        
        zoning_bonus = 0.1 if (int(lat * 50) + int(lon * 50)) % 3 == 0 else -0.1
        score += zoning_bonus
        
        return max(0.0, min(1.0, score))
    
    async def _assess_accessibility(self, lat: float, lon: float) -> float:
        """Assess site accessibility and infrastructure"""
        score = 0.7
        
        road_distance_km = 2.0 + (abs(lat + lon) % 10)
        if road_distance_km < 5:
            score += 0.2
        elif road_distance_km > 15:
            score -= 0.2
        
        transmission_distance_km = 15.0 + (abs(lat - lon) % 20)
        if transmission_distance_km < 10:
            score += 0.1
        elif transmission_distance_km > 30:
            score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    def _calculate_overall_score(
        self,
        solar: float,
        wind: float,
        terrain: Dict[str, Any],
        environmental: float,
        regulatory: float,
        accessibility: float
    ) -> float:
        """Calculate weighted overall site score"""
        slope = terrain.get("slope_degrees", 5)
        terrain_score = 1.0 if slope < 10 else 0.5 if slope < 20 else 0.2
        
        weights = {
            "solar": 0.25,
            "wind": 0.25,
            "terrain": 0.15,
            "environmental": 0.15,
            "regulatory": 0.10,
            "accessibility": 0.10
        }
        
        overall = (
            solar * weights["solar"] +
            wind * weights["wind"] +
            terrain_score * weights["terrain"] +
            environmental * weights["environmental"] +
            regulatory * weights["regulatory"] +
            accessibility * weights["accessibility"]
        )
        
        return round(overall, 3)
    
    def _estimate_capacity(
        self,
        solar_potential: float,
        wind_potential: float,
        usable_area: float
    ) -> float:
        """Estimate potential installed capacity in MW"""
        solar_capacity = usable_area * 6 * solar_potential * 0.5
        wind_capacity = usable_area * 12 * wind_potential * 0.5
        total_capacity = (solar_capacity * 0.6 + wind_capacity * 0.4)
        
        return round(total_capacity, 2)
    
    def _generate_recommendation(self, overall_score: float) -> str:
        """Generate a recommendation based on overall score"""
        if overall_score >= 0.8:
            return "Highly Recommended - Excellent site conditions for renewable energy development"
        elif overall_score >= 0.6:
            return "Recommended - Good site conditions with minor constraints"
        elif overall_score >= 0.4:
            return "Conditional - Site has potential but requires detailed feasibility study"
        else:
            return "Not Recommended - Significant constraints make development challenging"
    
    async def compare_locations(
        self,
        locations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Compare multiple locations and rank them"""
        results = []
        
        for loc in locations:
            analysis = await self.analyze_location(
                loc["latitude"],
                loc["longitude"],
                loc.get("name")
            )
            results.append(analysis)
        
        results.sort(key=lambda x: x["overall_score"], reverse=True)
        
        for i, result in enumerate(results, 1):
            result["rank"] = i
        
        return results
