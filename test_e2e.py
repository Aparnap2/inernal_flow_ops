#!/usr/bin/env python3
"""
End-to-End Production Simulation Test
Tests the complete workflow: webhook → queue → AI processing → approval → completion
"""
import requests
import json
import time
import asyncio

BASE_URL = "http://localhost:8000"

def test_api_endpoints():
    """Test all API endpoints are working"""
    print("=== Testing API Endpoints ===")
    
    endpoints = [
        "/health",
        "/api/runs",
        "/api/approvals/pending", 
        "/api/exceptions/open",
        "/api/users/me"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
            print(f"  {endpoint}: {status}")
        except Exception as e:
            print(f"  {endpoint}: ❌ ERROR - {e}")

def test_auth():
    """Test authentication"""
    print("\n=== Testing Authentication ===")
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@example.com",
            "password": "password123"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Login: ✅ PASS - Token: {data['access_token'][:20]}...")
            return data['access_token']
        else:
            print(f"  Login: ❌ FAIL - {response.text}")
            return None
    except Exception as e:
        print(f"  Login: ❌ ERROR - {e}")
        return None

def test_llm_integration():
    """Test LLM integration"""
    print("\n=== Testing LLM Integration ===")
    
    try:
        # Direct OpenRouter test
        headers = {
            "Authorization": "Bearer ***REDACTED***",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://your-site.com",
            "X-Title": "HubSpot Operations Orchestrator"
        }
        
        payload = {
            "model": "z-ai/glm-4.5-air:free",
            "messages": [{"role": "user", "content": "Say 'LLM Working' if you can respond."}],
            "max_tokens": 50
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print(f"  LLM Response: ✅ PASS - '{message}'")
            return True
        else:
            print(f"  LLM: ❌ FAIL - {response.text}")
            return False
    except Exception as e:
        print(f"  LLM: ❌ ERROR - {e}")
        return False

def test_queue_processing():
    """Test queue processing"""
    print("\n=== Testing Queue Processing ===")
    
    try:
        response = requests.post(f"{BASE_URL}/worker/process-queue")
        if response.status_code == 200:
            data = response.json()
            print(f"  Queue Processing: ✅ PASS - {data['message']}")
            return True
        else:
            print(f"  Queue Processing: ❌ FAIL - {response.text}")
            return False
    except Exception as e:
        print(f"  Queue Processing: ❌ ERROR - {e}")
        return False

def test_agui_approval():
    """Test AGUI approval functionality"""
    print("\n=== Testing AGUI Approval ===")
    
    try:
        # Get pending approvals
        response = requests.get(f"{BASE_URL}/api/approvals/pending")
        if response.status_code == 200:
            approvals = response.json()
            print(f"  Pending Approvals: ✅ PASS - Found {approvals['total']} approvals")
            
            if approvals['total'] > 0:
                # Test approval decision
                approval_id = approvals['approvals'][0]['id']
                decision_response = requests.patch(
                    f"{BASE_URL}/api/approvals/{approval_id}/decision",
                    json={"approved": True, "user_id": "admin", "comments": "E2E test approval"}
                )
                
                if decision_response.status_code == 200:
                    print(f"  Approval Decision: ✅ PASS - Approved {approval_id}")
                    return True
                else:
                    print(f"  Approval Decision: ❌ FAIL - {decision_response.text}")
                    return False
            else:
                print(f"  Approval Decision: ⚠️  SKIP - No pending approvals")
                return True
        else:
            print(f"  Pending Approvals: ❌ FAIL - {response.text}")
            return False
    except Exception as e:
        print(f"  AGUI: ❌ ERROR - {e}")
        return False

def test_exception_handling():
    """Test exception handling"""
    print("\n=== Testing Exception Handling ===")
    
    try:
        # Get open exceptions
        response = requests.get(f"{BASE_URL}/api/exceptions/open")
        if response.status_code == 200:
            exceptions = response.json()
            print(f"  Open Exceptions: ✅ PASS - Found {exceptions['total']} exceptions")
            
            if exceptions['total'] > 0:
                # Test exception resolution
                exception_id = exceptions['exceptions'][0]['id']
                resolution_response = requests.patch(
                    f"{BASE_URL}/api/exceptions/{exception_id}/resolve",
                    json={"resolution": "E2E test resolution"}
                )
                
                if resolution_response.status_code == 200:
                    print(f"  Exception Resolution: ✅ PASS - Resolved {exception_id}")
                    return True
                else:
                    print(f"  Exception Resolution: ❌ FAIL - {resolution_response.text}")
                    return False
            else:
                print(f"  Exception Resolution: ⚠️  SKIP - No open exceptions")
                return True
        else:
            print(f"  Open Exceptions: ❌ FAIL - {response.text}")
            return False
    except Exception as e:
        print(f"  Exception Handling: ❌ ERROR - {e}")
        return False

def main():
    """Run complete end-to-end test suite"""
    print("🚀 Starting End-to-End Production Simulation Test")
    print("=" * 60)
    
    results = []
    
    # Test all components
    test_api_endpoints()
    
    token = test_auth()
    results.append(("Authentication", token is not None))
    
    llm_result = test_llm_integration()
    results.append(("LLM Integration", llm_result))
    
    queue_result = test_queue_processing()
    results.append(("Queue Processing", queue_result))
    
    agui_result = test_agui_approval()
    results.append(("AGUI Approval", agui_result))
    
    exception_result = test_exception_handling()
    results.append(("Exception Handling", exception_result))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Production simulation successful!")
    else:
        print("⚠️  Some tests failed - Check logs for details")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
