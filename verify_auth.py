from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
import os

# --- TEST DATABASE SETUP ---
TEST_DB_URL = "sqlite:///./test_auth.db"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create tables in test DB
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_auth_flow():
    print("1. Testing Registration...")
    user_data = {
        "email": "test_unique@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    # Clean up user if exists (for re-runs without deleting file)
    # But since we use a test db file, we can just delete the file at start/end
    
    response = client.post("/api/auth/register", json=user_data)
    if response.status_code == 200:
        print("   [SUCCESS] User registered:", response.json())
    elif response.status_code == 400 and "already registered" in response.text:
         print("   [INFO] User already registered, proceeding to login.")
    else:
        print("   [FAILED] Registration failed:", response.text)
        return

    print("\n2. Testing Login...")
    login_data = {
        "username": "test_unique@example.com",
        "password": "testpassword123"
    }
    response = client.post("/api/auth/login", data=login_data)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        print("   [SUCCESS] Login successful. Token received.")
    else:
        print("   [FAILED] Login failed:", response.text)
        return

    print("\n3. Testing Protected Route (/me)...")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/auth/me", headers=headers)
    if response.status_code == 200:
        print("   [SUCCESS] Protected route accessed. User:", response.json())
    else:
        print("   [FAILED] Protected route access failed:", response.text)

if __name__ == "__main__":
    try:
        test_auth_flow()
    finally:
        # Optional: cleanup
        pass
        # if os.path.exists("./test_auth.db"):
        #     os.remove("./test_auth.db")
