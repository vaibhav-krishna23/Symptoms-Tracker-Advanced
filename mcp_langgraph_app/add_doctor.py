"""Add sample doctor for testing emergency appointments"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app import crud

def add_sample_doctor():
    db = SessionLocal()
    try:
        doctor = crud.create_doctor(
            db,
            full_name="Dr. Sarah Johnson",
            specialization="General Practitioner", 
            clinic_name="City Health Clinic",
            city="New York",  # Change to your city
            contact_email="doctor@example.com"
        )
        print(f"✅ Doctor created: {doctor.doctor_id}")
        print(f"   Name: {doctor.full_name}")
        print(f"   City: {doctor.city}")
        return doctor
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_doctor()