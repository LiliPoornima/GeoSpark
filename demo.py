#!/usr/bin/env python3
"""
GeoSpark Demo - Simplified version without external dependencies
This version uses mock data and doesn't require PostgreSQL or Redis
"""

import asyncio
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import random
import math

# Mock data for demonstration
MOCK_SITES = [
    {
        "id": str(uuid.uuid4()),
        "name": "Solar Farm - Texas",
        "location": {"latitude": 32.7767, "longitude": -96.7970, "area_km2": 500},
        "project_type": "solar",
        "overall_score": 0.92,
        "solar_potential": {"annual_irradiance_kwh_m2": 1800, "capacity_factor": 0.28},
        "environmental_score": 0.88,
        "regulatory_score": 0.85,
        "estimated_capacity_mw": 150.0,
        "created_at": datetime.now() - timedelta(days=2)
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Wind Project - California",
        "location": {"latitude": 34.0522, "longitude": -118.2437, "area_km2": 200},
        "project_type": "wind",
        "overall_score": 0.88,
        "wind_potential": {"average_wind_speed_ms": 8.5, "capacity_factor": 0.35},
        "environmental_score": 0.82,
        "regulatory_score": 0.90,
        "estimated_capacity_mw": 80.0,
        "created_at": datetime.now() - timedelta(days=5)
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Hybrid System - Nevada",
        "location": {"latitude": 36.1699, "longitude": -115.1398, "area_km2": 300},
        "project_type": "hybrid",
        "overall_score": 0.85,
        "solar_potential": {"annual_irradiance_kwh_m2": 2200, "capacity_factor": 0.32},
        "wind_potential": {"average_wind_speed_ms": 7.2, "capacity_factor": 0.28},
        "environmental_score": 0.90,
        "regulatory_score": 0.78,
        "estimated_capacity_mw": 120.0,
        "created_at": datetime.now() - timedelta(days=1)
    }
]

@dataclass
class SiteAnalysisRequest:
    location: Dict[str, float]
    project_type: str
    analysis_depth: str = "comprehensive"

@dataclass
class SiteAnalysisResult:
    site_id: str
    location: Dict[str, float]
    overall_score: float
    solar_potential: Dict[str, float]
    wind_potential: Dict[str, float]
    environmental_score: float
    regulatory_score: float
    accessibility_score: float
    recommendations: List[str]
    risks: List[str]
    estimated_capacity_mw: float
    analysis_timestamp: datetime
    # Protected land flags
    protected_overlap: bool
    protected_nearby_km: Optional[float]
    protected_features: List[Dict[str, Any]]
    # Suitability status based on constraints
    suitability: str  # 'suitable' | 'caution' | 'unsuitable'

class MockLLMService:
    """Mock LLM service for demo purposes"""
    
    @staticmethod
    async def analyze_text(text: str, analysis_type: str = "general") -> Dict[str, Any]:
        """Mock text analysis"""
        await asyncio.sleep(0.1)  # Simulate API call
        
        return {
            "analysis_type": analysis_type,
            "sentiment": random.choice(["positive", "neutral", "negative"]),
            "keywords": ["renewable", "energy", "solar", "wind", "sustainability"],
            "summary": f"Analysis of text containing {len(text.split())} words",
            "confidence": random.uniform(0.7, 0.95)
        }
    
    @staticmethod
    async def generate_recommendations(site_data: Dict[str, Any]) -> List[str]:
        """Generate mock recommendations"""
        await asyncio.sleep(0.2)
        
        recommendations = [
            "Consider implementing advanced tracking systems for optimal energy capture",
            "Evaluate grid connection requirements and upgrade infrastructure if needed",
            "Assess environmental impact and implement mitigation strategies",
            "Review local regulations and obtain necessary permits",
            "Consider energy storage solutions for improved reliability"
        ]
        
        return random.sample(recommendations, random.randint(2, 4))
    
    @staticmethod
    async def identify_risks(site_data: Dict[str, Any]) -> List[str]:
        """Identify mock risks"""
        await asyncio.sleep(0.15)
        
        risks = [
            "Potential weather-related disruptions",
            "Regulatory changes may affect project viability",
            "Grid connection capacity limitations",
            "Environmental impact concerns",
            "Market price volatility for energy sales"
        ]
        
        return random.sample(risks, random.randint(1, 3))

class MockNLPService:
    """Mock NLP service for demo purposes"""
    
    @staticmethod
    async def extract_entities(text: str) -> Dict[str, List[str]]:
        """Extract mock entities"""
        await asyncio.sleep(0.05)
        
        return {
            "locations": ["Texas", "California", "Nevada"],
            "organizations": ["Solar Corp", "Wind Energy Inc"],
            "technologies": ["solar panels", "wind turbines", "battery storage"],
            "dates": ["2024", "2025"]
        }
    
    @staticmethod
    async def summarize_text(text: str) -> str:
        """Generate mock summary"""
        await asyncio.sleep(0.1)
        
        return f"Summary: This text discusses renewable energy projects with focus on {random.choice(['solar', 'wind', 'hybrid'])} technologies."

class MockIRService:
    """Mock Information Retrieval service"""
    
    def __init__(self):
        self.documents = [
            {"id": "1", "content": "Solar energy potential in Texas is excellent", "metadata": {"type": "solar"}},
            {"id": "2", "content": "Wind resources in California coastal areas", "metadata": {"type": "wind"}},
            {"id": "3", "content": "Hybrid renewable energy systems", "metadata": {"type": "hybrid"}},
        ]
    
    async def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Mock document search"""
        await asyncio.sleep(0.1)
        
        # Simple keyword matching
        results = []
        query_lower = query.lower()
        
        for doc in self.documents:
            if any(word in doc["content"].lower() for word in query_lower.split()):
                results.append({
                    "id": doc["id"],
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "score": random.uniform(0.7, 0.95)
                })
        
        return results[:limit]

class GeoSparkDemo:
    """Main GeoSpark Demo class"""
    
    def __init__(self):
        self.llm_service = MockLLMService()
        self.nlp_service = MockNLPService()
        self.ir_service = MockIRService()
        self.analysis_history = []
    
    async def analyze_site(self, request: SiteAnalysisRequest) -> SiteAnalysisResult:
        """Perform comprehensive site analysis"""
        print(f"🔍 Analyzing site at {request.location['latitude']:.4f}, {request.location['longitude']:.4f}")
        
        # Simulate analysis time
        await asyncio.sleep(1.0)
        
        # Generate mock analysis results
        site_id = str(uuid.uuid4())
        
        # Calculate scores based on location (mock calculation)
        lat = request.location["latitude"]
        lng = request.location["longitude"]
        
        # Solar potential (higher in southern latitudes)
        solar_score = max(0.3, min(0.95, 0.7 + (30 - abs(lat)) * 0.01))
        solar_potential = {
            "annual_irradiance_kwh_m2": random.uniform(1200, 2500),
            "peak_sun_hours": random.uniform(4.5, 7.0),
            "capacity_factor": random.uniform(0.22, 0.35),
            "solar_score": solar_score
        }
        
        # Wind potential (mock calculation)
        wind_score = max(0.2, min(0.9, 0.5 + random.uniform(-0.2, 0.3)))
        wind_potential = {
            "average_wind_speed_ms": random.uniform(5.0, 12.0),
            "capacity_factor": random.uniform(0.25, 0.45),
            "wind_score": wind_score
        }
        
        # Other scores
        environmental_score = random.uniform(0.6, 0.95)
        regulatory_score = random.uniform(0.5, 0.9)
        accessibility_score = random.uniform(0.7, 0.95)
        
        # Simple protected areas check via Overpass (OpenStreetMap)
        # We look for nature reserve/protected areas within ~2km radius
        protected_overlap = False
        protected_nearby_km: Optional[float] = None
        protected_features: List[Dict[str, Any]] = []
        try:
            import httpx
            # Radius in meters (wider radius improves detection for large reserves)
            radius_m = 25000
            overpass_q = (
                f"[out:json][timeout:20];"
                f"("
                f"  nwr[boundary=protected_area](around:{radius_m},{lat},{lng});"
                f"  nwr[leisure=nature_reserve](around:{radius_m},{lat},{lng});"
                f"  nwr[boundary=national_park](around:{radius_m},{lat},{lng});"
                f"  nwr[protect_class](around:{radius_m},{lat},{lng});"
                f"  nwr[protection_title](around:{radius_m},{lat},{lng});"
                f"  nwr[protect_title](around:{radius_m},{lat},{lng});"
                f");"
                f"out center qt;"
            )
            headers = {"User-Agent": "GeoSpark-Demo/1.0 (contact: demo@example.com)"}
            endpoints = [
                "https://overpass-api.de/api/interpreter",
                "https://overpass.kumi.systems/api/interpreter",
                "https://lz4.overpass-api.de/api/interpreter",
            ]
            elements: List[Dict[str, Any]] = []
            async with httpx.AsyncClient(timeout=20, headers=headers) as client:
                for ep in endpoints:
                    try:
                        resp = await client.get(ep, params={"data": overpass_q})
                        if resp.status_code == 200:
                            data = resp.json()
                            elements = data.get("elements", [])
                            if elements:
                                break
                    except Exception:
                        continue
                # Fallback: use is_in to find protected polygons containing the point
                if not elements:
                    is_in_q = (
                        f"[out:json][timeout:20];"
                        f"is_in({lat},{lng})->.a;"
                        f"area.a[boundary=protected_area];"
                        f"rel(area);out center qt;"
                    )
                    for ep in endpoints:
                        try:
                            resp = await client.get(ep, params={"data": is_in_q})
                            if resp.status_code == 200:
                                data = resp.json()
                                elements = data.get("elements", [])
                                if elements:
                                    break
                        except Exception:
                            continue
            for el in elements[:50]:
                tags = el.get("tags", {})
                name = tags.get("name") or tags.get("protect_title") or "Protected Area"
                # Compute rough distance if center provided
                center = el.get("center") or {"lat": el.get("lat"), "lon": el.get("lon")}
                d_km = None
                if center and center.get("lat") is not None and center.get("lon") is not None:
                    d_km = self._haversine_km(lat, lng, center["lat"], center["lon"])
                    if protected_nearby_km is None or (d_km is not None and d_km < protected_nearby_km):
                        protected_nearby_km = d_km
                protected_features.append({
                    "id": el.get("id"),
                    "type": el.get("type"),
                    "name": name,
                    "distance_km": d_km,
                    "tags": tags
                })
            protected_overlap = len(elements) > 0
        except Exception:
            # Network or API failure shouldn't break analysis in demo
            pass

        # Secondary fallback: Nominatim reverse-geocoding keyword screening
        if not protected_overlap:
            try:
                import httpx
                headers = {"User-Agent": "GeoSpark-Demo/1.0 (contact: demo@example.com)"}
                async with httpx.AsyncClient(timeout=12, headers=headers) as client:
                    r = await client.get(
                        "https://nominatim.openstreetmap.org/reverse",
                        params={"format": "json", "lat": lat, "lon": lng, "zoom": 14, "addressdetails": 1},
                    )
                    if r.status_code == 200:
                        j = r.json()
                        text = (j.get("display_name") or "").lower()
                        cats = [j.get("category", ""), j.get("type", ""), j.get("addresstype", "")]
                        keywords = [
                            "national park", "forest reserve", "nature reserve", "protected area",
                            "wildlife reserve", "conservation", "sanctuary", "biosphere"
                        ]
                        if any(k in text for k in keywords) or any(k in (c or "") for c in cats for k in ["park", "reserve", "forest", "protected", "conservation"]):
                            protected_overlap = True
                            name = j.get("name") or (j.get("address", {}) or {}).get("suburb") or "Protected Area"
                            protected_features.append({
                                "id": None,
                                "type": j.get("type"),
                                "name": name,
                                "distance_km": 0.0,
                                "tags": {"source": "nominatim"}
                            })
                            protected_nearby_km = 0.0 if protected_nearby_km is None else protected_nearby_km
            except Exception:
                pass

        # If protected area detected, degrade environmental score and mark suitability
        suitability = "suitable"
        if protected_overlap:
            environmental_score = min(environmental_score, 0.3)
            risks.append("Site intersects or is adjacent to protected land; development likely restricted.")
            # Strengthen recommendation to avoid development
            recommendations = [
                "Do not proceed with development due to protected-area constraints.",
                "Engage environmental authorities to confirm legal boundaries and restrictions.",
                "Consider alternative sites outside protected or conservation zones."
            ] + recommendations
            suitability = "unsuitable"

        # Overall score
        if request.project_type == "solar":
            overall_score = (solar_score + environmental_score + regulatory_score + accessibility_score) / 4
        elif request.project_type == "wind":
            overall_score = (wind_score + environmental_score + regulatory_score + accessibility_score) / 4
        else:  # hybrid
            overall_score = (solar_score + wind_score + environmental_score + regulatory_score + accessibility_score) / 5
        
        # Generate recommendations and risks
        site_data = {
            "location": request.location,
            "project_type": request.project_type,
            "solar_potential": solar_potential,
            "wind_potential": wind_potential
        }
        
        recommendations = await self.llm_service.generate_recommendations(site_data)
        risks = await self.llm_service.identify_risks(site_data)
        
        # Estimate capacity
        area_km2 = request.location.get("area_km2", 100)
        if request.project_type == "solar":
            estimated_capacity_mw = area_km2 * random.uniform(0.2, 0.4)
        elif request.project_type == "wind":
            estimated_capacity_mw = area_km2 * random.uniform(0.1, 0.3)
        else:  # hybrid
            estimated_capacity_mw = area_km2 * random.uniform(0.15, 0.35)
        
        result = SiteAnalysisResult(
            site_id=site_id,
            location=request.location,
            overall_score=overall_score,
            solar_potential=solar_potential,
            wind_potential=wind_potential,
            environmental_score=environmental_score,
            regulatory_score=regulatory_score,
            accessibility_score=accessibility_score,
            recommendations=recommendations,
            risks=risks,
            estimated_capacity_mw=estimated_capacity_mw,
            analysis_timestamp=datetime.now(),
            protected_overlap=protected_overlap,
            protected_nearby_km=protected_nearby_km,
            protected_features=protected_features,
            suitability=suitability
        )
        
        # Store in history
        self.analysis_history.append(result)
        
        return result

    @staticmethod
    def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        # Calculate great-circle distance in kilometers
        R = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    
    async def analyze_text(self, text: str, analysis_type: str = "general") -> Dict[str, Any]:
        """Analyze text using NLP"""
        print(f"📝 Analyzing text: {text[:50]}...")
        
        # Run NLP analysis
        entities = await self.nlp_service.extract_entities(text)
        summary = await self.nlp_service.summarize_text(text)
        llm_analysis = await self.llm_service.analyze_text(text, analysis_type)
        
        return {
            "entities": entities,
            "summary": summary,
            "llm_analysis": llm_analysis,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    async def search_data(self, query: str) -> Dict[str, Any]:
        """Search renewable energy data"""
        print(f"🔍 Searching for: {query}")
        
        # Search documents
        documents = await self.ir_service.search_documents(query)
        
        # Analyze query with NLP
        query_analysis = await self.nlp_service.extract_entities(query)
        
        return {
            "query": query,
            "documents": documents,
            "query_analysis": query_analysis,
            "total_results": len(documents),
            "search_timestamp": datetime.now().isoformat()
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            "status": "operational",
            "version": "1.0.0-demo",
            "uptime": "24h 15m",
            "total_analyses": len(self.analysis_history),
            "cache_status": "active",
            "llm_providers": ["mock_openai", "mock_anthropic"],
            "database_status": "mock",
            "redis_status": "mock",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_data_statistics(self) -> Dict[str, Any]:
        """Get data statistics"""
        return {
            "total_sites": len(MOCK_SITES),
            "total_analyses": len(self.analysis_history),
            "project_types": {
                "solar": len([s for s in MOCK_SITES if s["project_type"] == "solar"]),
                "wind": len([s for s in MOCK_SITES if s["project_type"] == "wind"]),
                "hybrid": len([s for s in MOCK_SITES if s["project_type"] == "hybrid"])
            },
            "average_score": sum(s["overall_score"] for s in MOCK_SITES) / len(MOCK_SITES),
            "total_capacity_mw": sum(s["estimated_capacity_mw"] for s in MOCK_SITES),
            "timestamp": datetime.now().isoformat()
        }

async def demo_interactive():
    """Interactive demo mode"""
    demo = GeoSparkDemo()
    
    print("🌱 GeoSpark Demo - Interactive Mode")
    print("=" * 40)
    print("This is a simplified version that runs without external dependencies")
    print("All data is mock data for demonstration purposes")
    print()
    
    while True:
        print("\nAvailable commands:")
        print("1. Analyze site")
        print("2. Analyze text")
        print("3. Search data")
        print("4. System status")
        print("5. Data statistics")
        print("6. View mock sites")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-6): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
        
        elif choice == "1":
            print("\n📍 Site Analysis")
            try:
                lat = float(input("Enter latitude: "))
                lng = float(input("Enter longitude: "))
                area = float(input("Enter area (km²) [default: 100]: ") or "100")
                project_type = input("Project type (solar/wind/hybrid) [default: solar]: ").strip() or "solar"
                
                request = SiteAnalysisRequest(
                    location={"latitude": lat, "longitude": lng, "area_km2": area},
                    project_type=project_type
                )
                
                result = await demo.analyze_site(request)
                
                print(f"\n✅ Analysis Complete!")
                print(f"Site ID: {result.site_id}")
                print(f"Overall Score: {result.overall_score:.1%}")
                print(f"Estimated Capacity: {result.estimated_capacity_mw:.1f} MW")
                print(f"Recommendations: {len(result.recommendations)}")
                print(f"Risks: {len(result.risks)}")
                
            except ValueError:
                print("❌ Invalid input. Please enter valid numbers.")
        
        elif choice == "2":
            print("\n📝 Text Analysis")
            text = input("Enter text to analyze: ")
            analysis_type = input("Analysis type [default: general]: ").strip() or "general"
            
            result = await demo.analyze_text(text, analysis_type)
            
            print(f"\n✅ Text Analysis Complete!")
            print(f"Summary: {result['summary']}")
            print(f"Sentiment: {result['llm_analysis']['sentiment']}")
            print(f"Keywords: {', '.join(result['llm_analysis']['keywords'])}")
        
        elif choice == "3":
            print("\n🔍 Data Search")
            query = input("Enter search query: ")
            
            result = await demo.search_data(query)
            
            print(f"\n✅ Search Complete!")
            print(f"Found {result['total_results']} documents")
            for doc in result['documents']:
                print(f"- {doc['content']} (score: {doc['score']:.2f})")
        
        elif choice == "4":
            print("\n📊 System Status")
            status = demo.get_system_status()
            
            print(f"Status: {status['status']}")
            print(f"Version: {status['version']}")
            print(f"Uptime: {status['uptime']}")
            print(f"Total Analyses: {status['total_analyses']}")
        
        elif choice == "5":
            print("\n📈 Data Statistics")
            stats = demo.get_data_statistics()
            
            print(f"Total Sites: {stats['total_sites']}")
            print(f"Total Analyses: {stats['total_analyses']}")
            print(f"Average Score: {stats['average_score']:.1%}")
            print(f"Total Capacity: {stats['total_capacity_mw']:.1f} MW")
        
        elif choice == "6":
            print("\n🏗️ Mock Sites")
            for site in MOCK_SITES:
                print(f"- {site['name']}: {site['overall_score']:.1%} score, {site['estimated_capacity_mw']:.1f} MW")
        
        else:
            print("❌ Invalid choice. Please try again.")

async def demo_automated():
    """Automated demo with sample data"""
    demo = GeoSparkDemo()
    
    print("🤖 GeoSpark Demo - Automated Mode")
    print("=" * 40)
    
    # Sample analyses
    sample_sites = [
        {"location": {"latitude": 40.7128, "longitude": -74.0060, "area_km2": 100}, "project_type": "solar"},
        {"location": {"latitude": 34.0522, "longitude": -118.2437, "area_km2": 200}, "project_type": "wind"},
        {"location": {"latitude": 36.1699, "longitude": -115.1398, "area_km2": 300}, "project_type": "hybrid"}
    ]
    
    print("\n📍 Running sample site analyses...")
    for i, site_data in enumerate(sample_sites, 1):
        print(f"\n{i}. Analyzing {site_data['project_type']} project...")
        request = SiteAnalysisRequest(**site_data)
        result = await demo.analyze_site(request)
        
        print(f"   Score: {result.overall_score:.1%}")
        print(f"   Capacity: {result.estimated_capacity_mw:.1f} MW")
        print(f"   Recommendations: {len(result.recommendations)}")
    
    print("\n📝 Running text analysis...")
    sample_text = "This solar farm project in Texas shows excellent potential for renewable energy generation."
    text_result = await demo.analyze_text(sample_text)
    print(f"Sentiment: {text_result['llm_analysis']['sentiment']}")
    print(f"Summary: {text_result['summary']}")
    
    print("\n🔍 Running data search...")
    search_result = await demo.search_data("solar energy texas")
    print(f"Found {search_result['total_results']} relevant documents")
    
    print("\n📊 System Status:")
    status = demo.get_system_status()
    print(f"Total analyses completed: {status['total_analyses']}")
    
    print("\n✅ Demo completed successfully!")

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        asyncio.run(demo_interactive())
    else:
        asyncio.run(demo_automated())

if __name__ == "__main__":
    main()