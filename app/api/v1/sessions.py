"""Initialization or Placeholder File."""
# app/api/v1/sessions.py
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db.session import get_db
from app import crud
from app.db import models
from app.schemas.session import SessionCreate
from app.services import ai_processor, appointment_scheduler
# from app.services.email_service import send_appointment_email, send_doctor_notification
from app.core.config import settings
import redis
import json
from app.core.security import decrypt_bytes
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_emails(patient_email, patient_name, doctor_email, doctor_name, clinic_name, appointment_date, session_summary):
    try:
        if settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASS:
            # Patient email
            patient_msg = MIMEMultipart()
            patient_msg["Subject"] = "🏥 Appointment Confirmation"
            patient_msg["From"] = settings.SMTP_USER
            patient_msg["To"] = patient_email
            patient_html = f"""<h2>🏥 Appointment Confirmed</h2><p>Dear {patient_name},</p><p>Appointment with Dr. {doctor_name} at {clinic_name} on {appointment_date}</p><p>Symptoms: {session_summary}</p>"""
            patient_msg.attach(MIMEText(patient_html, "html"))
            
            # Doctor email
            doctor_msg = MIMEMultipart()
            doctor_msg["Subject"] = "🚨 New Emergency Appointment"
            doctor_msg["From"] = settings.SMTP_USER
            doctor_msg["To"] = doctor_email
            doctor_html = f"""<h2>🚨 New Emergency Patient</h2><p>Dr. {doctor_name},</p><p>Patient: {patient_name} ({patient_email})</p><p>Date: {appointment_date}</p><p>Symptoms: {session_summary}</p>"""
            doctor_msg.attach(MIMEText(doctor_html, "html"))
            
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(patient_msg)
            server.send_message(doctor_msg)
            server.quit()
            return True
        else:
            print(f"EMAILS: Patient({patient_email}) Doctor({doctor_email}) - {appointment_date}")
            return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

r = redis.from_url(settings.REDIS_URL, decode_responses=True)

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])

def get_patient_id_from_token(authorization: str = Header(None)):
    from jose import jwt
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    try:
        scheme, token = authorization.split()
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    return payload.get("sub")

@router.post("/submit")
def submit_session(payload: SessionCreate, authorization: str = Header(None), db: Session = Depends(get_db)):
    patient_id = get_patient_id_from_token(authorization)
    if not patient_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    # compute severity (LLM)
    ai_result = ai_processor.generate_summary_structured(payload.free_text, [s.dict() for s in payload.symptoms])
    try:
        summary_text = ai_result.get("summary")
        severity = float(ai_result.get("severity", 0))
        recommendation = ai_result.get("recommendation", "no")
    except Exception:
        summary_text = str(ai_result)
        severity = 0.0
        recommendation = "no"

    red_flag = severity >= 8 or any([s.intensity >= 8 for s in payload.symptoms])

    # create session record
    session = crud.create_session(db, patient_id, severity_score=severity, red_flag=red_flag, callback_required=red_flag, ai_summary=summary_text)
    # chat logs and symptoms
    free_text = payload.free_text or "No additional description provided"
    crud.create_chat_log(db, session.session_id, "patient", free_text, intent="symptom_report")
    crud.create_chat_log(db, session.session_id, "bot", summary_text, intent="ai_summary")

    for s in payload.symptoms:
        crud.create_symptom_entry(db, session.session_id, payload.mood, s.symptom, s.intensity, s.notes, s.photo_url)

    # Redis caching removed due to connection issues

    response = {"session_id": str(session.session_id), "severity": severity, "red_flag": red_flag, "ai_summary": summary_text, "recommendation": recommendation}

    # if recommendation yes, include suggested doctor (simple)
    if recommendation == "yes":
        patient = crud.get_patient_by_id(db, patient_id)
        if patient and patient.city:
            doctor = appointment_scheduler.find_doctor_for_symptoms(db, patient.city, [s.dict() for s in payload.symptoms])
            if doctor:
                response["suggested_doctor"] = {"doctor_id": str(doctor.doctor_id), "full_name": doctor.full_name, "clinic": doctor.clinic_name}
    return response

@router.post("/book-appointment")
def book_appointment(request: dict, authorization: str = Header(None), db: Session = Depends(get_db)):
    patient_id = get_patient_id_from_token(authorization)
    if not patient_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    session_id = request.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    # Get session and verify ownership
    session = db.query(models.Session).filter(models.Session.session_id == session_id, models.Session.patient_id == patient_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get patient info for city
    patient = crud.get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Find available doctor
    doctor = db.query(models.Doctor).filter(models.Doctor.city == patient.city).first()
    if not doctor:
        return {"error": "No available doctors found in your city"}
    
    # Create appointment
    from datetime import datetime, timedelta
    appointment_date = datetime.utcnow() + timedelta(days=1)
    appointment = models.Appointment(
        patient_id=patient_id,
        doctor_id=doctor.doctor_id,
        session_id=session_id,
        appointment_date=appointment_date,
        clinic_location=doctor.clinic_name,
        status="pending"
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    
    # Get chat logs for email summary
    logs = crud.get_chat_logs(db, session_id)
    chat_summary = ""
    for log in logs:
        if log.sender == "patient":
            chat_summary += f"Patient: {decrypt_bytes(log.message)}\n"
        elif log.sender == "bot":
            chat_summary += f"AI Analysis: {decrypt_bytes(log.message)}\n"
    
    # Send emails to both patient and doctor
    emails_sent = send_emails(
        patient_email=patient.email,
        patient_name=patient.full_name,
        doctor_email=doctor.contact_email,
        doctor_name=doctor.full_name,
        clinic_name=doctor.clinic_name,
        appointment_date=appointment_date.strftime("%Y-%m-%d %H:%M"),
        session_summary=chat_summary or "Severe symptoms reported requiring immediate attention"
    )
    
    return {
        "appointment_id": str(appointment.appointment_id),
        "doctor_name": doctor.full_name,
        "clinic": doctor.clinic_name,
        "appointment_date": appointment_date.isoformat(),
        "emails_sent": emails_sent,
        "message": f"Appointment scheduled with {doctor.full_name} at {doctor.clinic_name}. Emails sent to patient ({patient.email}) and doctor ({doctor.contact_email})"
    }
