
import requests
import json

url = "http://127.0.0.1:8000/api/analyze"
headers = {"Content-Type": "application/json"}
data = {
    "business_type": "Digital Marketing Agency",
    "target_market": "Small Businesses",
    "monthly_budget": "$2000",
    "primary_goal": "Get more leads",
    "additional_info": "Focus on SEO"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success!")
        print(json.dumps(response.json(), indent=2)[:500]) # First 500 chars
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
