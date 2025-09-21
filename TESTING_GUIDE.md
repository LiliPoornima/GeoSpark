# GeoSpark Testing Guide

This guide provides comprehensive testing instructions for the GeoSpark renewable energy analysis platform.

## 🚀 Quick Start Testing

### Option 1: Demo Version (No Dependencies)
```bash
# Run the quick start script
python quick_start.py

# Choose option 1 for demo mode
# This runs without any external dependencies
```

### Option 2: Full API Testing
```bash
# Start the API server
python main.py

# Test endpoints using curl or the frontend
```

### Option 3: Frontend Testing
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

## 🧪 API Testing Examples

### 1. Health Check
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 2. Site Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/site-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "location": {
      "latitude": 40.7128,
      "longitude": -74.0060,
      "area_km2": 100
    },
    "project_type": "solar",
    "analysis_depth": "comprehensive"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "analysis": {
    "site_id": "uuid-here",
    "location": {
      "latitude": 40.7128,
      "longitude": -74.0060,
      "area_km2": 100
    },
    "overall_score": 0.85,
    "solar_potential": {
      "annual_irradiance_kwh_m2": 1800,
      "peak_sun_hours": 6.2,
      "capacity_factor": 0.28,
      "solar_score": 0.88
    },
    "wind_potential": {
      "average_wind_speed_ms": 7.5,
      "capacity_factor": 0.32,
      "wind_score": 0.75
    },
    "environmental_score": 0.82,
    "regulatory_score": 0.78,
    "accessibility_score": 0.90,
    "recommendations": [
      "Consider implementing advanced tracking systems",
      "Evaluate grid connection requirements"
    ],
    "risks": [
      "Potential weather-related disruptions",
      "Regulatory changes may affect project viability"
    ],
    "estimated_capacity_mw": 28.5,
    "analysis_timestamp": "2024-01-15T10:30:00.000Z"
  }
}
```

### 3. Text Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/text-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This solar farm project in Texas shows excellent potential for renewable energy generation.",
    "analysis_type": "general"
  }'
```

### 4. Data Search
```bash
curl -X POST "http://localhost:8000/api/v1/data-search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "solar energy texas",
    "limit": 5
  }'
```

### 5. Authentication (Demo)
```bash
curl -X POST "http://localhost:8000/api/v1/authenticate" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "password": "demo123"
  }'
```

## 🎯 Frontend Testing

### 1. Login Testing
- Navigate to `http://localhost:3000/login`
- Use credentials: `demo` / `demo123`
- Verify successful login and redirect

### 2. Site Analysis Testing
- Navigate to Site Analysis page
- Enter coordinates: `40.7128, -74.0060`
- Set area: `100 km²`
- Select project type: `Solar`
- Click "Analyze Site"
- Verify results display correctly

### 3. Dashboard Testing
- Navigate to Dashboard
- Verify statistics display
- Check charts render properly
- Verify recent activity list

## 🐍 Python Testing Scripts

### Test Script 1: Basic API Tests
```python
#!/usr/bin/env python3
"""
Basic API testing script for GeoSpark
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{API_BASE}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✅ Health check passed")

def test_site_analysis():
    """Test site analysis endpoint"""
    print("Testing site analysis...")
    
    payload = {
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "area_km2": 100
        },
        "project_type": "solar",
        "analysis_depth": "comprehensive"
    }
    
    response = requests.post(f"{API_BASE}/api/v1/site-analysis", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] == True
    assert "analysis" in data
    assert "overall_score" in data["analysis"]
    
    print(f"✅ Site analysis passed - Score: {data['analysis']['overall_score']:.1%}")

def test_text_analysis():
    """Test text analysis endpoint"""
    print("Testing text analysis...")
    
    payload = {
        "text": "This solar farm project shows excellent potential.",
        "analysis_type": "general"
    }
    
    response = requests.post(f"{API_BASE}/api/v1/text-analysis", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] == True
    assert "analysis" in data
    
    print("✅ Text analysis passed")

def test_authentication():
    """Test authentication endpoint"""
    print("Testing authentication...")
    
    payload = {
        "username": "demo",
        "password": "demo123"
    }
    
    response = requests.post(f"{API_BASE}/api/v1/authenticate", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] == True
    assert "token" in data
    
    print("✅ Authentication passed")

def main():
    """Run all tests"""
    print("🧪 Running GeoSpark API Tests")
    print("=" * 40)
    
    try:
        test_health()
        test_site_analysis()
        test_text_analysis()
        test_authentication()
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
```

### Test Script 2: Performance Testing
```python
#!/usr/bin/env python3
"""
Performance testing script for GeoSpark
"""

import requests
import time
import concurrent.futures
import statistics

API_BASE = "http://localhost:8000"

def single_request():
    """Make a single API request"""
    payload = {
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "area_km2": 100
        },
        "project_type": "solar"
    }
    
    start_time = time.time()
    response = requests.post(f"{API_BASE}/api/v1/site-analysis", json=payload)
    end_time = time.time()
    
    return {
        "status_code": response.status_code,
        "response_time": end_time - start_time,
        "success": response.status_code == 200
    }

def performance_test(num_requests=10, concurrent_requests=5):
    """Run performance tests"""
    print(f"🚀 Running performance test: {num_requests} requests, {concurrent_requests} concurrent")
    
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        futures = [executor.submit(single_request) for _ in range(num_requests)]
        
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    
    # Analyze results
    response_times = [r["response_time"] for r in results]
    success_count = sum(1 for r in results if r["success"])
    
    print(f"\n📊 Performance Results:")
    print(f"Total requests: {num_requests}")
    print(f"Successful requests: {success_count}")
    print(f"Success rate: {success_count/num_requests:.1%}")
    print(f"Average response time: {statistics.mean(response_times):.2f}s")
    print(f"Median response time: {statistics.median(response_times):.2f}s")
    print(f"Min response time: {min(response_times):.2f}s")
    print(f"Max response time: {max(response_times):.2f}s")

if __name__ == "__main__":
    performance_test()
```

## 🔧 Database Testing

### Test Database Connection
```bash
# Test PostgreSQL connection
python -c "
import psycopg2
try:
    conn = psycopg2.connect('postgresql://geospark:geospark123@localhost:5432/geospark_db')
    print('✅ Database connection successful')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

### Test Redis Connection
```bash
# Test Redis connection
python -c "
import redis
try:
    r = redis.from_url('redis://localhost:6379/0')
    r.ping()
    print('✅ Redis connection successful')
except Exception as e:
    print(f'❌ Redis connection failed: {e}')
"
```

## 🎨 Frontend Testing

### Manual Testing Checklist

#### Login Page
- [ ] Page loads correctly
- [ ] Username/password fields work
- [ ] Login with demo credentials works
- [ ] Invalid credentials show error
- [ ] Password visibility toggle works

#### Site Analysis Page
- [ ] Form validation works
- [ ] Coordinate input accepts decimal values
- [ ] Area input accepts positive numbers
- [ ] Project type dropdown works
- [ ] Analysis button triggers API call
- [ ] Results display correctly
- [ ] Loading state shows during analysis

#### Dashboard Page
- [ ] Statistics cards display
- [ ] Charts render properly
- [ ] Recent activity list shows data
- [ ] Responsive design works on mobile

#### Navigation
- [ ] All navigation links work
- [ ] Active page highlighting works
- [ ] Logout functionality works
- [ ] User info displays correctly

### Automated Frontend Testing
```bash
# Install testing dependencies
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest

# Run tests
npm test
```

## 🐛 Debugging Tips

### Common Issues and Solutions

#### 1. API Server Won't Start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill process if needed
kill -9 <PID>

# Try different port
uvicorn main:app --port 8001
```

#### 2. Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Check if database exists
psql -U geospark -d geospark_db -c "\l"
```

#### 3. Frontend Build Issues
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for TypeScript errors
npm run build
```

#### 4. CORS Issues
- Ensure CORS middleware is configured in FastAPI
- Check that frontend is running on correct port
- Verify API base URL in frontend configuration

## 📊 Load Testing

### Using Apache Bench (ab)
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test site analysis endpoint
ab -n 100 -c 10 -p site_analysis.json -T application/json http://localhost:8000/api/v1/site-analysis
```

### Using curl for Load Testing
```bash
#!/bin/bash
# Simple load test script

for i in {1..50}; do
  curl -X POST "http://localhost:8000/api/v1/site-analysis" \
    -H "Content-Type: application/json" \
    -d '{"location":{"latitude":40.7128,"longitude":-74.0060,"area_km2":100},"project_type":"solar"}' &
done

wait
echo "Load test completed"
```

## 🎯 Test Scenarios

### Scenario 1: New User Onboarding
1. User visits homepage
2. Clicks "Start Analysis"
3. Enters location details
4. Reviews analysis results
5. Downloads report

### Scenario 2: Bulk Analysis
1. User uploads CSV with multiple locations
2. System processes all locations
3. User reviews batch results
4. User exports comprehensive report

### Scenario 3: Error Handling
1. User enters invalid coordinates
2. System shows appropriate error message
3. User corrects input and retries
4. Analysis completes successfully

## 📈 Monitoring and Metrics

### Key Metrics to Monitor
- API response times
- Success/failure rates
- Database query performance
- Memory usage
- CPU utilization
- Error rates by endpoint

### Health Check Endpoints
```bash
# Basic health check
curl http://localhost:8000/health

# Detailed system status
curl http://localhost:8000/api/v1/system-status

# Data statistics
curl http://localhost:8000/api/v1/data-statistics
```

## 🚀 Production Testing

### Pre-deployment Checklist
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Performance tests meet requirements
- [ ] Security tests pass
- [ ] Database migrations work
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Monitoring configured
- [ ] Backup procedures tested

### Post-deployment Testing
- [ ] Health checks pass
- [ ] API endpoints respond correctly
- [ ] Frontend loads properly
- [ ] Database connections work
- [ ] External API integrations work
- [ ] Logging is working
- [ ] Monitoring dashboards show data

This testing guide provides comprehensive coverage for testing the GeoSpark platform at all levels. Use the appropriate testing methods based on your development stage and requirements.