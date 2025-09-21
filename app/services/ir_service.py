"""
Information Retrieval Module for Renewable Energy Data
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import requests
from dataclasses import dataclass
from enum import Enum
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

from app.core.config import settings
from app.core.logging import agent_logger

logger = logging.getLogger(__name__)

class DataSource(Enum):
    """Types of data sources"""
    SOLAR_API = "solar_api"
    WIND_API = "wind_api"
    WEATHER_API = "weather_api"
    GRID_DATA = "grid_data"
    REGULATORY_DB = "regulatory_db"
    ENVIRONMENTAL_DB = "environmental_db"
    FINANCIAL_DB = "financial_db"

class QueryType(Enum):
    """Types of queries"""
    SOLAR_RESOURCE = "solar_resource"
    WIND_RESOURCE = "wind_resource"
    WEATHER_DATA = "weather_data"
    GRID_CONNECTION = "grid_connection"
    REGULATORY_INFO = "regulatory_info"
    ENVIRONMENTAL_DATA = "environmental_data"
    FINANCIAL_DATA = "financial_data"
    SITE_ANALYSIS = "site_analysis"

@dataclass
class DataPoint:
    """Data point structure"""
    id: str
    source: DataSource
    data_type: str
    location: Dict[str, float]  # lat, lon
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    quality_score: float

@dataclass
class SearchResult:
    """Search result structure"""
    query: str
    results: List[DataPoint]
    total_results: int
    search_time_ms: float
    query_type: QueryType
    confidence_score: float

class InformationRetrievalEngine:
    """Main information retrieval engine"""
    
    def __init__(self):
        self.vector_db = None
        self.embedding_model = None
        self.data_cache = {}
        self.initialized = False
        self._initialize_ir_system()
    
    def _initialize_ir_system(self):
        """Initialize the information retrieval system"""
        try:
            # Initialize ChromaDB for vector storage
            self.vector_db = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="./chroma_db"
            ))
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Create collections for different data types
            self._create_collections()
            
            self.initialized = True
            logger.info("Information Retrieval Engine initialized")
            
        except Exception as e:
            logger.error(f"Error initializing IR system: {e}")
            self.initialized = False
    
    def _create_collections(self):
        """Create ChromaDB collections for different data types"""
        try:
            collections = [
                "solar_data",
                "wind_data", 
                "weather_data",
                "regulatory_data",
                "environmental_data",
                "financial_data",
                "site_data"
            ]
            
            for collection_name in collections:
                try:
                    self.vector_db.get_collection(collection_name)
                except:
                    self.vector_db.create_collection(
                        name=collection_name,
                        metadata={"description": f"Collection for {collection_name}"}
                    )
            
            logger.info("ChromaDB collections created successfully")
            
        except Exception as e:
            logger.error(f"Error creating collections: {e}")
    
    async def search_data(self, query: str, query_type: QueryType, 
                         location: Optional[Dict[str, float]] = None,
                         filters: Optional[Dict[str, Any]] = None,
                         limit: int = 10) -> SearchResult:
        """Search for data using natural language query"""
        if not self.initialized:
            raise RuntimeError("IR system not initialized")
        
        start_time = datetime.utcnow()
        
        try:
            # Generate embeddings for the query
            query_embedding = self.embedding_model.encode([query])[0].tolist()
            
            # Determine collection based on query type
            collection_name = self._get_collection_name(query_type)
            
            # Search in vector database
            collection = self.vector_db.get_collection(collection_name)
            
            # Prepare search parameters
            search_params = {
                "query_embeddings": [query_embedding],
                "n_results": limit
            }
            
            # Add location filter if provided
            if location:
                search_params["where"] = self._create_location_filter(location)
            
            # Add additional filters
            if filters:
                if "where" in search_params:
                    search_params["where"] = {**search_params["where"], **filters}
                else:
                    search_params["where"] = filters
            
            # Perform search
            results = collection.query(**search_params)
            
            # Convert results to DataPoint objects
            data_points = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    try:
                        data_dict = json.loads(doc)
                        data_point = DataPoint(
                            id=results["ids"][0][i],
                            source=DataSource(data_dict.get("source", "unknown")),
                            data_type=data_dict.get("data_type", "unknown"),
                            location=data_dict.get("location", {}),
                            timestamp=datetime.fromisoformat(data_dict.get("timestamp", datetime.utcnow().isoformat())),
                            data=data_dict.get("data", {}),
                            metadata=data_dict.get("metadata", {}),
                            quality_score=results["distances"][0][i] if results["distances"] else 0.5
                        )
                        data_points.append(data_point)
                    except Exception as e:
                        logger.warning(f"Error parsing result {i}: {e}")
                        continue
            
            # Calculate search time
            search_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(data_points, query_type)
            
            # Log search
            agent_logger.log_agent_decision(
                "ir_engine",
                f"Data search completed: {query_type.value}",
                f"Found {len(data_points)} results in {search_time:.1f}ms"
            )
            
            return SearchResult(
                query=query,
                results=data_points,
                total_results=len(data_points),
                search_time_ms=search_time,
                query_type=query_type,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"Error in data search: {e}")
            return SearchResult(
                query=query,
                results=[],
                total_results=0,
                search_time_ms=0,
                query_type=query_type,
                confidence_score=0.0
            )
    
    def _get_collection_name(self, query_type: QueryType) -> str:
        """Get collection name based on query type"""
        mapping = {
            QueryType.SOLAR_RESOURCE: "solar_data",
            QueryType.WIND_RESOURCE: "wind_data",
            QueryType.WEATHER_DATA: "weather_data",
            QueryType.GRID_CONNECTION: "site_data",
            QueryType.REGULATORY_INFO: "regulatory_data",
            QueryType.ENVIRONMENTAL_DATA: "environmental_data",
            QueryType.FINANCIAL_DATA: "financial_data",
            QueryType.SITE_ANALYSIS: "site_data"
        }
        return mapping.get(query_type, "site_data")
    
    def _create_location_filter(self, location: Dict[str, float]) -> Dict[str, Any]:
        """Create location-based filter for search"""
        lat = location.get("latitude", 0)
        lon = location.get("longitude", 0)
        
        # Create a bounding box around the location (simplified)
        tolerance = 0.1  # degrees
        return {
            "latitude": {"$gte": lat - tolerance, "$lte": lat + tolerance},
            "longitude": {"$gte": lon - tolerance, "$lte": lon + tolerance}
        }
    
    def _calculate_confidence_score(self, data_points: List[DataPoint], 
                                  query_type: QueryType) -> float:
        """Calculate confidence score for search results"""
        if not data_points:
            return 0.0
        
        # Base confidence on number of results and quality scores
        avg_quality = np.mean([dp.quality_score for dp in data_points])
        result_count_score = min(1.0, len(data_points) / 10)  # Normalize to 10 results
        
        # Weighted combination
        confidence = 0.7 * avg_quality + 0.3 * result_count_score
        
        return min(1.0, max(0.0, confidence))
    
    async def add_data_point(self, data_point: DataPoint) -> bool:
        """Add a data point to the vector database"""
        if not self.initialized:
            return False
        
        try:
            # Generate embedding for the data
            data_text = self._create_data_text(data_point)
            embedding = self.embedding_model.encode([data_text])[0].tolist()
            
            # Prepare document
            document = json.dumps({
                "source": data_point.source.value,
                "data_type": data_point.data_type,
                "location": data_point.location,
                "timestamp": data_point.timestamp.isoformat(),
                "data": data_point.data,
                "metadata": data_point.metadata
            })
            
            # Get appropriate collection
            collection_name = self._get_collection_name_by_data_type(data_point.data_type)
            collection = self.vector_db.get_collection(collection_name)
            
            # Add to collection
            collection.add(
                ids=[data_point.id],
                embeddings=[embedding],
                documents=[document],
                metadatas=[{
                    "source": data_point.source.value,
                    "data_type": data_point.data_type,
                    "timestamp": data_point.timestamp.isoformat(),
                    "quality_score": data_point.quality_score
                }]
            )
            
            logger.info(f"Added data point {data_point.id} to {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding data point: {e}")
            return False
    
    def _create_data_text(self, data_point: DataPoint) -> str:
        """Create searchable text from data point"""
        text_parts = []
        
        # Add data type
        text_parts.append(f"Data type: {data_point.data_type}")
        
        # Add location
        if data_point.location:
            lat = data_point.location.get("latitude", 0)
            lon = data_point.location.get("longitude", 0)
            text_parts.append(f"Location: {lat}, {lon}")
        
        # Add data content
        for key, value in data_point.data.items():
            text_parts.append(f"{key}: {value}")
        
        # Add metadata
        for key, value in data_point.metadata.items():
            text_parts.append(f"{key}: {value}")
        
        return " ".join(text_parts)
    
    def _get_collection_name_by_data_type(self, data_type: str) -> str:
        """Get collection name based on data type"""
        if "solar" in data_type.lower():
            return "solar_data"
        elif "wind" in data_type.lower():
            return "wind_data"
        elif "weather" in data_type.lower():
            return "weather_data"
        elif "regulatory" in data_type.lower():
            return "regulatory_data"
        elif "environmental" in data_type.lower():
            return "environmental_data"
        elif "financial" in data_type.lower():
            return "financial_data"
        else:
            return "site_data"
    
    async def fetch_external_data(self, source: DataSource, 
                                location: Dict[str, float],
                                parameters: Dict[str, Any]) -> List[DataPoint]:
        """Fetch data from external APIs"""
        try:
            if source == DataSource.SOLAR_API:
                return await self._fetch_solar_data(location, parameters)
            elif source == DataSource.WIND_API:
                return await self._fetch_wind_data(location, parameters)
            elif source == DataSource.WEATHER_API:
                return await self._fetch_weather_data(location, parameters)
            elif source == DataSource.GRID_DATA:
                return await self._fetch_grid_data(location, parameters)
            elif source == DataSource.REGULATORY_DB:
                return await self._fetch_regulatory_data(location, parameters)
            elif source == DataSource.ENVIRONMENTAL_DB:
                return await self._fetch_environmental_data(location, parameters)
            elif source == DataSource.FINANCIAL_DB:
                return await self._fetch_financial_data(location, parameters)
            else:
                logger.warning(f"Unknown data source: {source}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching external data from {source}: {e}")
            return []
    
    async def _fetch_solar_data(self, location: Dict[str, float], 
                              parameters: Dict[str, Any]) -> List[DataPoint]:
        """Fetch solar resource data"""
        try:
            lat = location["latitude"]
            lon = location["longitude"]
            
            # Simulate API call (in real implementation, call actual solar API)
            solar_data = {
                "annual_irradiance": 4.5 + np.random.normal(0, 0.5),
                "peak_sun_hours": 5.2 + np.random.normal(0, 0.3),
                "capacity_factor": 0.22 + np.random.normal(0, 0.02),
                "tilt_angle": 30,
                "azimuth_angle": 180
            }
            
            data_point = DataPoint(
                id=f"solar_{lat}_{lon}_{datetime.utcnow().timestamp()}",
                source=DataSource.SOLAR_API,
                data_type="solar_resource",
                location=location,
                timestamp=datetime.utcnow(),
                data=solar_data,
                metadata={
                    "api_version": "1.0",
                    "data_quality": "high",
                    "resolution": "1km"
                },
                quality_score=0.9
            )
            
            return [data_point]
            
        except Exception as e:
            logger.error(f"Error fetching solar data: {e}")
            return []
    
    async def _fetch_wind_data(self, location: Dict[str, float], 
                             parameters: Dict[str, Any]) -> List[DataPoint]:
        """Fetch wind resource data"""
        try:
            lat = location["latitude"]
            lon = location["longitude"]
            
            # Simulate API call
            wind_data = {
                "average_wind_speed": 6.5 + np.random.normal(0, 1.0),
                "wind_direction": 270 + np.random.normal(0, 30),
                "capacity_factor": 0.35 + np.random.normal(0, 0.05),
                "turbulence_intensity": 0.15 + np.random.normal(0, 0.02),
                "wind_shear": 0.2 + np.random.normal(0, 0.05)
            }
            
            data_point = DataPoint(
                id=f"wind_{lat}_{lon}_{datetime.utcnow().timestamp()}",
                source=DataSource.WIND_API,
                data_type="wind_resource",
                location=location,
                timestamp=datetime.utcnow(),
                data=wind_data,
                metadata={
                    "api_version": "1.0",
                    "data_quality": "high",
                    "resolution": "1km"
                },
                quality_score=0.85
            )
            
            return [data_point]
            
        except Exception as e:
            logger.error(f"Error fetching wind data: {e}")
            return []
    
    async def _fetch_weather_data(self, location: Dict[str, float], 
                                parameters: Dict[str, Any]) -> List[DataPoint]:
        """Fetch weather data"""
        try:
            lat = location["latitude"]
            lon = location["longitude"]
            
            # Simulate API call
            weather_data = {
                "temperature": 20 + np.random.normal(0, 5),
                "humidity": 60 + np.random.normal(0, 10),
                "pressure": 1013 + np.random.normal(0, 20),
                "precipitation": np.random.exponential(2),
                "cloud_cover": np.random.uniform(0, 100)
            }
            
            data_point = DataPoint(
                id=f"weather_{lat}_{lon}_{datetime.utcnow().timestamp()}",
                source=DataSource.WEATHER_API,
                data_type="weather_data",
                location=location,
                timestamp=datetime.utcnow(),
                data=weather_data,
                metadata={
                    "api_version": "1.0",
                    "data_quality": "medium",
                    "resolution": "10km"
                },
                quality_score=0.8
            )
            
            return [data_point]
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return []
    
    async def _fetch_grid_data(self, location: Dict[str, float], 
                             parameters: Dict[str, Any]) -> List[DataPoint]:
        """Fetch grid connection data"""
        try:
            lat = location["latitude"]
            lon = location["longitude"]
            
            # Simulate grid data
            grid_data = {
                "nearest_substation_distance": 5 + np.random.exponential(3),
                "grid_capacity": 100 + np.random.normal(0, 20),
                "voltage_level": "138kV",
                "connection_cost_estimate": 50000 + np.random.normal(0, 10000),
                "interconnection_queue": np.random.randint(0, 50)
            }
            
            data_point = DataPoint(
                id=f"grid_{lat}_{lon}_{datetime.utcnow().timestamp()}",
                source=DataSource.GRID_DATA,
                data_type="grid_connection",
                location=location,
                timestamp=datetime.utcnow(),
                data=grid_data,
                metadata={
                    "data_source": "utility_database",
                    "data_quality": "high",
                    "update_frequency": "monthly"
                },
                quality_score=0.9
            )
            
            return [data_point]
            
        except Exception as e:
            logger.error(f"Error fetching grid data: {e}")
            return []
    
    async def _fetch_regulatory_data(self, location: Dict[str, float], 
                                  parameters: Dict[str, Any]) -> List[DataPoint]:
        """Fetch regulatory data"""
        try:
            lat = location["latitude"]
            lon = location["longitude"]
            
            # Simulate regulatory data
            regulatory_data = {
                "zoning_status": "industrial",
                "permit_requirements": ["environmental", "electrical", "building"],
                "setback_requirements": 100,  # meters
                "noise_limits": 45,  # dB
                "environmental_review_required": True,
                "permitting_timeline": 12  # months
            }
            
            data_point = DataPoint(
                id=f"regulatory_{lat}_{lon}_{datetime.utcnow().timestamp()}",
                source=DataSource.REGULATORY_DB,
                data_type="regulatory_info",
                location=location,
                timestamp=datetime.utcnow(),
                data=regulatory_data,
                metadata={
                    "jurisdiction": "state",
                    "data_quality": "high",
                    "last_updated": datetime.utcnow().isoformat()
                },
                quality_score=0.85
            )
            
            return [data_point]
            
        except Exception as e:
            logger.error(f"Error fetching regulatory data: {e}")
            return []
    
    async def _fetch_environmental_data(self, location: Dict[str, float], 
                                      parameters: Dict[str, Any]) -> List[DataPoint]:
        """Fetch environmental data"""
        try:
            lat = location["latitude"]
            lon = location["longitude"]
            
            # Simulate environmental data
            environmental_data = {
                "protected_species": ["bald_eagle", "prairie_chicken"],
                "wetland_proximity": 2.5,  # km
                "wildlife_corridor": True,
                "soil_type": "clay_loam",
                "groundwater_depth": 15,  # meters
                "environmental_sensitivity": "medium"
            }
            
            data_point = DataPoint(
                id=f"environmental_{lat}_{lon}_{datetime.utcnow().timestamp()}",
                source=DataSource.ENVIRONMENTAL_DB,
                data_type="environmental_data",
                location=location,
                timestamp=datetime.utcnow(),
                data=environmental_data,
                metadata={
                    "data_source": "environmental_agency",
                    "data_quality": "high",
                    "survey_date": "2023-01-01"
                },
                quality_score=0.9
            )
            
            return [data_point]
            
        except Exception as e:
            logger.error(f"Error fetching environmental data: {e}")
            return []
    
    async def _fetch_financial_data(self, location: Dict[str, float], 
                                  parameters: Dict[str, Any]) -> List[DataPoint]:
        """Fetch financial data"""
        try:
            lat = location["latitude"]
            lon = location["longitude"]
            
            # Simulate financial data
            financial_data = {
                "electricity_price": 50 + np.random.normal(0, 10),  # $/MWh
                "renewable_energy_credits": 25 + np.random.normal(0, 5),  # $/MWh
                "capacity_payments": 100 + np.random.normal(0, 20),  # $/MW/year
                "tax_incentives": 0.3 + np.random.normal(0, 0.05),  # 30% ITC
                "financing_rate": 0.05 + np.random.normal(0, 0.01)  # 5% interest
            }
            
            data_point = DataPoint(
                id=f"financial_{lat}_{lon}_{datetime.utcnow().timestamp()}",
                source=DataSource.FINANCIAL_DB,
                data_type="financial_data",
                location=location,
                timestamp=datetime.utcnow(),
                data=financial_data,
                metadata={
                    "data_source": "market_database",
                    "data_quality": "high",
                    "update_frequency": "daily"
                },
                quality_score=0.8
            )
            
            return [data_point]
            
        except Exception as e:
            logger.error(f"Error fetching financial data: {e}")
            return []
    
    async def get_data_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored data"""
        try:
            stats = {
                "total_collections": 0,
                "total_documents": 0,
                "collections": {}
            }
            
            collections = ["solar_data", "wind_data", "weather_data", "regulatory_data", 
                          "environmental_data", "financial_data", "site_data"]
            
            for collection_name in collections:
                try:
                    collection = self.vector_db.get_collection(collection_name)
                    count = collection.count()
                    stats["collections"][collection_name] = count
                    stats["total_documents"] += count
                except:
                    stats["collections"][collection_name] = 0
            
            stats["total_collections"] = len(collections)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting data statistics: {e}")
            return {"error": str(e)}
    
    async def clear_cache(self):
        """Clear data cache"""
        self.data_cache.clear()
        logger.info("Data cache cleared")

# Global IR engine instance
ir_engine = InformationRetrievalEngine()