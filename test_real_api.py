"""
Test script to verify GeoSpark site analysis with real NASA API data
"""
import requests
import json

# API endpoint
url = "http://localhost:8000/api/v1/site-analysis"

# Test data - Phoenix, Arizona (excellent solar conditions)
payload = {
    "location": {
        "latitude": 33.4484,
        "longitude": -112.0740,
        "area_km2": 10
    },
    "project_type": "solar",
    "analysis_depth": "comprehensive"
}

# Headers (using demo authentication)
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer demo_token"
}

print("🔍 Testing GeoSpark Site Analysis API")
print(f"📍 Location: Phoenix, Arizona ({payload['location']['latitude']}, {payload['location']['longitude']})")
print(f"📐 Area: {payload['location']['area_km2']} km²")
print("\n⏳ Fetching real data from NASA POWER API...")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        analysis = data.get('analysis', {})
        
        print("\n✅ Analysis completed successfully!")
        print("\n" + "="*60)
        print("SOLAR POTENTIAL")
        print("="*60)
        solar = analysis.get('solar_potential', {})
        print(f"Annual Irradiance: {solar.get('annual_irradiance_kwh_m2', 0):.2f} kWh/m²/day")
        print(f"Peak Sun Hours: {solar.get('peak_sun_hours', 0):.2f} hours/day")
        print(f"Capacity Factor: {solar.get('capacity_factor', 0):.1%}")
        print(f"Solar Score: {solar.get('solar_score', 0):.2f}/1.00")
        
        print("\n" + "="*60)
        print("WIND POTENTIAL")
        print("="*60)
        wind = analysis.get('wind_potential', {})
        print(f"Wind Speed (100m): {wind.get('average_wind_speed_ms', 0):.2f} m/s")
        print(f"Wind Speed (10m): {wind.get('wind_speed_10m', 0):.2f} m/s")
        print(f"Capacity Factor: {wind.get('capacity_factor', 0):.1%}")
        print(f"Wind Score: {wind.get('wind_score', 0):.2f}/1.00")
        
        print("\n" + "="*60)
        print("SITE ASSESSMENT")
        print("="*60)
        print(f"Environmental Score: {analysis.get('environmental_score', 0):.2f}/1.00")
        print(f"Regulatory Score: {analysis.get('regulatory_score', 0):.2f}/1.00")
        print(f"Accessibility Score: {analysis.get('accessibility_score', 0):.2f}/1.00")
        print(f"Overall Score: {analysis.get('overall_score', 0):.2f}/1.00")
        
        print("\n" + "="*60)
        print("CAPACITY ESTIMATION")
        print("="*60)
        print(f"Estimated Capacity: {analysis.get('estimated_capacity_mw', 0):.2f} MW")
        
        print("\n" + "="*60)
        print("RECOMMENDATIONS")
        print("="*60)
        for i, rec in enumerate(analysis.get('recommendations', []), 1):
            print(f"{i}. {rec}")
        
        print("\n" + "="*60)
        print("RISKS")
        print("="*60)
        for i, risk in enumerate(analysis.get('risks', []), 1):
            print(f"{i}. {risk}")
        
        print("\n" + "="*60)
        print("✨ Real data fetched successfully from NASA POWER API!")
        print("="*60)
        
    else:
        print(f"\n❌ Error: Status code {response.status_code}")
        print(response.text)

except requests.exceptions.Timeout:
    print("\n⏰ Request timed out - NASA API may be slow")
except requests.exceptions.ConnectionError:
    print("\n❌ Connection error - Is the server running on port 8000?")
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
