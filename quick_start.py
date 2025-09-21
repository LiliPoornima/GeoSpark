#!/usr/bin/env python3
"""
GeoSpark Quick Start Script
This script helps you get GeoSpark running quickly with minimal setup
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing Python dependencies...")
    
    try:
        # Install basic dependencies for demo
        basic_deps = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "python-multipart",
            "python-jose[cryptography]",
            "passlib[bcrypt]",
            "python-dotenv"
        ]
        
        for dep in basic_deps:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create a basic .env file"""
    env_content = """# GeoSpark Configuration
# This is a minimal configuration for demo purposes

# Application Settings
APP_NAME=GeoSpark
APP_VERSION=1.0.0
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Security (for demo only - change in production)
SECRET_KEY=demo_secret_key_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database (using SQLite for demo)
DATABASE_URL=sqlite:///./geospark_demo.db

# Redis (optional for demo)
REDIS_URL=redis://localhost:6379/0

# API Keys (optional - add your keys for full functionality)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
MAX_REQUESTS_PER_HOUR=1000
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Created .env file")
    else:
        print("ℹ️ .env file already exists")

def create_simple_main():
    """Create a simplified main.py for demo"""
    main_content = '''#!/usr/bin/env python3
"""
GeoSpark - Simplified Demo Version
Run this with: python main.py
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import json
import asyncio
from datetime import datetime
import uuid

# Import the demo functionality
from demo import GeoSparkDemo

app = FastAPI(
    title="GeoSpark Demo API",
    description="AI-powered renewable energy analysis platform - Demo Version",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize demo
demo = GeoSparkDemo()

# Pydantic models
class Location(BaseModel):
    latitude: float
    longitude: float
    area_km2: float = 100

class SiteAnalysisRequest(BaseModel):
    location: Location
    project_type: str = "solar"
    analysis_depth: str = "comprehensive"

class TextAnalysisRequest(BaseModel):
    text: str
    analysis_type: str = "general"

class DataSearchRequest(BaseModel):
    query: str
    limit: int = 5

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Welcome to GeoSpark Demo API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/site-analysis")
async def analyze_site(request: SiteAnalysisRequest):
    """Analyze a site for renewable energy potential"""
    try:
        from demo import SiteAnalysisRequest as DemoRequest
        
        demo_request = DemoRequest(
            location=request.location.dict(),
            project_type=request.project_type,
            analysis_depth=request.analysis_depth
        )
        
        result = await demo.analyze_site(demo_request)
        
        return {
            "success": True,
            "analysis": {
                "site_id": result.site_id,
                "location": result.location,
                "overall_score": result.overall_score,
                "solar_potential": result.solar_potential,
                "wind_potential": result.wind_potential,
                "environmental_score": result.environmental_score,
                "regulatory_score": result.regulatory_score,
                "accessibility_score": result.accessibility_score,
                "recommendations": result.recommendations,
                "risks": result.risks,
                "estimated_capacity_mw": result.estimated_capacity_mw,
                "analysis_timestamp": result.analysis_timestamp.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/text-analysis")
async def analyze_text(request: TextAnalysisRequest):
    """Analyze text using NLP"""
    try:
        result = await demo.analyze_text(request.text, request.analysis_type)
        return {"success": True, "analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/data-search")
async def search_data(request: DataSearchRequest):
    """Search renewable energy data"""
    try:
        result = await demo.search_data(request.query)
        return {"success": True, "results": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/system-status")
async def get_system_status():
    """Get system status"""
    try:
        status = demo.get_system_status()
        return {"success": True, "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/data-statistics")
async def get_data_statistics():
    """Get data statistics"""
    try:
        stats = demo.get_data_statistics()
        return {"success": True, "statistics": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/authenticate")
async def authenticate(credentials: Dict[str, str]):
    """Mock authentication for demo"""
    username = credentials.get("username", "")
    password = credentials.get("password", "")
    
    # Demo credentials
    if username == "demo" and password == "demo123":
        return {
            "success": True,
            "token": "demo_token_" + str(uuid.uuid4()),
            "user": {
                "id": "1",
                "username": username,
                "email": f"{username}@geospark.com",
                "role": "user"
            }
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

if __name__ == "__main__":
    print("🚀 Starting GeoSpark Demo API...")
    print("=" * 40)
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("=" * 40)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
'''
    
    with open("main.py", "w") as f:
        f.write(main_content)
    
    print("✅ Created simplified main.py")

def run_demo():
    """Run the demo"""
    print("🚀 Starting GeoSpark Demo...")
    print("=" * 40)
    
    try:
        # Run the demo
        subprocess.run([sys.executable, "demo.py"])
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"❌ Demo failed: {e}")

def run_api():
    """Run the API server"""
    print("🌐 Starting GeoSpark API Server...")
    print("=" * 40)
    print("API will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop")
    print("=" * 40)
    
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n👋 API server stopped by user")
    except Exception as e:
        print(f"❌ API server failed: {e}")

def main():
    """Main quick start function"""
    print("🌱 GeoSpark Quick Start")
    print("=" * 30)
    print("This script will help you get GeoSpark running quickly")
    print()
    
    # Check Python version
    if not check_python_version():
        return
    
    print()
    
    # Install dependencies
    if not install_dependencies():
        return
    
    print()
    
    # Create configuration files
    create_env_file()
    create_simple_main()
    
    print()
    print("✅ Quick start setup completed!")
    print("=" * 30)
    print()
    print("What would you like to do next?")
    print("1. Run the demo (command line)")
    print("2. Start the API server")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            run_demo()
            break
        elif choice == "2":
            run_api()
            break
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()