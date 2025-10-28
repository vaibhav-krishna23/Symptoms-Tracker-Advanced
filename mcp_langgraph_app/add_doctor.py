"""Add sample doctor and test email functionality"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app import crud
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from mcp_langgraph_app.config.settings import settings

def test_email_detailed():
    """Test email with detailed appointment format"""
    print("📧 Testing appointment email format...")
    
    try:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        
        # Patient Email
        patient_msg = MIMEMultipart("alternative")
        patient_msg["Subject"] = "🏥 Emergency Appointment Confirmation - TEST"
        patient_msg["From"] = settings.SMTP_USER
        patient_msg["To"] = settings.SMTP_USER
        patient_msg.attach(MIMEText(
            "<html><body><h2>🏥 Appointment Confirmed</h2>"
            "<p>Dear <strong>Test Patient</strong>,</p>"
            "<p><strong>Doctor:</strong> Dr. Test Doctor</p>"
            "<p><strong>Clinic:</strong> Test Clinic</p>"
            "<p><strong>Date:</strong> Tomorrow 10:00 AM</p>"
            "<p><strong>Symptoms:</strong> Test emergency symptoms</p>"
            "</body></html>", "html"))
        
        # Doctor Email  
        doctor_msg = MIMEMultipart("alternative")
        doctor_msg["Subject"] = "🚨 New Emergency Patient Appointment - TEST"
        doctor_msg["From"] = settings.SMTP_USER
        doctor_msg["To"] = settings.SMTP_USER
        doctor_msg.attach(MIMEText(
            "<html><body><h2>🚨 New Patient Appointment</h2>"
            "<p>Dear <strong>Dr. Test Doctor</strong>,</p>"
            "<p><strong>Patient:</strong> Test Patient (test@example.com)</p>"
            "<p><strong>Date:</strong> Tomorrow 10:00 AM</p>"
            "<p><strong>Symptoms:</strong> Emergency test symptoms requiring immediate attention</p>"
            "</body></html>", "html"))
        
        # Send both emails
        server.send_message(patient_msg)
        server.send_message(doctor_msg)
        server.quit()
        
        print("✅ Appointment emails sent successfully!")
        print(f"   Check your inbox: {settings.SMTP_USER}")
        return True
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False

def test_email():
    """Test basic email functionality"""
    print("📧 Testing email configuration...")
    print(f"   SMTP Host: {settings.SMTP_HOST}")
    print(f"   SMTP User: {settings.SMTP_USER}")
    print(f"   SMTP Pass: {'SET' if settings.SMTP_PASS else 'NOT SET'}")
    
    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASS:
        print("❌ Email not configured properly")
        return False
    
    try:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        
        # Send test email
        msg = MIMEText("Test email from Symptom Tracker MCP")
        msg["Subject"] = "Test Email"
        msg["From"] = settings.SMTP_USER
        msg["To"] = settings.SMTP_USER  # Send to self
        
        server.send_message(msg)
        server.quit()
        
        print("✅ Email test successful!")
        return True
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False

def add_sample_doctor():
    db = SessionLocal()
    try:
        # Check if doctor already exists
        existing = db.query(crud.models.Doctor).filter(
            crud.models.Doctor.full_name == "Dr. Sarah Johnson"
        ).first()
        
        if existing:
            print(f"✅ Doctor already exists: {existing.doctor_id}")
            print(f"   Name: {existing.full_name}")
            print(f"   City: {existing.city}")
            return existing
        
        doctor = crud.create_doctor(
            db,
            full_name="Dr. Sarah Johnson",
            specialization="General Practitioner", 
            clinic_name="City Health Clinic",
            city="New York",  # Change to your city
            contact_email="vaibhavtowardsdawn@gmail.com"  # Use real email for testing
        )
        print(f"✅ Doctor created: {doctor.doctor_id}")
        print(f"   Name: {doctor.full_name}")
        print(f"   City: {doctor.city}")
        print(f"   Email: {doctor.contact_email}")
        return doctor
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("Symptom Tracker Setup & Test")
    print("=" * 50)
    
    # Test basic email
    email_ok = test_email()
    print()
    
    if email_ok:
        # Test detailed appointment email
        print("Testing appointment email format...")
        test_email_detailed()
        print()
    
    # Add doctor
    add_sample_doctor()
    print()
    
    if email_ok:
        print("✅ Setup complete! Email and doctor ready.")
        print("   → Check your email inbox for test messages")
    else:
        print("⚠️ Setup complete but email needs fixing.")
        print("   → Check SMTP credentials in .env file")
    print("=" * 50)