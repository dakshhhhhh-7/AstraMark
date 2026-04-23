#!/usr/bin/env python3
"""
Comprehensive AstraMark System Test
Tests all endpoints, API keys, and integrations
"""
import requests
import json
import time
from typing import Dict, Any, List, Tuple
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8001/api"
FRONTEND_BASE = "http://localhost:3000"

# Test credentials
TEST_EMAIL = "comprehensive_test@astramark.com"
TEST_PASSWORD = "TestPassword123!@#"
TEST_FULL_NAME = "Comprehensive Test User"

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class TestResults:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.errors: List[str] = []
        self.warnings_list: List[str] = []
        
    def add_pass(self, test_name: str):
        self.total += 1
        self.passed += 1
        print(f"{Colors.GREEN}✓{Colors.RESET} {test_name}")
        
    def add_fail(self, test_name: str, error: str):
        self.total += 1
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"{Colors.RED}✗{Colors.RESET} {test_name}")
        print(f"  {Colors.RED}Error: {error}{Colors.RESET}")
        
    def add_warning(self, test_name: str, warning: str):
        self.warnings += 1
        self.warnings_list.append(f"{test_name}: {warning}")
        print(f"{Colors.YELLOW}⚠{Colors.RESET} {test_name}")
        print(f"  {Colors.YELLOW}Warning: {warning}{Colors.RESET}")
        
    def print_summary(self):
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}TEST SUMMARY{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"Total Tests: {self.total}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.RESET}")
        print(f"{Colors.YELLOW}Warnings: {self.warnings}{Colors.RESET}")
        
        if self.total > 0:
            success_rate = (self.passed / self.total) * 100
            print(f"\nSuccess Rate: {success_rate:.1f}%")
            
        if self.errors:
            print(f"\n{Colors.RED}{Colors.BOLD}ERRORS:{Colors.RESET}")
            for error in self.errors:
                print(f"  {Colors.RED}• {error}{Colors.RESET}")
                
        if self.warnings_list:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}WARNINGS:{Colors.RESET}")
            for warning in self.warnings_list:
                print(f"  {Colors.YELLOW}• {warning}{Colors.RESET}")
        
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")

results = TestResults()
access_token = None
refresh_token = None

def print_section(title: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")

def test_health_check():
    """Test system health endpoint"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                results.add_pass("Health Check")
                return True
            else:
                results.add_fail("Health Check", f"Unhealthy status: {data.get('status')}")
                return False
        else:
            results.add_fail("Health Check", f"Status code: {response.status_code}")
            return False
    except Exception as e:
        results.add_fail("Health Check", str(e))
        return False

def test_register():
    """Test user registration"""
    try:
        # Try to register new user
        response = requests.post(
            f"{API_BASE}/auth/register",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "full_name": TEST_FULL_NAME
            },
            timeout=10
        )
        
        # Accept both 200 and 201 status codes
        if response.status_code in [200, 201]:
            results.add_pass("User Registration (New User)")
            return True
        elif response.status_code == 400:
            data = response.json()
            if "already registered" in data.get('detail', '').lower():
                results.add_warning("User Registration", "User already exists (expected)")
                return True
            else:
                results.add_fail("User Registration", data.get('detail', 'Unknown error'))
                return False
        else:
            results.add_fail("User Registration", f"Status code: {response.status_code}")
            return False
    except Exception as e:
        results.add_fail("User Registration", str(e))
        return False

def test_login():
    """Test user login"""
    global access_token, refresh_token
    try:
        response = requests.post(
            f"{API_BASE}/auth/token",
            data={
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('access_token'):
                access_token = data['access_token']
                refresh_token = data.get('refresh_token')
                results.add_pass("User Login")
                return True
            else:
                results.add_fail("User Login", "No access token in response")
                return False
        else:
            results.add_fail("User Login", f"Status code: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        results.add_fail("User Login", str(e))
        return False

def test_get_user():
    """Test get current user"""
    if not access_token:
        results.add_fail("Get Current User", "No access token available")
        return False
        
    try:
        response = requests.get(
            f"{API_BASE}/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('email') == TEST_EMAIL:
                if data.get('full_name'):
                    results.add_pass("Get Current User (with full_name)")
                else:
                    results.add_warning("Get Current User", "full_name field missing")
                return True
            else:
                results.add_fail("Get Current User", "Email mismatch")
                return False
        else:
            results.add_fail("Get Current User", f"Status code: {response.status_code}")
            return False
    except Exception as e:
        results.add_fail("Get Current User", str(e))
        return False

def test_refresh_token():
    """Test token refresh"""
    if not refresh_token:
        results.add_warning("Token Refresh", "No refresh token available")
        return False
        
    try:
        response = requests.post(
            f"{API_BASE}/auth/refresh",
            json={"refresh_token": refresh_token},  # Send as JSON body, not Bearer token
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('access_token'):
                results.add_pass("Token Refresh")
                return True
            else:
                results.add_fail("Token Refresh", "No access token in response")
                return False
        else:
            results.add_fail("Token Refresh", f"Status code: {response.status_code}, Response: {response.text[:200]}")
            return False
    except Exception as e:
        results.add_fail("Token Refresh", str(e))
        return False

def test_ai_chat():
    """Test AI chat endpoint"""
    if not access_token:
        results.add_fail("AI Chat", "No access token available")
        return False
        
    try:
        response = requests.post(
            f"{API_BASE}/ai/chat",
            json={
                "message": "What are the best marketing strategies for a SaaS startup?",
                "history": [],
                "budget": 5000,
                "currency": "USD"
            },
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('response'):
                results.add_pass("AI Chat")
                return True
            else:
                results.add_fail("AI Chat", "No response in data")
                return False
        else:
            results.add_fail("AI Chat", f"Status code: {response.status_code}, Response: {response.text[:200]}")
            return False
    except Exception as e:
        results.add_fail("AI Chat", str(e))
        return False

def test_business_analysis():
    """Test business analysis endpoint"""
    if not access_token:
        results.add_fail("Business Analysis", "No access token available")
        return False
        
    try:
        response = requests.post(
            f"{API_BASE}/analyze",
            json={
                "business_type": "SaaS Marketing Platform",
                "target_market": "Small businesses and startups",
                "monthly_budget": "5000",  # String, not number
                "primary_goal": "Generate leads and increase brand awareness through digital marketing",
                "additional_info": "Focus on content marketing and SEO"
            },
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('overview'):
                # Check AI service used
                ai_service = data.get('ai_service_used', 'unknown')
                if ai_service == 'groq':
                    results.add_pass(f"Business Analysis (Groq AI)")
                elif ai_service == 'gemini':
                    results.add_pass(f"Business Analysis (Gemini AI)")
                elif ai_service == 'fallback':
                    results.add_warning("Business Analysis", "Using fallback mock data (AI services unavailable)")
                else:
                    results.add_pass(f"Business Analysis ({ai_service})")
                return True
            else:
                results.add_fail("Business Analysis", "No overview in response")
                return False
        else:
            results.add_fail("Business Analysis", f"Status code: {response.status_code}, Response: {response.text[:200]}")
            return False
    except Exception as e:
        results.add_fail("Business Analysis", str(e))
        return False

def test_razorpay_create_order():
    """Test Razorpay order creation"""
    if not access_token:
        results.add_fail("Razorpay Create Order", "No access token available")
        return False
        
    try:
        response = requests.post(
            f"{API_BASE}/payments/razorpay/create-order",
            json={
                "plan_id": "pro"  # Valid plan IDs: starter, pro, growth
            },
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('order'):
                order = data['order']
                if order.get('order_id'):
                    results.add_pass("Razorpay Create Order")
                    return True
                else:
                    results.add_fail("Razorpay Create Order", "No order_id in response")
                    return False
            else:
                results.add_fail("Razorpay Create Order", "Invalid response structure")
                return False
        else:
            results.add_fail("Razorpay Create Order", f"Status code: {response.status_code}, Response: {response.text[:200]}")
            return False
    except Exception as e:
        results.add_fail("Razorpay Create Order", str(e))
        return False

def test_frontend_accessibility():
    """Test if frontend is accessible"""
    try:
        response = requests.get(FRONTEND_BASE, timeout=5)
        if response.status_code == 200:
            results.add_pass("Frontend Accessibility")
            return True
        else:
            results.add_fail("Frontend Accessibility", f"Status code: {response.status_code}")
            return False
    except Exception as e:
        results.add_fail("Frontend Accessibility", str(e))
        return False

def test_cors():
    """Test CORS configuration"""
    try:
        response = requests.options(
            f"{API_BASE}/auth/me",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            },
            timeout=5
        )
        
        if response.status_code == 200:
            cors_header = response.headers.get('Access-Control-Allow-Origin')
            if cors_header:
                results.add_pass("CORS Configuration")
                return True
            else:
                results.add_fail("CORS Configuration", "No CORS headers in response")
                return False
        else:
            results.add_fail("CORS Configuration", f"Status code: {response.status_code}")
            return False
    except Exception as e:
        results.add_fail("CORS Configuration", str(e))
        return False

def main():
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     ASTRAMARK COMPREHENSIVE SYSTEM TEST                    ║")
    print("║     Testing all endpoints, APIs, and integrations          ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # System Tests
    print_section("1. SYSTEM HEALTH TESTS")
    test_health_check()
    test_frontend_accessibility()
    test_cors()
    
    # Authentication Tests
    print_section("2. AUTHENTICATION TESTS")
    test_register()
    test_login()
    test_get_user()
    test_refresh_token()
    
    # AI Service Tests
    print_section("3. AI SERVICE TESTS")
    test_ai_chat()
    test_business_analysis()
    
    # Payment Tests
    print_section("4. PAYMENT INTEGRATION TESTS")
    test_razorpay_create_order()
    
    # Print Summary
    results.print_summary()
    
    # Exit code based on results
    if results.failed > 0:
        print(f"{Colors.RED}❌ Tests failed! Please review errors above.{Colors.RESET}\n")
        return 1
    elif results.warnings > 0:
        print(f"{Colors.YELLOW}⚠️  Tests passed with warnings. Review warnings above.{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.GREEN}✅ All tests passed successfully!{Colors.RESET}\n")
        return 0

if __name__ == "__main__":
    exit(main())
