#!/usr/bin/env python3
"""
Service App API Testing Script - Simple Version
Tests all endpoints with real database connection
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8002"

def test_endpoint(method, endpoint, data=None, headers=None, expected_status=200):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        
        print(f"[OK] {method} {endpoint} - Status: {response.status_code}")
        
        if response.status_code == expected_status:
            try:
                result = response.json()
                print(f"  Response: {json.dumps(result, indent=2)[:200]}...")
                return True, result
            except:
                print(f"  Response: {response.text[:100]}...")
                return True, response.text
        else:
            print(f"  [ERROR] Expected {expected_status}, got {response.status_code}")
            print(f"  Error: {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print(f"[FAIL] {method} {endpoint} - CONNECTION ERROR (Server not running?)")
        return False, None
    except Exception as e:
        print(f"[FAIL] {method} {endpoint} - ERROR: {str(e)}")
        return False, None

def main():
    print("=" * 60)
    print("SERVICE APP API TESTING")
    print("=" * 60)
    
    results = []
    
    # 1. Health Check
    print("\n1. HEALTH CHECK")
    success, _ = test_endpoint("GET", "/health")
    results.append(("Health Check", success))
    
    # 2. Authentication Tests
    print("\n2. AUTHENTICATION TESTS")
    
    # Login
    login_data = {"username": "demo.tech", "password": "password123"}
    success, login_result = test_endpoint("POST", "/api/v1/auth/login", login_data)
    results.append(("Login", success))
    
    # Get token for authenticated requests
    token = None
    if success and login_result:
        token = login_result.get("access_token")
    
    # Signup
    signup_data = {"full_name": "Test Technician"}
    success, _ = test_endpoint("POST", "/api/v1/auth/signup", signup_data)
    results.append(("Signup", success))
    
    # Send OTP
    otp_data = {"contact": "9876543210"}
    success, _ = test_endpoint("POST", "/api/v1/auth/send-otp", otp_data)
    results.append(("Send OTP", success))
    
    # Verify OTP
    verify_data = {"otp": "123456"}
    success, _ = test_endpoint("POST", "/api/v1/auth/verify-otp", verify_data)
    results.append(("Verify OTP", success))
    
    # 3. Dashboard Tests
    print("\n3. DASHBOARD TESTS")
    
    headers = {"Authorization": f"Bearer {token}"} if token else None
    success, _ = test_endpoint("GET", "/api/v1/dashboard/overview", headers=headers)
    results.append(("Dashboard Overview", success))
    
    # 4. Ticket Management Tests
    print("\n4. TICKET MANAGEMENT TESTS")
    
    # Assigned tickets
    success, _ = test_endpoint("GET", "/api/v1/tickets/assigned")
    results.append(("Assigned Tickets", success))
    
    # Completed tickets
    success, _ = test_endpoint("GET", "/api/v1/tickets/completed")
    results.append(("Completed Tickets", success))
    
    # Ticket details
    success, _ = test_endpoint("GET", "/api/v1/tickets/1")
    results.append(("Ticket Details", success))
    
    # Update ticket status
    status_data = {"status": "IN_PROGRESS", "notes": "Started working on the issue"}
    success, _ = test_endpoint("PUT", "/api/v1/tickets/1/status", status_data)
    results.append(("Update Ticket Status", success))
    
    # Capture location
    location_data = {"latitude": 40.7128, "longitude": -74.0060}
    success, _ = test_endpoint("POST", "/api/v1/tickets/1/location", location_data)
    results.append(("Capture Location", success))
    
    # 5. Notifications Tests
    print("\n5. NOTIFICATIONS TESTS")
    
    success, _ = test_endpoint("GET", "/api/v1/notifications/")
    results.append(("Notifications", success))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} - {test_name}")
    
    print(f"\nOVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("SUCCESS: ALL TESTS PASSED - SERVICE APP IS WORKING!")
    else:
        print("WARNING: SOME TESTS FAILED - CHECK SERVER AND DATABASE")

if __name__ == "__main__":
    main()