import requests
import sys

def check_url(url, expected_text=None):
    try:
        response = requests.get(url)
        print(f"Checking {url}...")
        if response.status_code == 200:
            print(f"  [PASS] Status 200 OK")
            if expected_text:
                if expected_text in response.text:
                    print(f"  [PASS] Found expected text: '{expected_text}'")
                else:
                    print(f"  [FAIL] Expected text '{expected_text}' not found!")
                    return False
            return True
        else:
            print(f"  [FAIL] Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"  [FAIL] Exception: {e}")
        return False

def main():
    base_url = "http://127.0.0.1:8000"
    
    # Check main pages to ensure no regression
    check_url(f"{base_url}/", "AgriShield")
    check_url(f"{base_url}/login", "Login")
    check_url(f"{base_url}/signup", "Create Account")
    check_url(f"{base_url}/market", "Market")
    
    # Check that bidding is GONE (should be 404 or redirect, likely 404 since route removed)
    print(f"Checking {base_url}/bidding (Should be 404)...")
    resp = requests.get(f"{base_url}/bidding")
    if resp.status_code == 404:
         print(f"  [PASS] Status 404 Not Found (Correct)")
    else:
         print(f"  [FAIL] Status {resp.status_code} (Expected 404)")

    print(f"Checking {base_url}/login/farmer (Should be 404)...")
    resp = requests.get(f"{base_url}/login/farmer")
    if resp.status_code == 404:
         print(f"  [PASS] Status 404 Not Found (Correct)")
    else:
         print(f"  [FAIL] Status {resp.status_code} (Expected 404)")

if __name__ == "__main__":
    main()
