from app import app, db, User
from werkzeug.security import generate_password_hash, check_password_hash

def test_auth_fix():
    with app.app_context():
        # Test hash generation
        try:
            pw_hash = generate_password_hash('testpassword')
            print(f"Hash generated successfully: {pw_hash[:20]}...")
            
            assert check_password_hash(pw_hash, 'testpassword')
            print("Hash verification successful.")
            
        except Exception as e:
            print(f"Error during hash generation/verification: {e}")

if __name__ == "__main__":
    test_auth_fix()
