
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_endpoints():
    print("Testing Backend Endpoints...")
    
    # 1. Health Check
    try:
        resp = requests.get(f"{BASE_URL}/health")
        print(f"Health Check: {resp.status_code}")
        print(json.dumps(resp.json(), indent=2))
    except Exception as e:
        print(f"Health Check Failed: {e}")
        return

    # 2. Analyze (Mock/Quick for testing)
    print("\nTesting Analysis...")
    payload = {
        "business_type": "Coffee Shop",
        "target_market": "Local Residents",
        "monthly_budget": "$1000",
        "primary_goal": "Increase foot traffic"
    }
    analysis_id = None
    try:
        resp = requests.post(f"{BASE_URL}/analyze", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            analysis_id = data.get("id")
            print(f"Analysis Successful. ID: {analysis_id}")
            print(f"Verdict: {data.get('ai_verdict')}")
        else:
            print(f"Analysis Failed: {resp.text}")
    except Exception as e:
        print(f"Analysis Request Failed: {e}")

    if not analysis_id:
        print("Skipping dependent tests due to analysis failure")
        return

    # 3. Generate Pitch Deck
    print(f"\nTesting Pitch Deck Generation for {analysis_id}...")
    try:
        resp = requests.post(f"{BASE_URL}/generate/pitch-deck?analysis_id={analysis_id}")
        if resp.status_code == 200:
            print("Pitch Deck Generated Successfully")
            print(f"Slides: {resp.json().get('total_slides')}")
        else:
            print(f"Pitch Deck Failed: {resp.text}")
    except Exception as e:
        print(f"Pitch Deck Request Failed: {e}")

    # 4. Generate Content Calendar
    print(f"\nTesting Content Calendar for {analysis_id}...")
    try:
        resp = requests.post(f"{BASE_URL}/generate/content-calendar?analysis_id={analysis_id}&weeks=2")
        if resp.status_code == 200:
            print("Calendar Generated Successfully")
            print(f"Total Posts: {resp.json().get('total_posts')}")
        else:
            print(f"Calendar Failed: {resp.text}")
    except Exception as e:
        print(f"Calendar Request Failed: {e}")

if __name__ == "__main__":
    test_endpoints()
