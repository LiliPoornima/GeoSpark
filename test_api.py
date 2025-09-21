#!/usr/bin/env python3
"""
GeoSpark API Testing Script
Comprehensive testing for all API endpoints
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List

class GeoSparkTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.time()
        })
    
    def test_health_endpoint(self) -> bool:
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health Check", True)
                    return True
            
            self.log_test("Health Check", False, f"Status: {response.status_code}")
            return False
            
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            return False
    
    def test_root_endpoint(self) -> bool:
        """Test root endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "GeoSpark" in data["message"]:
                    self.log_test("Root Endpoint", True)
                    return True
            
            self.log_test("Root Endpoint", False, f"Status: {response.status_code}")
            return False
            
        except Exception as e:
            self.log_test("Root Endpoint", False, str(e))
            return False
    
    def test_authentication(self) -> bool:
        """Test authentication endpoint"""
        try:
            payload = {
                "username": "demo",
                "password": "demo123"
            }
            
            response = self.session.post(f"{self.base_url}/api/v1/authenticate", json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    self.log_test("Authentication", True, f"Token: {data['token'][:20]}...")
                    return True
            
            self.log_test("Authentication", False, f"Status: {response.status_code}")
            return False
            
        except Exception as e:
            self.log_test("Authentication", False, str(e))
            return False
    
    def test_site_analysis(self) -> bool:
        """Test site analysis endpoint"""
        try:
            payload = {
                "location": {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "area_km2": 100
                },
                "project_type": "solar",
                "analysis_depth": "comprehensive"
            }
            
            start_time = time.time()
            response = self.session.post(f"{self.base_url}/api/v1/site-analysis", json=payload)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "analysis" in data:
                    analysis = data["analysis"]
                    if all(key in analysis for key in ["overall_score", "site_id", "recommendations"]):
                        response_time = end_time - start_time
                        self.log_test("Site Analysis", True, 
                                   f"Score: {analysis['overall_score']:.1%}, "
                                   f"Time: {response_time:.2f}s")
                        return True
            
            self.log_test("Site Analysis", False, f"Status: {response.status_code}")
            return False
            
        except Exception as e:
            self.log_test("Site Analysis", False, str(e))
            return False
    
    def test_text_analysis(self) -> bool:
        """Test text analysis endpoint"""
        try:
            payload = {
                "text": "This solar farm project in Texas shows excellent potential for renewable energy generation.",
                "analysis_type": "general"
            }
            
            response = self.session.post(f"{self.base_url}/api/v1/text-analysis", json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "analysis" in data:
                    self.log_test("Text Analysis", True)
                    return True
            
            self.log_test("Text Analysis", False, f"Status: {response.status_code}")
            return False
            
        except Exception as e:
            self.log_test("Text Analysis", False, str(e))
            return False
    
    def test_data_search(self) -> bool:
        """Test data search endpoint"""
        try:
            payload = {
                "query": "solar energy texas",
                "limit": 5
            }
            
            response = self.session.post(f"{self.base_url}/api/v1/data-search", json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "results" in data:
                    results = data["results"]
                    if "total_results" in results:
                        self.log_test("Data Search", True, 
                                   f"Found {results['total_results']} results")
                        return True
            
            self.log_test("Data Search", False, f"Status: {response.status_code}")
            return False
            
        except Exception as e:
            self.log_test("Data Search", False, str(e))
            return False
    
    def test_system_status(self) -> bool:
        """Test system status endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/system-status")
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "status" in data:
                    status = data["status"]
                    if status.get("status") == "operational":
                        self.log_test("System Status", True, 
                                   f"Version: {status.get('version', 'unknown')}")
                        return True
            
            self.log_test("System Status", False, f"Status: {response.status_code}")
            return False
            
        except Exception as e:
            self.log_test("System Status", False, str(e))
            return False
    
    def test_data_statistics(self) -> bool:
        """Test data statistics endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/data-statistics")
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "statistics" in data:
                    stats = data["statistics"]
                    if "total_sites" in stats:
                        self.log_test("Data Statistics", True, 
                                   f"Sites: {stats['total_sites']}")
                        return True
            
            self.log_test("Data Statistics", False, f"Status: {response.status_code}")
            return False
            
        except Exception as e:
            self.log_test("Data Statistics", False, str(e))
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling"""
        try:
            # Test invalid endpoint
            response = self.session.get(f"{self.base_url}/api/v1/invalid-endpoint")
            if response.status_code == 404:
                self.log_test("Error Handling (404)", True)
            else:
                self.log_test("Error Handling (404)", False, f"Status: {response.status_code}")
                return False
            
            # Test invalid authentication
            payload = {"username": "invalid", "password": "invalid"}
            response = self.session.post(f"{self.base_url}/api/v1/authenticate", json=payload)
            if response.status_code == 401:
                self.log_test("Error Handling (401)", True)
            else:
                self.log_test("Error Handling (401)", False, f"Status: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Error Handling", False, str(e))
            return False
    
    def test_performance(self, num_requests: int = 10) -> bool:
        """Test API performance"""
        try:
            payload = {
                "location": {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "area_km2": 100
                },
                "project_type": "solar"
            }
            
            response_times = []
            success_count = 0
            
            for i in range(num_requests):
                start_time = time.time()
                response = self.session.post(f"{self.base_url}/api/v1/site-analysis", json=payload)
                end_time = time.time()
                
                response_times.append(end_time - start_time)
                if response.status_code == 200:
                    success_count += 1
            
            avg_response_time = sum(response_times) / len(response_times)
            success_rate = success_count / num_requests
            
            if success_rate >= 0.9 and avg_response_time < 5.0:
                self.log_test("Performance Test", True, 
                           f"Success: {success_rate:.1%}, Avg Time: {avg_response_time:.2f}s")
                return True
            else:
                self.log_test("Performance Test", False, 
                           f"Success: {success_rate:.1%}, Avg Time: {avg_response_time:.2f}s")
                return False
                
        except Exception as e:
            self.log_test("Performance Test", False, str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return summary"""
        print("🧪 Running GeoSpark API Tests")
        print("=" * 50)
        
        tests = [
            self.test_health_endpoint,
            self.test_root_endpoint,
            self.test_authentication,
            self.test_site_analysis,
            self.test_text_analysis,
            self.test_data_search,
            self.test_system_status,
            self.test_data_statistics,
            self.test_error_handling,
            self.test_performance
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ FAIL {test.__name__} - Exception: {e}")
        
        print("\n" + "=" * 50)
        print(f"📊 Test Summary: {passed}/{total} tests passed ({passed/total:.1%})")
        
        if passed == total:
            print("🎉 All tests passed! GeoSpark API is working correctly.")
        else:
            print("⚠️ Some tests failed. Check the output above for details.")
        
        return {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": total - passed,
            "success_rate": passed / total,
            "test_results": self.test_results
        }

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test GeoSpark API endpoints")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="Base URL for the API (default: http://localhost:8000)")
    parser.add_argument("--performance-requests", type=int, default=10,
                       help="Number of requests for performance test (default: 10)")
    
    args = parser.parse_args()
    
    tester = GeoSparkTester(args.url)
    
    # Override performance test if specified
    if args.performance_requests != 10:
        tester.test_performance = lambda: tester.test_performance(args.performance_requests)
    
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results["success_rate"] == 1.0 else 1)

if __name__ == "__main__":
    main()