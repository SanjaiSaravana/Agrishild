from app import app, db, User

def test_user_registration():
    with app.app_context():
        # Clear existing users for consistent testing
        User.query.delete()
        db.session.commit()

        # Create test users
        try:
            from werkzeug.security import generate_password_hash
            farmer = User(username='test_farmer', password=generate_password_hash('password'), role='farmer')
            bidder = User(username='test_bidder', password=generate_password_hash('password'), role='bidder')

            db.session.add(farmer)
            db.session.add(bidder)
            db.session.commit()
            print("Successfully added test users to the database.")
        except Exception as e:
            print(f"Failed to add users: {e}")

        # Verify users exist
        users = User.query.all()
        print(f"Users in database: {[u.username for u in users]}")

if __name__ == "__main__":
    test_user_registration()
