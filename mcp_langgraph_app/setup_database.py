"""Database setup script - Create tables and add sample data"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db.session import SessionLocal, engine, Base
from app.db import models
from app import crud


def create_tables():
    """Create all database tables."""
    print("📊 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")


def add_sample_doctors():
    """Add sample doctors to database."""
    print("\n👨⚕️ Adding sample doctors...")
    
    db = SessionLocal()
    
    doctors_data = [
        {
            "full_name": "Dr. Sarah Johnson",
            "specialization": "General Practitioner",
            "clinic_name": "City Health Clinic",
            "city": "New York",
            "contact_email": "sarah.johnson@cityhealthclinic.com"
        },
        {
            "full_name": "Dr. Michael Chen",
            "specialization": "Cardiologist",
            "clinic_name": "Heart Care Center",
            "city": "New York",
            "contact_email": "michael.chen@heartcarecenter.com"
        },
        {
            "full_name": "Dr. Emily Rodriguez",
            "specialization": "General Practitioner",
            "clinic_name": "Community Medical Center",
            "city": "Los Angeles",
            "contact_email": "emily.rodriguez@communitymed.com"
        },
        {
            "full_name": "Dr. James Wilson",
            "specialization": "Emergency Medicine",
            "clinic_name": "Emergency Care Hospital",
            "city": "Chicago",
            "contact_email": "james.wilson@emergencycare.com"
        },
        {
            "full_name": "Dr. Lisa Anderson",
            "specialization": "General Practitioner",
            "clinic_name": "Family Health Practice",
            "city": "Houston",
            "contact_email": "lisa.anderson@familyhealth.com"
        }
    ]
    
    created_count = 0
    for doctor_data in doctors_data:
        # Check if doctor already exists
        existing = db.query(models.Doctor).filter(
            models.Doctor.contact_email == doctor_data["contact_email"]
        ).first()
        
        if not existing:
            doctor = crud.create_doctor(db, **doctor_data)
            print(f"   ✅ Created: Dr. {doctor_data['full_name']} ({doctor_data['city']})")
            created_count += 1
        else:
            print(f"   ⏭️  Skipped: Dr. {doctor_data['full_name']} (already exists)")
    
    db.close()
    print(f"\n✅ Added {created_count} new doctors!")


def verify_setup():
    """Verify database setup."""
    print("\n🔍 Verifying database setup...")
    
    db = SessionLocal()
    
    # Count doctors
    doctor_count = db.query(models.Doctor).count()
    print(f"   Doctors in database: {doctor_count}")
    
    # Count patients
    patient_count = db.query(models.Patient).count()
    print(f"   Patients in database: {patient_count}")
    
    # Count sessions
    session_count = db.query(models.Session).count()
    print(f"   Sessions in database: {session_count}")
    
    db.close()
    
    if doctor_count > 0:
        print("\n✅ Database setup verified!")
    else:
        print("\n⚠️  Warning: No doctors in database. Emergency appointments won't work.")


def main():
    """Main setup function."""
    print("=" * 60)
    print("Database Setup Script")
    print("=" * 60)
    print("\nThis script will:")
    print("1. Create all database tables")
    print("2. Add sample doctors")
    print("3. Verify setup")
    print("\n" + "=" * 60 + "\n")
    
    try:
        # Create tables
        create_tables()
        
        # Add sample doctors
        add_sample_doctors()
        
        # Verify
        verify_setup()
        
        print("\n" + "=" * 60)
        print("✅ Database setup completed successfully!")
        print("=" * 60)
        print("\n📝 Next steps:")
        print("   1. Register a patient account")
        print("   2. Start MCP server: python run_mcp_server.py")
        print("   3. Start API: uvicorn api.main:app --reload")
        print("   4. Start UI: streamlit run streamlit_app/app_v2.py")
        print()
        
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
