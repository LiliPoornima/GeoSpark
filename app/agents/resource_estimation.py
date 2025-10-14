"""
Resource Estimation Agent
Estimates renewable energy generation potential based on site analysis
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class ResourceEstimationAgent:
    """Agent for estimating renewable energy resource potential"""
    
    def __init__(self):
        self.solar_capacity_factor = 0.20  # Typical solar capacity factor (20%)
        self.wind_capacity_factor = 0.35   # Typical wind capacity factor (35%)
        self.hours_per_year = 8760
        
    async def estimate_resources(
        self,
        location: str,
        site_data: Dict[str, Any],
        project_type: str = "hybrid"
    ) -> Dict[str, Any]:
        """
        Estimate energy generation potential
        
        Args:
            location: Location name
            site_data: Site analysis data with scores
            project_type: Type of project (solar, wind, or hybrid)
            
        Returns:
            Dictionary with resource estimates
        """
        try:
            logger.info(f"Estimating resources for {location}, type: {project_type}")
            
            # Extract site scores
            solar_score = site_data.get("solar_potential", 0.5)
            wind_score = site_data.get("wind_potential", 0.5)
            environmental_score = site_data.get("environmental_factors", 0.8)
            
            # Estimate installed capacity based on site quality
            # Base capacity: 100 MW, scaled by site quality
            base_capacity = 100  # MW
            
            if project_type == "solar":
                installed_capacity = base_capacity * solar_score
                capacity_factor = self.solar_capacity_factor * solar_score
            elif project_type == "wind":
                installed_capacity = base_capacity * wind_score
                capacity_factor = self.wind_capacity_factor * wind_score
            else:  # hybrid
                solar_capacity = base_capacity * 0.6 * solar_score
                wind_capacity = base_capacity * 0.4 * wind_score
                installed_capacity = solar_capacity + wind_capacity
                capacity_factor = (
                    self.solar_capacity_factor * 0.6 * solar_score +
                    self.wind_capacity_factor * 0.4 * wind_score
                )
            
            # Calculate annual generation
            annual_generation = (
                installed_capacity * capacity_factor * 
                self.hours_per_year * environmental_score
            )  # MWh
            
            # Convert to GWh
            annual_generation_gwh = annual_generation / 1000
            
            # Calculate monthly generation (simplified seasonal variation)
            monthly_generation = self._calculate_monthly_generation(
                annual_generation_gwh,
                project_type
            )
            
            # Calculate carbon offset (tons CO2/year)
            # Average grid emission: 0.5 tons CO2 per MWh
            carbon_offset = annual_generation * 0.5
            
            result = {
                "location": location,
                "project_type": project_type,
                "installed_capacity_mw": round(installed_capacity, 2),
                "capacity_factor": round(capacity_factor, 3),
                "annual_generation_gwh": round(annual_generation_gwh, 2),
                "monthly_generation_gwh": monthly_generation,
                "carbon_offset_tons": round(carbon_offset, 2),
                "site_quality_factor": round(
                    (solar_score + wind_score) / 2 * environmental_score,
                    3
                )
            }
            
            logger.info(f"Resource estimation complete: {annual_generation_gwh:.2f} GWh/year")
            return result
            
        except Exception as e:
            logger.error(f"Error in resource estimation: {str(e)}")
            raise
    
    def _calculate_monthly_generation(
        self,
        annual_gwh: float,
        project_type: str
    ) -> list:
        """Calculate monthly generation with seasonal variation"""
        
        # Seasonal factors (12 months)
        if project_type == "solar":
            # Solar: higher in summer, lower in winter
            factors = [0.07, 0.08, 0.09, 0.10, 0.11, 0.10, 
                      0.10, 0.10, 0.09, 0.08, 0.07, 0.06]
        elif project_type == "wind":
            # Wind: higher in winter, more consistent
            factors = [0.09, 0.09, 0.09, 0.08, 0.07, 0.07,
                      0.07, 0.07, 0.08, 0.09, 0.09, 0.10]
        else:  # hybrid
            # Balanced profile
            factors = [0.08, 0.08, 0.09, 0.09, 0.09, 0.08,
                      0.08, 0.08, 0.09, 0.09, 0.08, 0.08]
        
        # Normalize factors to sum to 1.0
        total_factor = sum(factors)
        normalized_factors = [f / total_factor for f in factors]
        
        # Calculate monthly values
        monthly = [round(annual_gwh * f, 2) for f in normalized_factors]
        
        return monthly
