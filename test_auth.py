"""
Quick test script to verify authentication endpoints work correctly.
This will test both registration and login flows.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_registration():
    """Test user registration"""
    print("\n=== Testing Registration ===")
    url = f"{BASE_URL}/api/auth/register"
    data = {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("[SUCCESS] Registration successful!")
            return True
        elif response.status_code == 400 and "already registered" in response.text:
            print("[INFO] User already exists (expected if running multiple times)")
            return True
        else:
            print("[FAILED] Registration failed")
            return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def test_login():
    """Test user login"""
    print("\n=== Testing Login ===")
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "username": "test@example.com",  # OAuth2 uses 'username' field
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(url, data=data)  # OAuth2 expects form data
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            if "access_token" in response_data:
                print("[SUCCESS] Login successful! Token received.")
                return response_data["access_token"]
            else:
                print("[FAILED] Login response missing access_token")
                return None
        else:
            print("[FAILED] Login failed")
            return None
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return None

def test_protected_endpoint(token):
    """Test accessing a protected endpoint"""
    print("\n=== Testing Protected Endpoint (/api/auth/me) ===")
    url = f"{BASE_URL}/api/auth/me"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("[SUCCESS] Protected endpoint access successful!")
            return True
        else:
            print("[FAILED] Protected endpoint access failed")
            return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

if __name__ == "__main__":
    print("Starting Authentication Tests...")
    print(f"Server: {BASE_URL}")
    
    # Test registration
    test_registration()
    
    # Test login
    token = test_login()
    
    # Test protected endpoint if login was successful
    if token:
        test_protected_endpoint(token)
    
    print("\n=== Tests Complete ===")
