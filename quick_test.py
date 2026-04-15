"""
Quick test to verify token validation fix
"""
import requests
import json

BACKEND = "http://localhost:8001"

def test_auth_flow():
    print("🧪 Testing Authentication Flow...")
    print("=" * 50)
    
    # 1. Register/Login
    print("\n1️⃣ Testing Login...")
    login_data = {
        "username": "test@example.com",
        "password": "password123"  # Try the simpler password
    }
    
    response = requests.post(
        f"{BACKEND}/api/auth/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        print(f"   ✅ Login successful!")
        print(f"   Access token: {access_token[:30]}...")
        print(f"   Refresh token: {refresh_token[:30]}...")
    else:
        print(f"   ❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    # 2. Test /auth/me endpoint
    print("\n2️⃣ Testing /auth/me endpoint...")
    response = requests.get(
        f"{BACKEND}/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"   ✅ /auth/me successful!")
        print(f"   User: {user_data.get('email')}")
    else:
        print(f"   ❌ /auth/me failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    # 3. Test token refresh
    print("\n3️⃣ Testing Token Refresh...")
    response = requests.post(
        f"{BACKEND}/api/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    if response.status_code == 200:
        new_tokens = response.json()
        new_access_token = new_tokens["access_token"]
        print(f"   ✅ Token refresh successful!")
        print(f"   New access token: {new_access_token[:30]}...")
    else:
        print(f"   ❌ Token refresh failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    # 4. Test /auth/me with refreshed token
    print("\n4️⃣ Testing /auth/me with refreshed token...")
    response = requests.get(
        f"{BACKEND}/api/auth/me",
        headers={"Authorization": f"Bearer {new_access_token}"}
    )
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"   ✅ /auth/me with refreshed token successful!")
        print(f"   User: {user_data.get('email')}")
    else:
        print(f"   ❌ /auth/me with refreshed token failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    # 5. Test Razorpay order creation
    print("\n5️⃣ Testing Razorpay Order Creation...")
    response = requests.post(
        f"{BACKEND}/api/payments/razorpay/create-order",
        json={"plan_id": "pro"},
        headers={"Authorization": f"Bearer {new_access_token}"}
    )
    
    if response.status_code == 200:
        order_data = response.json()
        print(f"   ✅ Razorpay order creation successful!")
        print(f"   Order: {json.dumps(order_data, indent=2)}")
    else:
        print(f"   ❌ Razorpay order creation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        # This might fail due to Razorpay config, but auth should work
        if response.status_code == 503:
            print(f"   ℹ️  Payment service unavailable (expected if Razorpay not configured)")
            print(f"   ✅ But authentication worked correctly!")
        else:
            return False
    
    print("\n" + "=" * 50)
    print("🎉 ALL AUTHENTICATION TESTS PASSED!")
    print("✨ Token validation fix is working correctly!")
    return True

if __name__ == "__main__":
    try:
        success = test_auth_flow()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
