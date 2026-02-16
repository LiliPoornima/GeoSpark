"""
Resource Estimation Agent for Renewable Energy Analysis
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from dataclasses import dataclass
import requests  # For NASA POWER and Open-Meteo APIs

from app.agents.communication import BaseAgent, AgentMessage, MessagePriority
from app.core.logging import agent_logger

logger = logging.getLogger(__name__)

@dataclass
class ResourceEstimate:
    """Resource estimation results"""
    resource_type: str  # solar, wind, hydro, geothermal
    annual_generation_gwh: float
    capacity_factor: float
    peak_power_mw: float
    seasonal_variation: Dict[str, float]
    uncertainty_range: Tuple[float, float]
    confidence_level: float
    data_quality_score: float

@dataclass
class WeatherData:
    """Weather data structure"""
    temperature_celsius: List[float]
    humidity_percent: List[float]
    wind_speed_ms: List[float]
    wind_direction_degrees: List[float]
    solar_irradiance_wm2: List[float]
    precipitation_mm: List[float]
    pressure_hpa: List[float]
    timestamp: List[datetime]

class ResourceEstimationAgent(BaseAgent):
    """Agent responsible for estimating renewable energy resources"""
    
    def __init__(self, communication_manager):
        super().__init__("resource_estimation", communication_manager)
        
        # Define capabilities
        self.capabilities.add_capability("solar_resource_estimation")
        self.capabilities.add_capability("wind_resource_estimation")
        self.capabilities.add_capability("hydro_resource_estimation")
        self.capabilities.add_capability("weather_data_analysis")
        self.capabilities.add_capability("energy_yield_modeling")
        
        # Register message handlers
        self.register_handler("estimate_solar_resource", self._handle_estimate_solar)
        self.register_handler("estimate_wind_resource", self._handle_estimate_wind)
        self.register_handler("estimate_hydro_resource", self._handle_estimate_hydro)
        self.register_handler("get_weather_data", self._handle_get_weather)
        self.register_handler("calculate_energy_yield", self._handle_calculate_yield)
        
        # Real API configurations (FREE APIs)
        # NASA POWER for comprehensive weather and solar data
        self.nasa_power_api_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        # Open-Meteo for high-resolution wind and weather forecasts
        self.openmeteo_api_url = "https://api.open-meteo.com/v1/forecast"
        # NREL (optional - requires API key, but we'll use NASA POWER instead)
        # self.nrel_api_url = "https://developer.nrel.gov/api"
        
    async def estimate_solar_resource(self, location_data: Dict[str, Any], 
                                   system_config: Dict[str, Any]) -> ResourceEstimate:
        """Estimate solar energy resource potential"""
        try:
            lat = location_data["latitude"]
            lon = location_data["longitude"]
            
            # Get weather data
            weather_data = await self._get_weather_data(lat, lon)
            
            # Calculate solar resource metrics
            solar_metrics = await self._calculate_solar_metrics(
                weather_data, system_config
            )
            
            # Estimate annual generation
            annual_generation = self._estimate_annual_solar_generation(
                solar_metrics, system_config
            )
            
            # Calculate capacity factor
            capacity_factor = self._calculate_solar_capacity_factor(
                solar_metrics, system_config
            )
            
            # Estimate seasonal variation
            seasonal_variation = self._calculate_seasonal_variation(
                weather_data, "solar"
            )
            
            # Calculate uncertainty
            uncertainty_range = self._calculate_uncertainty_range(
                solar_metrics, "solar"
            )
            
            # Log decision
            agent_logger.log_agent_decision(
                self.agent_id,
                f"Solar resource estimation completed for {lat}, {lon}",
                f"Annual generation: {annual_generation:.1f} GWh, Capacity factor: {capacity_factor:.2f}"
            )
            
            return ResourceEstimate(
                resource_type="solar",
                annual_generation_gwh=annual_generation,
                capacity_factor=capacity_factor,
                peak_power_mw=system_config.get("peak_power_mw", 100),
                seasonal_variation=seasonal_variation,
                uncertainty_range=uncertainty_range,
                confidence_level=0.85,
                data_quality_score=0.9
            )
            
        except Exception as e:
            logger.error(f"Error estimating solar resource: {e}")
            agent_logger.log_agent_error(self.agent_id, str(e), location_data)
            raise
    
    async def estimate_wind_resource(self, location_data: Dict[str, Any],
                                   system_config: Dict[str, Any]) -> ResourceEstimate:
        """Estimate wind energy resource potential"""
        try:
            lat = location_data["latitude"]
            lon = location_data["longitude"]
            
            # Get weather data
            weather_data = await self._get_weather_data(lat, lon)
            
            # Calculate wind resource metrics
            wind_metrics = await self._calculate_wind_metrics(
                weather_data, system_config
            )
            
            # Estimate annual generation
            annual_generation = self._estimate_annual_wind_generation(
                wind_metrics, system_config
            )
            
            # Calculate capacity factor
            capacity_factor = self._calculate_wind_capacity_factor(
                wind_metrics, system_config
            )
            
            # Estimate seasonal variation
            seasonal_variation = self._calculate_seasonal_variation(
                weather_data, "wind"
            )
            
            # Calculate uncertainty
            uncertainty_range = self._calculate_uncertainty_range(
                wind_metrics, "wind"
            )
            
            # Log decision
            agent_logger.log_agent_decision(
                self.agent_id,
                f"Wind resource estimation completed for {lat}, {lon}",
                f"Annual generation: {annual_generation:.1f} GWh, Capacity factor: {capacity_factor:.2f}"
            )
            
            return ResourceEstimate(
                resource_type="wind",
                annual_generation_gwh=annual_generation,
                capacity_factor=capacity_factor,
                peak_power_mw=system_config.get("peak_power_mw", 50),
                seasonal_variation=seasonal_variation,
                uncertainty_range=uncertainty_range,
                confidence_level=0.80,
                data_quality_score=0.85
            )
            
        except Exception as e:
            logger.error(f"Error estimating wind resource: {e}")
            agent_logger.log_agent_error(self.agent_id, str(e), location_data)
            raise
    
    async def estimate_hydro_resource(self, location_data: Dict[str, Any],
                                     system_config: Dict[str, Any]) -> ResourceEstimate:
        """Estimate hydroelectric resource potential"""
        try:
            lat = location_data["latitude"]
            lon = location_data["longitude"]
            
            # Get weather data for precipitation analysis
            weather_data = await self._get_weather_data(lat, lon)
            
            # Calculate hydro resource metrics
            hydro_metrics = await self._calculate_hydro_metrics(
                weather_data, system_config, location_data
            )
            
            # Estimate annual generation
            annual_generation = self._estimate_annual_hydro_generation(
                hydro_metrics, system_config
            )
            
            # Calculate capacity factor
            capacity_factor = self._calculate_hydro_capacity_factor(
                hydro_metrics, system_config
            )
            
            # Estimate seasonal variation
            seasonal_variation = self._calculate_seasonal_variation(
                weather_data, "hydro"
            )
            
            # Calculate uncertainty
            uncertainty_range = self._calculate_uncertainty_range(
                hydro_metrics, "hydro"
            )
            
            return ResourceEstimate(
                resource_type="hydro",
                annual_generation_gwh=annual_generation,
                capacity_factor=capacity_factor,
                peak_power_mw=system_config.get("peak_power_mw", 25),
                seasonal_variation=seasonal_variation,
                uncertainty_range=uncertainty_range,
                confidence_level=0.75,
                data_quality_score=0.8
            )
            
        except Exception as e:
            logger.error(f"Error estimating hydro resource: {e}")
            agent_logger.log_agent_error(self.agent_id, str(e), location_data)
            raise
    
    async def _get_weather_data(self, lat: float, lon: float) -> WeatherData:
        """Get real historical weather data from NASA POWER and Open-Meteo APIs"""
        try:
            import requests
            
            # Get solar irradiance and temperature from NASA POWER (last full year)
            nasa_params = {
                "parameters": "ALLSKY_SFC_SW_DWN,T2M,RH2M,PRECTOTCORR,PS",  # Solar, Temp, Humidity, Precipitation, Pressure
                "community": "RE",
                "longitude": lon,
                "latitude": lat,
                "start": "20230101",
                "end": "20231231",
                "format": "JSON"
            }
            
            nasa_response = requests.get(
                self.nasa_power_api_url,
                params=nasa_params,
                timeout=15
            )
            
            # Get wind data from Open-Meteo (last 90 days, hourly)
            meteo_params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": "temperature_2m,relative_humidity_2m,wind_speed_100m,wind_direction_100m,surface_pressure",
                "past_days": 90,
                "forecast_days": 0
            }
            
            meteo_response = requests.get(
                self.openmeteo_api_url,
                params=meteo_params,
                timeout=15
            )
            
            if nasa_response.status_code == 200 and meteo_response.status_code == 200:
                nasa_data = nasa_response.json()
                meteo_data = meteo_response.json()
                
                # Parse NASA POWER data (daily)
                nasa_params_data = nasa_data.get("properties", {}).get("parameter", {})
                solar_irradiance_daily = nasa_params_data.get("ALLSKY_SFC_SW_DWN", {})
                temp_daily = nasa_params_data.get("T2M", {})
                humidity_daily = nasa_params_data.get("RH2M", {})
                precip_daily = nasa_params_data.get("PRECTOTCORR", {})
                pressure_daily = nasa_params_data.get("PS", {})
                
                # Parse Open-Meteo data (hourly)
                meteo_hourly = meteo_data.get("hourly", {})
                wind_speeds_hourly = meteo_hourly.get("wind_speed_100m", [])
                wind_dir_hourly = meteo_hourly.get("wind_direction_100m", [])
                temp_hourly = meteo_hourly.get("temperature_2m", [])
                humidity_hourly = meteo_hourly.get("relative_humidity_2m", [])
                pressure_hourly = meteo_hourly.get("surface_pressure", [])
                time_hourly = meteo_hourly.get("time", [])

                # Determine the number of hours we have; prefer explicit time array, else wind length, else temp length
                n_hours = 0
                for candidate in (len(time_hourly), len(wind_speeds_hourly), len(temp_hourly), 90 * 24):
                    if candidate and candidate > 0:
                        n_hours = candidate
                        break
                if n_hours == 0:
                    raise ValueError("No hourly data returned from Open-Meteo")

                # Helper to sanitize lists: cast to float and replace None/NaN, pad/truncate to n_hours
                def _sanitize_numeric_list(lst, default_value: float) -> List[float]:
                    out: List[float] = []
                    length = len(lst) if isinstance(lst, list) else 0
                    for i in range(n_hours):
                        val = lst[i] if i < length else None
                        try:
                            # Treat None or nan as missing
                            if val is None:
                                raise ValueError("missing")
                            f = float(val)
                            if np.isnan(f):
                                raise ValueError("nan")
                            out.append(f)
                        except Exception:
                            out.append(float(default_value))
                    return out
                
                # Convert NASA daily solar irradiance (kWh/m²/day) to hourly W/m²
                # Assume solar radiation follows a sine curve during daylight hours
                solar_irradiance_hourly: List[float] = []
                timestamps: List[datetime] = []
                start_date = datetime.utcnow() - timedelta(hours=n_hours)

                for hour in range(n_hours):
                    timestamp = start_date + timedelta(hours=hour)
                    timestamps.append(timestamp)

                    # Get daily solar irradiance from NASA (kWh/m²/day) with safe default
                    date_key = timestamp.strftime("%Y%m%d")
                    daily_value = solar_irradiance_daily.get(date_key, 4.5)
                    try:
                        daily_solar_kwh = float(daily_value) if daily_value is not None else 4.5
                    except Exception:
                        daily_solar_kwh = 4.5
                    
                    # Convert to hourly W/m² (assuming 12 hours of daylight)
                    # Peak irradiance = daily_kwh * 1000 / (π/2) ≈ daily_kwh * 637
                    hour_of_day = timestamp.hour
                    if 6 <= hour_of_day <= 18:  # Daylight hours
                        solar_w_m2 = daily_solar_kwh * 637 * np.sin(np.pi * (hour_of_day - 6) / 12)
                    else:
                        solar_w_m2 = 0
                    solar_irradiance_hourly.append(float(max(0, solar_w_m2)))

                # Use Open-Meteo hourly data for other parameters, sanitized to numeric and aligned to n_hours
                temperature = _sanitize_numeric_list(temp_hourly, 15.0)
                humidity = _sanitize_numeric_list(humidity_hourly, 60.0)
                wind_speed = _sanitize_numeric_list(wind_speeds_hourly, 5.0)
                wind_direction = _sanitize_numeric_list(wind_dir_hourly, 270.0)
                pressure = _sanitize_numeric_list(pressure_hourly, 1013.0)

                # Precipitation (mm/hour) - simplified from NASA daily data with safe default
                precipitation_hourly: List[float] = []
                for ts in timestamps:
                    daily_precip = precip_daily.get(ts.strftime("%Y%m%d"))
                    try:
                        val = float(daily_precip) if daily_precip is not None else 0.0
                    except Exception:
                        val = 0.0
                    precipitation_hourly.append(val / 24.0)
                
                logger.info(f"Successfully fetched real weather data for ({lat}, {lon}) from NASA POWER and Open-Meteo")
                
                return WeatherData(
                    temperature_celsius=temperature,
                    humidity_percent=humidity,
                    wind_speed_ms=wind_speed,
                    wind_direction_degrees=wind_direction,
                    solar_irradiance_wm2=solar_irradiance_hourly,
                    precipitation_mm=precipitation_hourly,
                    pressure_hpa=pressure,
                    timestamp=timestamps
                )
            else:
                logger.warning(f"API calls failed: NASA={nasa_response.status_code}, Meteo={meteo_response.status_code}")
                raise ValueError("API calls failed")
            
        except Exception as e:
            logger.error(f"Error fetching real weather data: {e}")
            # Fallback to synthetic data
            return await self._get_synthetic_weather_data(lat, lon)
    
    async def _get_synthetic_weather_data(self, lat: float, lon: float) -> WeatherData:
        """Generate synthetic weather data as fallback (when APIs are unavailable)"""
        try:
            # Generate 90 days of hourly data (matching Open-Meteo's range)
            start_date = datetime.utcnow() - timedelta(days=90)
            timestamps = [start_date + timedelta(hours=i) for i in range(90 * 24)]
            
            
            # Generate realistic weather patterns
            temperature = self._generate_temperature_data(timestamps, lat)
            humidity = self._generate_humidity_data(timestamps)
            wind_speed = self._generate_wind_speed_data(timestamps, lat)
            wind_direction = self._generate_wind_direction_data(timestamps)
            solar_irradiance = self._generate_solar_irradiance_data(timestamps, lat)
            precipitation = self._generate_precipitation_data(timestamps)
            pressure = self._generate_pressure_data(timestamps)
            
            logger.info(f"Using synthetic weather data (fallback) for ({lat}, {lon})")
            
            return WeatherData(
                temperature_celsius=temperature,
                humidity_percent=humidity,
                wind_speed_ms=wind_speed,
                wind_direction_degrees=wind_direction,
                solar_irradiance_wm2=solar_irradiance,
                precipitation_mm=precipitation,
                pressure_hpa=pressure,
                timestamp=timestamps
            )
            
        except Exception as e:
            logger.error(f"Error generating synthetic weather data: {e}")
            # Return minimal default data
            return self._get_default_weather_data()
    
    def _generate_temperature_data(self, timestamps: List[datetime], lat: float) -> List[float]:
        """Generate realistic temperature data"""
        temperatures = []
        base_temp = 20 - abs(lat) * 0.5  # Temperature decreases with latitude
        
        for timestamp in timestamps:
            # Seasonal variation
            day_of_year = timestamp.timetuple().tm_yday
            seasonal_temp = base_temp + 10 * np.sin(2 * np.pi * day_of_year / 365)
            
            # Daily variation
            hour_temp = seasonal_temp + 5 * np.sin(2 * np.pi * timestamp.hour / 24)
            
            # Add some noise
            noise = np.random.normal(0, 2)
            temperatures.append(hour_temp + noise)
        
        return temperatures
    
    def _generate_humidity_data(self, timestamps: List[datetime]) -> List[float]:
        """Generate realistic humidity data"""
        humidities = []
        
        for timestamp in timestamps:
            # Humidity varies inversely with temperature
            base_humidity = 60
            daily_variation = 20 * np.sin(2 * np.pi * timestamp.hour / 24)
            noise = np.random.normal(0, 5)
            
            humidity = base_humidity + daily_variation + noise
            humidities.append(max(0, min(100, humidity)))
        
        return humidities
    
    def _generate_wind_speed_data(self, timestamps: List[datetime], lat: float) -> List[float]:
        """Generate realistic wind speed data"""
        wind_speeds = []
        base_speed = 5 + abs(lat) * 0.1  # Wind speed increases with latitude
        
        for timestamp in timestamps:
            # Seasonal variation
            day_of_year = timestamp.timetuple().tm_yday
            seasonal_speed = base_speed + 2 * np.sin(2 * np.pi * day_of_year / 365)
            
            # Daily variation
            hour_speed = seasonal_speed + 1 * np.sin(2 * np.pi * timestamp.hour / 24)
            
            # Add noise and ensure positive values
            noise = np.random.normal(0, 1)
            wind_speeds.append(max(0, hour_speed + noise))
        
        return wind_speeds
    
    def _generate_wind_direction_data(self, timestamps: List[datetime]) -> List[float]:
        """Generate realistic wind direction data"""
        directions = []
        
        for timestamp in timestamps:
            # Prevailing wind direction with some variation
            base_direction = 270  # West
            variation = np.random.normal(0, 30)
            direction = (base_direction + variation) % 360
            directions.append(direction)
        
        return directions
    
    def _generate_solar_irradiance_data(self, timestamps: List[datetime], lat: float) -> List[float]:
        """Generate realistic solar irradiance data"""
        irradiances = []
        
        for timestamp in timestamps:
            # Solar irradiance depends on sun angle
            day_of_year = timestamp.timetuple().tm_yday
            hour_of_day = timestamp.hour
            
            # Calculate sun elevation angle (simplified)
            declination = 23.45 * np.sin(2 * np.pi * (284 + day_of_year) / 365)
            hour_angle = 15 * (hour_of_day - 12)
            
            elevation = np.arcsin(
                np.sin(np.radians(lat)) * np.sin(np.radians(declination)) +
                np.cos(np.radians(lat)) * np.cos(np.radians(declination)) * np.cos(np.radians(hour_angle))
            )
            
            # Solar irradiance proportional to sun elevation
            if elevation > 0:
                irradiance = 1000 * np.sin(elevation)
            else:
                irradiance = 0
            
            # Add some atmospheric effects
            atmospheric_factor = 0.7 + 0.2 * np.random.random()
            irradiances.append(irradiance * atmospheric_factor)
        
        return irradiances
    
    def _generate_precipitation_data(self, timestamps: List[datetime]) -> List[float]:
        """Generate realistic precipitation data"""
        precipitations = []
        
        for timestamp in timestamps:
            # Precipitation is intermittent
            if np.random.random() < 0.1:  # 10% chance of precipitation
                intensity = np.random.exponential(2)  # mm/hour
                precipitations.append(intensity)
            else:
                precipitations.append(0)
        
        return precipitations
    
    def _generate_pressure_data(self, timestamps: List[datetime]) -> List[float]:
        """Generate realistic atmospheric pressure data"""
        pressures = []
        base_pressure = 1013.25  # hPa
        
        for timestamp in timestamps:
            # Pressure varies with weather patterns
            variation = np.random.normal(0, 10)
            pressure = base_pressure + variation
            pressures.append(pressure)
        
        return pressures
    
    def _get_default_weather_data(self) -> WeatherData:
        """Get default weather data when API fails"""
        timestamps = [datetime.utcnow() - timedelta(hours=i) for i in range(8760)]
        
        return WeatherData(
            temperature_celsius=[20] * 8760,
            humidity_percent=[60] * 8760,
            wind_speed_ms=[5] * 8760,
            wind_direction_degrees=[270] * 8760,
            solar_irradiance_wm2=[500] * 8760,
            precipitation_mm=[0] * 8760,
            pressure_hpa=[1013] * 8760,
            timestamp=timestamps
        )
    
    async def _calculate_solar_metrics(self, weather_data: WeatherData, 
                                    system_config: Dict[str, Any]) -> Dict[str, float]:
        """Calculate solar energy metrics from weather data"""
        # Calculate average solar irradiance
        avg_irradiance = np.mean(weather_data.solar_irradiance_wm2)
        
        # Calculate peak sun hours
        peak_sun_hours = avg_irradiance / 1000  # Convert W/m² to sun hours
        
        # Calculate temperature coefficient effect
        avg_temp = np.mean(weather_data.temperature_celsius)
        temp_coefficient = -0.004  # per °C
        temp_effect = 1 + temp_coefficient * (avg_temp - 25)
        
        return {
            "average_irradiance_wm2": avg_irradiance,
            "peak_sun_hours": peak_sun_hours,
            "temperature_effect": temp_effect,
            "efficiency_factor": system_config.get("panel_efficiency", 0.22)
        }
    
    async def _calculate_wind_metrics(self, weather_data: WeatherData,
                                   system_config: Dict[str, Any]) -> Dict[str, float]:
        """Calculate wind energy metrics from weather data"""
        # Calculate average wind speed
        avg_wind_speed = np.mean(weather_data.wind_speed_ms)
        
        # Calculate wind speed distribution (Weibull parameters)
        wind_speeds = np.array(weather_data.wind_speed_ms)
        weibull_shape = 2.0  # Typical value
        weibull_scale = avg_wind_speed / np.sqrt(np.pi) / 2
        
        # Calculate capacity factor using power curve
        cut_in_speed = system_config.get("cut_in_speed", 3.0)
        rated_speed = system_config.get("rated_speed", 12.0)
        cut_out_speed = system_config.get("cut_out_speed", 25.0)
        
        capacity_factor = self._calculate_wind_capacity_factor_from_speeds(
            wind_speeds, cut_in_speed, rated_speed, cut_out_speed
        )
        
        return {
            "average_wind_speed_ms": avg_wind_speed,
            "weibull_shape": weibull_shape,
            "weibull_scale": weibull_scale,
            "capacity_factor": capacity_factor
        }
    
    async def _calculate_hydro_metrics(self, weather_data: WeatherData,
                                    system_config: Dict[str, Any],
                                    location_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate hydroelectric metrics from weather data"""
        # Calculate average precipitation
        avg_precipitation = np.mean(weather_data.precipitation_mm)
        
        # Estimate runoff coefficient
        runoff_coefficient = 0.3  # Typical value
        
        # Calculate head (elevation difference)
        head_meters = system_config.get("head_meters", 50)
        
        # Calculate flow rate
        catchment_area_km2 = location_data.get("catchment_area_km2", 100)
        flow_rate_m3s = (avg_precipitation * catchment_area_km2 * 1000000 * runoff_coefficient) / (365 * 24 * 3600)
        
        return {
            "average_precipitation_mm": avg_precipitation,
            "runoff_coefficient": runoff_coefficient,
            "head_meters": head_meters,
            "flow_rate_m3s": flow_rate_m3s,
            "catchment_area_km2": catchment_area_km2
        }
    
    def _estimate_annual_solar_generation(self, solar_metrics: Dict[str, float],
                                        system_config: Dict[str, Any]) -> float:
        """Estimate annual solar energy generation"""
        peak_power_mw = system_config.get("peak_power_mw", 100)
        peak_sun_hours = solar_metrics["peak_sun_hours"]
        efficiency_factor = solar_metrics["efficiency_factor"]
        temperature_effect = solar_metrics["temperature_effect"]
        
        # Annual generation in GWh
        annual_generation = (peak_power_mw * peak_sun_hours * efficiency_factor * 
                           temperature_effect * 365) / 1000
        
        return annual_generation
    
    def _estimate_annual_wind_generation(self, wind_metrics: Dict[str, float],
                                      system_config: Dict[str, Any]) -> float:
        """Estimate annual wind energy generation"""
        peak_power_mw = system_config.get("peak_power_mw", 50)
        capacity_factor = wind_metrics["capacity_factor"]
        
        # Annual generation in GWh
        annual_generation = (peak_power_mw * capacity_factor * 8760) / 1000
        
        return annual_generation
    
    def _estimate_annual_hydro_generation(self, hydro_metrics: Dict[str, float],
                                        system_config: Dict[str, Any]) -> float:
        """Estimate annual hydroelectric generation"""
        peak_power_mw = system_config.get("peak_power_mw", 25)
        flow_rate_m3s = hydro_metrics["flow_rate_m3s"]
        head_meters = hydro_metrics["head_meters"]
        
        # Calculate theoretical power
        water_density = 1000  # kg/m³
        gravity = 9.81  # m/s²
        efficiency = 0.85  # Turbine efficiency
        
        theoretical_power_mw = (flow_rate_m3s * water_density * gravity * head_meters * efficiency) / 1000000
        
        # Use minimum of theoretical and installed capacity
        actual_power_mw = min(peak_power_mw, theoretical_power_mw)
        
        # Annual generation in GWh
        annual_generation = (actual_power_mw * 8760) / 1000
        
        return annual_generation
    
    def _calculate_solar_capacity_factor(self, solar_metrics: Dict[str, float],
                                       system_config: Dict[str, Any]) -> float:
        """Calculate solar capacity factor"""
        peak_sun_hours = solar_metrics["peak_sun_hours"]
        return peak_sun_hours / 24.0
    
    def _calculate_wind_capacity_factor(self, wind_metrics: Dict[str, float],
                                       system_config: Dict[str, Any]) -> float:
        """Calculate wind capacity factor"""
        return wind_metrics["capacity_factor"]
    
    def _calculate_hydro_capacity_factor(self, hydro_metrics: Dict[str, float],
                                       system_config: Dict[str, Any]) -> float:
        """Calculate hydro capacity factor"""
        # Hydro capacity factor depends on water availability
        flow_rate_m3s = hydro_metrics["flow_rate_m3s"]
        design_flow_m3s = system_config.get("design_flow_m3s", 10)
        
        return min(1.0, flow_rate_m3s / design_flow_m3s)
    
    def _calculate_wind_capacity_factor_from_speeds(self, wind_speeds: np.ndarray,
                                                   cut_in: float, rated: float,
                                                   cut_out: float) -> float:
        """Calculate capacity factor from wind speed distribution"""
        power_outputs = []
        
        for speed in wind_speeds:
            if speed < cut_in or speed > cut_out:
                power_outputs.append(0)
            elif speed < rated:
                # Linear increase from cut-in to rated speed
                power_outputs.append(speed / rated)
            else:
                # Constant power at rated speed
                power_outputs.append(1.0)
        
        return np.mean(power_outputs)
    
    def _calculate_seasonal_variation(self, weather_data: WeatherData, 
                                    resource_type: str) -> Dict[str, float]:
        """Calculate seasonal variation in resource availability"""
        # Group data by month
        monthly_data = {}
        
        for i, timestamp in enumerate(weather_data.timestamp):
            month = timestamp.month
            
            if month not in monthly_data:
                monthly_data[month] = []
            
            if resource_type == "solar":
                monthly_data[month].append(weather_data.solar_irradiance_wm2[i])
            elif resource_type == "wind":
                monthly_data[month].append(weather_data.wind_speed_ms[i])
            elif resource_type == "hydro":
                monthly_data[month].append(weather_data.precipitation_mm[i])
        
        # Calculate monthly averages
        monthly_averages = {}
        for month, values in monthly_data.items():
            monthly_averages[f"month_{month}"] = np.mean(values)
        
        return monthly_averages
    
    def _calculate_uncertainty_range(self, metrics: Dict[str, float], 
                                    resource_type: str) -> Tuple[float, float]:
        """Calculate uncertainty range for estimates"""
        # Base uncertainty depends on resource type
        base_uncertainty = {
            "solar": 0.15,
            "wind": 0.20,
            "hydro": 0.25
        }.get(resource_type, 0.20)
        
        # Calculate confidence interval
        mean_value = np.mean(list(metrics.values()))
        uncertainty = mean_value * base_uncertainty
        
        return (mean_value - uncertainty, mean_value + uncertainty)
    
    # Message handlers
    async def _handle_estimate_solar(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle solar resource estimation requests"""
        location_data = message.content.get("location")
        system_config = message.content.get("system_config", {})
        
        estimate = await self.estimate_solar_resource(location_data, system_config)
        
        return {
            "resource_estimate": {
                "resource_type": estimate.resource_type,
                "annual_generation_gwh": estimate.annual_generation_gwh,
                "capacity_factor": estimate.capacity_factor,
                "peak_power_mw": estimate.peak_power_mw,
                "seasonal_variation": estimate.seasonal_variation,
                "uncertainty_range": estimate.uncertainty_range,
                "confidence_level": estimate.confidence_level,
                "data_quality_score": estimate.data_quality_score
            }
        }
    
    async def _handle_estimate_wind(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle wind resource estimation requests"""
        location_data = message.content.get("location")
        system_config = message.content.get("system_config", {})
        
        estimate = await self.estimate_wind_resource(location_data, system_config)
        
        return {
            "resource_estimate": {
                "resource_type": estimate.resource_type,
                "annual_generation_gwh": estimate.annual_generation_gwh,
                "capacity_factor": estimate.capacity_factor,
                "peak_power_mw": estimate.peak_power_mw,
                "seasonal_variation": estimate.seasonal_variation,
                "uncertainty_range": estimate.uncertainty_range,
                "confidence_level": estimate.confidence_level,
                "data_quality_score": estimate.data_quality_score
            }
        }
    
    async def _handle_estimate_hydro(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle hydro resource estimation requests"""
        location_data = message.content.get("location")
        system_config = message.content.get("system_config", {})
        
        estimate = await self.estimate_hydro_resource(location_data, system_config)
        
        return {
            "resource_estimate": {
                "resource_type": estimate.resource_type,
                "annual_generation_gwh": estimate.annual_generation_gwh,
                "capacity_factor": estimate.capacity_factor,
                "peak_power_mw": estimate.peak_power_mw,
                "seasonal_variation": estimate.seasonal_variation,
                "uncertainty_range": estimate.uncertainty_range,
                "confidence_level": estimate.confidence_level,
                "data_quality_score": estimate.data_quality_score
            }
        }
    
    async def _handle_get_weather(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle weather data requests"""
        location_data = message.content.get("location")
        lat = location_data["latitude"]
        lon = location_data["longitude"]
        
        weather_data = await self._get_weather_data(lat, lon)
        
        return {
            "weather_data": {
                "temperature_celsius": weather_data.temperature_celsius[:24],  # First 24 hours
                "humidity_percent": weather_data.humidity_percent[:24],
                "wind_speed_ms": weather_data.wind_speed_ms[:24],
                "wind_direction_degrees": weather_data.wind_direction_degrees[:24],
                "solar_irradiance_wm2": weather_data.solar_irradiance_wm2[:24],
                "precipitation_mm": weather_data.precipitation_mm[:24],
                "pressure_hpa": weather_data.pressure_hpa[:24]
            }
        }
    
    async def _handle_calculate_yield(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle energy yield calculation requests"""
        resource_estimates = message.content.get("resource_estimates", [])
        
        total_yield = 0
        for estimate in resource_estimates:
            total_yield += estimate.get("annual_generation_gwh", 0)
        
        return {
            "total_annual_yield_gwh": total_yield,
            "breakdown": resource_estimates
        }