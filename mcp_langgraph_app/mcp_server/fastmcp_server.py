"""Real MCP Server using FastMCP Protocol"""
from fastmcp import FastMCP
from typing import Any
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.db.session import SessionLocal
from app.db import models
from app.core import security
from app import crud
from datetime import datetime, timedelta
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from mcp_langgraph_app.config.settings import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

mcp = FastMCP("Symptom Tracker")

@mcp.tool()
async def analyze_symptoms_with_ai(symptoms: list[dict[str, Any]], free_text: str) -> dict[str, Any]:
    """Analyze patient symptoms using AI and return severity score, summary, and recommendations"""
    try:
        symptom_list = "\n".join([f"- {s.get('symptom', 'Unknown')}: Intensity {s.get('intensity', 0)}/10" for s in symptoms])
        
        prompt = f"""Analyze ONLY current symptoms and provide JSON response:
Current Symptoms: {symptom_list}
Description: {free_text}
{f"Current Memory (sessions within 12 hours): {current_memory}" if current_memory else ""}
{f"Previous Memory (sessions within 24 hours): {previous_memory}" if previous_memory else ""}

Return JSON with: summary (max 150 chars), severity (0-10), recommendation (yes/no), red_flags (list), suggested_actions (list), specialization_needed (Cardiologist/Neurologist/Dermatologist/Gastroenterologist/Orthopedist/General Practitioner)"""

        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = model.generate_content(prompt)
        text = response.text.strip().replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        
        result.setdefault("summary", "Symptoms analyzed")
        result.setdefault("severity", 5.0)
        result.setdefault("recommendation", "no")
        result.setdefault("red_flags", [])
        result.setdefault("suggested_actions", [])
        result.setdefault("specialization_needed", "General Practitioner")
        
        return json.dumps(result)
    except Exception as e:
        max_intensity = max([s.get('intensity', 0) for s in symptoms]) if symptoms else 0
        result = {
            "summary": f"Reported {len(symptoms)} symptoms with max intensity {max_intensity}",
            "severity": float(max_intensity),
            "recommendation": "yes" if max_intensity >= 8 else "no",
            "red_flags": [s['symptom'] for s in symptoms if s.get('intensity', 0) >= 8],
            "suggested_actions": ["Consult a doctor" if max_intensity >= 8 else "Monitor symptoms"],
            "specialization_needed": "General Practitioner"
        }
        return json.dumps(result)

@mcp.tool()
async def check_severity_threshold(severity: float, symptoms: list[dict[str, Any]]) -> str:
    """Check if symptoms meet emergency threshold (severity >= 8)"""
    max_intensity = max([s.get("intensity", 0) for s in symptoms]) if symptoms else 0
    is_emergency = severity >= 8 or max_intensity >= 8
    
    result = {
        "is_emergency": is_emergency,
        "severity_score": severity,
        "max_intensity": max_intensity,
        "critical_symptoms": [s.get("symptom") for s in symptoms if s.get("intensity", 0) >= 8],
        "recommendation": "immediate_appointment" if is_emergency else "monitor",
        "message": "EMERGENCY: Immediate medical attention required!" if is_emergency else "Symptoms logged."
    }
    return json.dumps(result)

@mcp.tool()
async def find_available_doctor(city: str, specialization: str, urgency: str = "normal", symptoms: list[dict[str, Any]] = []) -> str:
    """Find available doctor in patient's city using AI-powered matching"""
    db = SessionLocal()
    try:
        doctors = db.query(models.Doctor).filter(models.Doctor.city == city).all()
        if not doctors:
            return json.dumps({"success": False, "error": f"No doctors available in {city}"})
        
        doctors_list = "\n".join([f"{i+1}. Dr. {d.full_name} - {d.specialization} at {d.clinic_name}" for i, d in enumerate(doctors)])
        symptoms_text = ", ".join([s.get("symptom", "") for s in symptoms]) if symptoms else "Not specified"
        
        prompt = f"""Select BEST doctor:
City: {city}, Specialization: {specialization}, Symptoms: {symptoms_text}
Doctors: {doctors_list}
Return ONLY the number (1, 2, 3, etc.)."""

        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = model.generate_content(prompt)
        selected_index = int(response.text.strip()) - 1
        doctor = doctors[selected_index] if 0 <= selected_index < len(doctors) else doctors[0]
        
        result = {
            "success": True,
            "doctor_id": str(doctor.doctor_id),
            "full_name": doctor.full_name,
            "specialization": doctor.specialization,
            "clinic_name": doctor.clinic_name,
            "city": doctor.city,
            "contact_email": doctor.contact_email,
            "contact_number": doctor.contact_number,
            "available_slots": doctor.available_slots or []
        }
        return json.dumps(result)
    except Exception:
        doctor = doctors[0]
        result = {
            "success": True,
            "doctor_id": str(doctor.doctor_id),
            "full_name": doctor.full_name,
            "specialization": doctor.specialization,
            "clinic_name": doctor.clinic_name,
            "city": doctor.city,
            "contact_email": doctor.contact_email,
            "contact_number": doctor.contact_number,
            "available_slots": doctor.available_slots or []
        }
        return json.dumps(result)
    finally:
        db.close()

@mcp.tool()
async def save_session_to_database(patient_id: str, symptoms: list[dict[str, Any]], mood: int, free_text: str, ai_analysis: dict[str, Any]) -> str:
    """Save symptom session to database with AI analysis"""
    db = SessionLocal()
    try:
        severity = ai_analysis.get("severity", 0)
        red_flag = severity >= 8 or any(s.get("intensity", 0) >= 8 for s in symptoms)
        
        session = models.Session(
            patient_id=patient_id,
            severity_score=severity,
            red_flag=red_flag,
            callback_required=red_flag,
            ai_summary=ai_analysis.get("summary", "")
        )
        db.add(session)
        db.flush()
        
        crud.create_chat_log(db, session.session_id, "patient", free_text, intent="symptom_report")
        crud.create_chat_log(db, session.session_id, "bot", ai_analysis.get("summary", ""), intent="ai_summary")
        
        for symptom in symptoms:
            crud.create_symptom_entry(db, session.session_id, mood, symptom.get("symptom", ""), symptom.get("intensity", 0), symptom.get("notes", ""), symptom.get("photo_url"))
        
        db.commit()
        result = {"success": True, "session_id": str(session.session_id), "severity": severity, "red_flag": red_flag, "ai_summary": ai_analysis.get("summary", "")}
        return json.dumps(result)
    except Exception as e:
        db.rollback()
        return json.dumps({"success": False, "error": str(e)})
    finally:
        db.close()

@mcp.tool()
async def create_appointment(patient_id: str, doctor_id: str, session_id: str, appointment_type: str = "emergency", notes: str = "") -> str:
    """Create appointment in database"""
    db = SessionLocal()
    try:
        patient = db.query(models.Patient).filter(models.Patient.patient_id == patient_id).first()
        doctor = db.query(models.Doctor).filter(models.Doctor.doctor_id == doctor_id).first()
        
        if not patient or not doctor:
            return json.dumps({"success": False, "error": "Patient or doctor not found"})
        
        days_ahead = 1 if appointment_type == "emergency" else 3
        appointment_date = datetime.utcnow() + timedelta(days=days_ahead)
        notes_encrypted = security.encrypt_bytes(notes) if notes else None
        
        appointment = models.Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            session_id=session_id,
            appointment_date=appointment_date,
            clinic_location=doctor.clinic_name,
            status="confirmed",
            notes=notes_encrypted
        )
        
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        
        result = {
            "success": True,
            "appointment_id": str(appointment.appointment_id),
            "patient_name": patient.full_name,
            "patient_email": patient.email,
            "doctor_name": doctor.full_name,
            "doctor_email": doctor.contact_email,
            "clinic_location": doctor.clinic_name,
            "appointment_date": appointment_date.isoformat(),
            "appointment_type": appointment_type,
            "status": "confirmed"
        }
        return json.dumps(result)
    except Exception as e:
        db.rollback()
        return json.dumps({"success": False, "error": str(e)})
    finally:
        db.close()

@mcp.tool()
async def send_appointment_emails(patient_email: str, patient_name: str, doctor_email: str, doctor_name: str, clinic_name: str, appointment_date: str, symptoms_summary: str, appointment_type: str = "emergency", photo_urls: list[str] = []) -> str:
    """Send appointment confirmation emails to patient and doctor with photo attachments"""
    try:
        if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASS:
            return json.dumps({"success": False, "error": "Email configuration not set"})
        
        try:
            apt_date = datetime.fromisoformat(appointment_date.replace('Z', '+00:00'))
            formatted_date = apt_date.strftime("%B %d, %Y at %I:%M %p")
        except:
            formatted_date = appointment_date
        
        # Patient Email
        patient_msg = MIMEMultipart("alternative")
        patient_msg["Subject"] = f"{'Emergency ' if appointment_type == 'emergency' else ''}Appointment Confirmation"
        patient_msg["From"] = settings.SMTP_USER
        patient_msg["To"] = patient_email
        patient_msg.attach(MIMEText(f"<html><body><h2>Appointment Confirmed</h2><p>Dear <strong>{patient_name}</strong>,</p><p><strong>Doctor:</strong> Dr. {doctor_name}</p><p><strong>Clinic:</strong> {clinic_name}</p><p><strong>Date:</strong> {formatted_date}</p><p><strong>Symptoms:</strong> {symptoms_summary}</p></body></html>", "html"))
        
        # Doctor Email
        doctor_msg = MIMEMultipart("alternative")
        doctor_msg["Subject"] = f"New {'Emergency ' if appointment_type == 'emergency' else ''}Patient Appointment"
        doctor_msg["From"] = settings.SMTP_USER
        doctor_msg["To"] = doctor_email
        photo_section = f"<p><strong>Symptom Photos:</strong> {len(photo_urls)} image(s) attached</p>" if photo_urls else ""
        doctor_msg.attach(MIMEText(f"<html><body><h2>New Patient Appointment</h2><p>Dear <strong>Dr. {doctor_name}</strong>,</p><p><strong>Patient:</strong> {patient_name} ({patient_email})</p><p><strong>Date:</strong> {formatted_date}</p><p><strong>Symptoms:</strong> {symptoms_summary}</p>{photo_section}</body></html>", "html"))
        
        # Attach photos
        if photo_urls:
            uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "symptom_photos")
            for photo_url in photo_urls:
                try:
                    filename = photo_url.split("/")[-1]
                    filepath = os.path.join(uploads_dir, filename)
                    if os.path.exists(filepath):
                        with open(filepath, "rb") as f:
                            img_data = f.read()
                        image = MIMEImage(img_data)
                        image.add_header("Content-Disposition", "attachment", filename=filename)
                        doctor_msg.attach(image)
                except Exception as e:
                    print(f"Failed to attach photo: {e}")
        
        # Send emails with detailed logging
        print(f"Attempting to send emails...")
        print(f"   Patient: {patient_email}")
        print(f"   Doctor: {doctor_email}")
        print(f"   SMTP: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
        
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        
        patient_sent = False
        doctor_sent = False
        error_details = []
        
        try:
            server.send_message(patient_msg)
            patient_sent = True
            print(f"SUCCESS: Patient email sent successfully")
        except Exception as e:
            error_msg = f"Failed to send patient email: {e}"
            print(f"ERROR: {error_msg}")
            error_details.append(error_msg)
            
        try:
            server.send_message(doctor_msg)
            doctor_sent = True
            print(f"SUCCESS: Doctor email sent successfully")
        except Exception as e:
            error_msg = f"Failed to send doctor email: {e}"
            print(f"ERROR: {error_msg}")
            error_details.append(error_msg)
        
        server.quit()
        
        result = {
            "success": patient_sent and doctor_sent, 
            "patient_email_sent": patient_sent, 
            "doctor_email_sent": doctor_sent,
            "errors": error_details if error_details else None
        }
        print(f"Email result: {result}")
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

@mcp.tool()
async def get_patient_history(patient_id: str, limit: int = 5) -> str:
    """Get patient's symptom history"""
    db = SessionLocal()
    try:
        patient = db.query(models.Patient).filter(models.Patient.patient_id == patient_id).first()
        if not patient:
            return json.dumps({"success": False, "error": "Patient not found"})
        
        sessions = db.query(models.Session).filter(models.Session.patient_id == patient_id).order_by(models.Session.created_at.desc()).limit(limit).all()
        history = []
        for session in sessions:
            symptoms = db.query(models.SymptomEntry).filter(models.SymptomEntry.session_id == session.session_id).all()
            history.append({
                "session_id": str(session.session_id),
                "date": session.start_time.isoformat() if session.start_time else None,
                "severity": float(session.severity_score) if session.severity_score else 0,
                "red_flag": session.red_flag,
                "summary": session.ai_summary,
                "symptoms": [{"symptom": s.symptom, "intensity": s.intensity, "mood": s.mood} for s in symptoms]
            })
        
        result = {"success": True, "patient_id": str(patient.patient_id), "patient_name": patient.full_name, "city": patient.city, "history": history}
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})
    finally:
        db.close()


if __name__ == "__main__":
    mcp.run()
