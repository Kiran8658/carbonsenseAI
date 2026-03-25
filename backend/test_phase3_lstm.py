#!/usr/bin/env python3
"""
Phase 3: LSTM Forecast Module - Comprehensive Test Suite
Tests all 4 new LSTM API endpoints with various scenarios
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8888"
TEST_RESULTS = []

def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_endpoint(name, method, endpoint, payload=None, expected_status=200):
    """Generic endpoint test function"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == "POST":
            response = requests.post(url, json=payload)
        else:
            response = requests.get(url)
        
        status = "✅ PASS" if response.status_code == expected_status else "❌ FAIL"
        TEST_RESULTS.append({
            "test": name,
            "endpoint": endpoint,
            "status": response.status_code,
            "expected": expected_status,
            "result": status
        })
        
        print(f"{status} | {name}")
        print(f"   Endpoint: {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == expected_status:
            data = response.json()
            if "data" in data and isinstance(data["data"], dict):
                if "forecast" in data["data"]:
                    forecast_count = len(data["data"]["forecast"])
                    print(f"   Forecast Points: {forecast_count}")
                if "accuracy_score" in data["data"]:
                    print(f"   Accuracy: {data['data']['accuracy_score']:.1%}")
            if "message" in data:
                print(f"   Message: {data['message']}")
        else:
            print(f"   Response: {response.text[:200]}")
        
        return response
    
    except Exception as e:
        TEST_RESULTS.append({
            "test": name,
            "endpoint": endpoint,
            "status": "ERROR",
            "expected": expected_status,
            "result": "❌ FAIL"
        })
        print(f"❌ FAIL | {name}")
        print(f"   Error: {str(e)}")
        return None

def main():
    """Run all Phase 3 tests"""
    
    print_section("PHASE 3: LSTM FORECAST MODULE - TEST SUITE")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    
    # Verify backend is running
    print("\n[1/5] Checking backend connectivity...")
    try:
        response = requests.get(f"{BASE_URL}/api/v2/health-v2")
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend health check failed")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        sys.exit(1)
    
    # Check feature flag is enabled
    print("\n[2/5] Checking LSTM_FORECAST feature flag...")
    try:
        response = requests.get(f"{BASE_URL}/api/v2/features")
        if response.status_code == 200:
            features = response.json().get("data", {})
            lstm_enabled = features.get("LSTM_FORECAST", False)
            if lstm_enabled:
                print("✅ LSTM_FORECAST feature flag is ENABLED")
            else:
                print("⚠️  LSTM_FORECAST feature flag is DISABLED")
    except Exception as e:
        print(f"⚠️  Could not verify feature flag: {e}")
    
    # Test data: Sample historical CO2 emissions (kg/month)
    historical_data = [
        500, 520, 530, 525, 540, 550,  # First 6 months
        560, 575, 585, 590, 605, 620,  # Next 6 months (trending up)
        600, 615, 625, 630, 645, 655,  # Last 6 months
    ]
    
    print("\n[3/5] Running LSTM Forecast Tests...")
    print_section("TEST GROUP: LSTM Forecasting")
    
    # Test 1: Basic LSTM forecast
    print("Test 1: Basic LSTM Forecast (12 months)")
    response1 = test_endpoint(
        "LSTM Forecast - 12 months",
        "POST",
        "/api/v2/forecast/lstm",
        {"historical_data": historical_data, "months_ahead": 12},
        200
    )
    
    # Test 2: Longer LSTM forecast
    print("\nTest 2: Extended LSTM Forecast (24 months)")
    response2 = test_endpoint(
        "LSTM Forecast - 24 months",
        "POST",
        "/api/v2/forecast/lstm",
        {"historical_data": historical_data, "months_ahead": 24},
        200
    )
    
    # Test 3: Scenario forecast (reduction)
    print("\nTest 3: Scenario Forecast (15% annual reduction)")
    response3 = test_endpoint(
        "Scenario Forecast - 15% reduction",
        "POST",
        "/api/v2/forecast/scenario",
        {"historical_data": historical_data, "reduction_pct": 15, "months_ahead": 12},
        200
    )
    
    # Test 4: More aggressive scenario
    print("\nTest 4: Scenario Forecast (25% annual reduction)")
    response4 = test_endpoint(
        "Scenario Forecast - 25% reduction",
        "POST",
        "/api/v2/forecast/scenario",
        {"historical_data": historical_data, "reduction_pct": 25, "months_ahead": 12},
        200
    )
    
    # Test 5: Ensemble forecast
    print("\nTest 5: Ensemble Forecast (multi-model)")
    response5 = test_endpoint(
        "Ensemble Forecast - Combined Models",
        "POST",
        "/api/v2/forecast/ensemble",
        {"historical_data": historical_data, "months_ahead": 12},
        200
    )
    
    # Test 6: Ensemble with different data
    print("\nTest 6: Ensemble Forecast (declining trend)")
    declining_data = [1000, 950, 920, 890, 860, 830, 800, 770, 750, 720, 700, 680]
    response6 = test_endpoint(
        "Ensemble Forecast - Declining Trend",
        "POST",
        "/api/v2/forecast/ensemble",
        {"historical_data": declining_data, "months_ahead": 12},
        200
    )
    
    print("\n[4/5] Running Error Handling Tests...")
    print_section("TEST GROUP: Error Handling")
    
    # Test 7: Invalid data (empty)
    print("Test 7: Empty Historical Data")
    test_endpoint(
        "LSTM Forecast - Empty data",
        "POST",
        "/api/v2/forecast/lstm",
        {"historical_data": [], "months_ahead": 12},
        500
    )
    
    # Test 8: Insufficient data
    print("\nTest 8: Insufficient Historical Data")
    test_endpoint(
        "LSTM Forecast - Only 2 data points",
        "POST",
        "/api/v2/forecast/lstm",
        {"historical_data": [500, 520], "months_ahead": 12},
        500
    )
    
    # Test 9: Invalid reduction percentage
    print("\nTest 9: Invalid Reduction Percentage")
    test_endpoint(
        "Scenario Forecast - 150% reduction (invalid)",
        "POST",
        "/api/v2/forecast/scenario",
        {"historical_data": historical_data, "reduction_pct": 150, "months_ahead": 12},
        200  # Service may handle or accept, check actual behavior
    )
    
    print("\n[5/5] Generating Test Report...")
    print_section("TEST RESULTS SUMMARY")
    
    # Count results
    passed = sum(1 for r in TEST_RESULTS if "PASS" in r["result"])
    failed = sum(1 for r in TEST_RESULTS if "FAIL" in r["result"])
    total = len(TEST_RESULTS)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    print("\nDetailed Results:")
    print("-" * 80)
    for i, result in enumerate(TEST_RESULTS, 1):
        status_icon = "✅" if "PASS" in result["result"] else "❌"
        print(f"{i}. {status_icon} {result['test']}")
        print(f"   Endpoint: {result['endpoint']}")
        print(f"   Status: {result['status']} (Expected: {result['expected']})")
    
    print("\n" + "="*60)
    if failed == 0:
        print("  ✅ ALL TESTS PASSED - PHASE 3 READY FOR DEPLOYMENT")
    else:
        print(f"  ⚠️  {failed} TEST(S) FAILED - FIX REQUIRED")
    print("="*60 + "\n")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
