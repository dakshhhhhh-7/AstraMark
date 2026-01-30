import requests

BASE_URL = "http://localhost:8001/api"

def test_auth_flow():
    # 1. Register
    email = "testuser@example.com"
    password = "password123"
    print(f"Registering user: {email}")
    
    try:
        reg_resp = requests.post(f"{BASE_URL}/auth/register", json={
            "email": email,
            "password": password,
            "full_name": "Test User"
        })
        if reg_resp.status_code == 200:
            print("Registration success:", reg_resp.json())
        elif reg_resp.status_code == 400 and "already registered" in reg_resp.text:
            print("User already registered, proceeding to login.")
        else:
            print("Registration failed:", reg_resp.text)
            return

        # 2. Login
        print("Logging in...")
        login_resp = requests.post(f"{BASE_URL}/auth/token", data={
            "username": email,
            "password": password
        })
        
        if login_resp.status_code != 200:
            print("Login failed:", login_resp.text)
            return
            
        token = login_resp.json()["access_token"]
        print("Login success. Token received.")
        
        # 3. Access Protected Endpoint
        print("Testing protected endpoint (Me)...")
        headers = {"Authorization": f"Bearer {token}"}
        me_resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        
        if me_resp.status_code == 200:
            print("Protected endpoint success:", me_resp.json())
        else:
            print("Protected endpoint failed:", me_resp.text)

        # 4. Test Analyze Endpoint (Protected)
        print("Testing Analyze endpoint...")
        analyze_resp = requests.post(f"{BASE_URL}/analyze", headers=headers, json={
            "business_type": "Bakery",
            "target_market": "Local families",
            "monthly_budget": "$500",
            "primary_goal": "Increase foot traffic"
        })
        
        if analyze_resp.status_code == 200:
            print("Analyze endpoint success!")
            print("Analysis ID:", analyze_resp.json().get("id"))
        else:
             print("Analyze endpoint failed:", analyze_resp.text)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_auth_flow()
