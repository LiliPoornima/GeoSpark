#!/usr/bin/env python3
"""
Redis setup and testing script for GeoSpark
"""

import redis
import json
import time
from typing import Dict, Any

def test_redis_connection(redis_url: str = "redis://localhost:6379/0") -> bool:
    """Test Redis connection"""
    try:
        r = redis.from_url(redis_url)
        r.ping()
        print("✅ Redis connection successful")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def setup_redis_data(redis_url: str = "redis://localhost:6379/0") -> bool:
    """Set up initial Redis data"""
    try:
        r = redis.from_url(redis_url)
        
        # Clear existing data
        r.flushdb()
        print("🗑️ Cleared existing Redis data")
        
        # Set up sample cache data
        sample_data = {
            "site_analysis_cache": {
                "40.7128_-74.0060": {
                    "timestamp": time.time(),
                    "data": {
                        "solar_score": 0.85,
                        "wind_score": 0.72,
                        "overall_score": 0.78
                    }
                }
            },
            "user_sessions": {
                "demo_user": {
                    "last_login": time.time(),
                    "active": True
                }
            },
            "system_stats": {
                "total_analyses": 0,
                "cache_hits": 0,
                "cache_misses": 0
            }
        }
        
        # Store sample data
        for key, value in sample_data.items():
            r.set(key, json.dumps(value))
        
        print("✅ Sample Redis data created")
        
        # Test data retrieval
        cached_data = r.get("site_analysis_cache")
        if cached_data:
            data = json.loads(cached_data)
            print(f"✅ Data retrieval test successful: {len(data)} entries")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis setup failed: {e}")
        return False

def main():
    """Main Redis setup function"""
    print("🚀 Redis Setup for GeoSpark")
    print("=" * 30)
    
    # Test connection
    if not test_redis_connection():
        print("\n❌ Redis setup failed")
        print("Please make sure Redis is installed and running:")
        print("- Ubuntu/Debian: sudo apt-get install redis-server")
        print("- macOS: brew install redis")
        print("- Start Redis: redis-server")
        return False
    
    print()
    
    # Set up data
    if not setup_redis_data():
        return False
    
    print()
    print("✅ Redis setup completed successfully!")
    print("=" * 30)
    print("Redis is ready for GeoSpark caching and session management")
    
    return True

if __name__ == "__main__":
    main()