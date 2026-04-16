from app import SessionLocal, engine, Base, User, Crop, mock_ai_grading
from werkzeug.security import generate_password_hash
import datetime
from datetime import timedelta

def seed_database():
    # Clear and recreate tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Create Users
        farmer = User(username='farmer', password=generate_password_hash('password'), role='farmer')
        bidder = User(username='bidder', password=generate_password_hash('password'), role='bidder')
        
        db.add(farmer)
        db.add(bidder)
        db.commit()
        db.refresh(farmer)
        db.refresh(bidder)

        # Create Crops
        crops_data = [
            {'name': 'Wheat', 'qty': '1000kg', 'price': 500, 'desc': 'Premium quality wheat, harvested yesterday.'},
            {'name': 'Rice', 'qty': '500kg', 'price': 800, 'desc': 'Basmati rice, long grain.'},
            {'name': 'Corn', 'qty': '2000kg', 'price': 300, 'desc': 'Sweet corn, organic.'}
        ]

        for c in crops_data:
            grade = mock_ai_grading(c['name'], c['desc'])
            # Set end time to 10 minutes from now
            end_time = datetime.datetime.now() + timedelta(minutes=10)
            
            crop = Crop(
                farmer_id=farmer.id,
                name=c['name'],
                quantity=c['qty'],
                base_price=c['price'],
                description=c['desc'],
                ai_grade=grade,
                end_time=end_time
            )
            db.add(crop)
        
        db.commit()
        print("Database seeded successfully!")
        print("Credentials:")
        print("Farmer: username='farmer', password='password'")
        print("Bidder: username='bidder', password='password'")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
