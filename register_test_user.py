"""Register test user"""
import requests

BACKEND = "http://localhost:8001"

# Register user
response = requests.post(
    f"{BACKEND}/api/auth/register",
    json={
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User"
    }
)

if response.status_code == 200:
    print("✅ User registered successfully!")
elif "already exists" in response.text:
    print("ℹ️  User already exists, that's fine!")
else:
    print(f"❌ Registration failed: {response.status_code}")
    print(f"Response: {response.text}")
