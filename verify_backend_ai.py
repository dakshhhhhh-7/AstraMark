import requests
import json
import time

def test_backend():
    print("Testing Backend AI Integration...")
    url = "http://localhost:8000/api/analyze"
    payload = {
        "business_type": "Test Coffee Shop",
        "target_market": "Local Residents",
        "monthly_budget": "$1000",
        "primary_goal": "Brand Awareness",
        "additional_info": "Test run"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Response received.")
            print(f"Verdict: {data.get('ai_verdict')}")
            # print(json.dumps(data, indent=2))
        else:
            print("❌ Failed.")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_backend()
