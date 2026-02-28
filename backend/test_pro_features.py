
import requests
import json
import time
import os
import sys

# Force UTF-8 for stdout/stderr
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8001/api"
TEST_USER_EMAIL = "test_pro_user@example.com"
TEST_USER_PASS = "securepassword123"

def get_auth_token():
    print("\n--- Authenticating ---")
    # 1. Register (ignore if exists)
    try:
        requests.post(f"{BASE_URL}/auth/register", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASS,
            "full_name": "Pro Tester"
        })
    except:
        pass # Ignore errors, user might exist

    # 2. Login
    try:
        resp = requests.post(f"{BASE_URL}/auth/token", data={
            "username": TEST_USER_EMAIL,
            "password": TEST_USER_PASS
        })
        if resp.status_code == 200:
            token = resp.json()["access_token"]
            print(f"[PASS] Authenticated as {TEST_USER_EMAIL}")
            return token
        else:
            print(f"[FAIL] Login failed: {resp.text}")
            return None
    except Exception as e:
        print(f"[FAIL] Auth Request Error: {e}")
        return None

def test_pro_features():
    print(f"Testing AstraMark Pro Features against {BASE_URL}...")
    
    # 1. Health Check
    try:
        print("\n--- 1. Checking Health ---")
        resp = requests.get(f"{BASE_URL}/health")
        if resp.status_code == 200:
            print("[PASS] Server is Healthy")
            # print(json.dumps(resp.json(), indent=2))
        else:
            print(f"[FAIL] Health Check Failed: {resp.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("[FAIL] Could not connect to server. Is it running on port 8001?")
        return
    except Exception as e:
        print(f"[FAIL] Health Check Error: {e}")
        return

    # Authenticate
    token = get_auth_token()
    if not token:
        print("[FAIL] Cannot proceed without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Analyze (Prerequisite for other features)
    print("\n--- 2. Generating Baseline Analysis (Prerequisite) ---")
    payload = {
        "business_type": "SaaS AI Automation",
        "target_market": "Marketing Agencies",
        "monthly_budget": "$5000",
        "primary_goal": "Scale Recurring Revenue",
        "country": "US"
    }
    analysis_id = None
    try:
        resp = requests.post(f"{BASE_URL}/analyze?premium=true", json=payload, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            analysis_id = data.get("id") or data.get("_id")
            
            if not analysis_id and 'business_id' in data:
                 print(f"Got Business ID: {data['business_id']}")
            
            if not analysis_id:
                 print("ID not in response, fetching recent analyses...")
                 recent = requests.get(f"{BASE_URL}/analyses?limit=1").json()
                 if recent:
                     analysis_id = recent[0].get('id')
                     print(f"Retrieved Analysis ID from history: {analysis_id}")

            print(f"[PASS] Analysis Successful. Using ID: {analysis_id}")
        else:
            print(f"[FAIL] Analysis Failed: {resp.text}")
            return
    except Exception as e:
        print(f"[FAIL] Analysis Request Error: {e}")
        return

    if not analysis_id:
        print("[FAIL] Cannot proceed without Analysis ID")
        return

    # 3. Test Pitch Deck
    print(f"\n--- 3. Testing Pitch Deck Generation (Growth Feature) ---")
    try:
        resp = requests.post(f"{BASE_URL}/generate/pitch-deck?analysis_id={analysis_id}")
        if resp.status_code == 200:
            data = resp.json()
            # print("DEBUG:",json.dumps(data, indent=2))
            # Structure: {'pitch_deck': {'slides': [...]}, 'total_slides': N, ...}
            slides = data.get('pitch_deck', {}).get('slides', [])
            total = data.get('total_slides', len(slides))
            source = data.get('data_source', 'real (assumed)')
            print(f"[PASS] Pitch Deck Generated: {total} slides [{source}]")
            if slides:
                print(f"   First Slide: {slides[0].get('title', 'Unknown')}")
        else:
            print(f"[FAIL] Pitch Deck Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"[FAIL] Pitch Deck Error: {e}")

    # 4. Test Content Calendar
    print(f"\n--- 4. Testing Content Calendar (Growth Feature) ---")
    try:
        resp = requests.post(f"{BASE_URL}/generate/content-calendar?analysis_id={analysis_id}&weeks=2")
        if resp.status_code == 200:
            data = resp.json()
            # Structure: {'content_calendar': {'weeks': [...]}, 'total_posts': N}
            calendar = data.get('content_calendar', {})
            weeks = calendar.get('weeks', [])
            total_posts = data.get('total_posts', 0)
            source = data.get('data_source', 'real (assumed)')
            print(f"[PASS] Calendar Generated: {len(weeks)} weeks, {total_posts} total posts [{source}]")
        else:
            print(f"[FAIL] Calendar Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"[FAIL] Calendar Error: {e}")

    # 5. Test Email Sequence
    print(f"\n--- 5. Testing Email Sequence (Growth Feature) ---")
    try:
        resp = requests.post(f"{BASE_URL}/generate/email-sequence?analysis_id={analysis_id}&sequence_type=cold_outreach")
        if resp.status_code == 200:
            data = resp.json()
            # Structure: {'email_sequence': {'emails': [...]}, 'total_emails': N}
            emails = data.get('email_sequence', {}).get('emails', [])
            total_emails = data.get('total_emails', len(emails))
            source = data.get('data_source', 'real (assumed)')
            print(f"[PASS] Email Sequence Generated: {total_emails} emails [{source}]")
        else:
            print(f"[FAIL] Email Sequence Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"[FAIL] Email Sequence Error: {e}")

    # 6. Test PDF Export
    print(f"\n--- 6. Testing PDF Export (Growth Feature) ---")
    try:
        resp = requests.get(f"{BASE_URL}/export/pdf/{analysis_id}")
        if resp.status_code == 200:
            content_size = len(resp.content)
            print(f"[PASS] PDF Export Successful: {content_size} bytes downloaded")
            if resp.headers.get('content-type') == 'application/pdf':
                print("   Header verified: application/pdf")
        else:
            print(f"[FAIL] PDF Export Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"[FAIL] PDF Export Error: {e}")

    # 7. Test Market Intelligence
    print(f"\n--- 7. Testing Market Signals (Pro Feature) ---")
    try:
        resp = requests.get(f"{BASE_URL}/market/signals?business_type=SaaS")
        if resp.status_code == 200:
            data = resp.json()
            signals = data.get('signals', [])
            print(f"[PASS] Market Signals Retrieved: {len(signals)} signals found")
        else:
            print(f"[FAIL] Market Signals Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"[FAIL] Market Signals Error: {e}")

if __name__ == "__main__":
    test_pro_features()
