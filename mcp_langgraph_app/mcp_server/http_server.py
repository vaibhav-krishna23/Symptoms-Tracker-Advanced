"""HTTP wrapper for MCP tools"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.db.session import SessionLocal
from app.db import models
from app.core import security
from app import crud
from datetime import datetime, timedelta
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import google.generativeai as genai

# Load settings
from mcp_langgraph_app.config.settings import settings

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

app = FastAPI(title="MCP Tools HTTP Server", version="1.0.0")

class ToolRequest(BaseModel):
    pass

@app.get("/")
def root():
    return {"message": "MCP Tools HTTP Server", "status": "running"}

@app.get("/tools")
def list_tools():
    return {
        "tools": [
            "analyze_symptoms_with_ai",
            "find_available_doctor", 
            "create_appointment",
            "send_appointment_emails",
            "get_patient_history",
            "save_session_to_database",
            "check_severity_threshold"
        ]
    }

@app.post("/tools/analyze_symptoms_with_ai")
async def analyze_symptoms_with_ai(request: Dict[str, Any]):
    symptoms = request.get("symptoms", [])
    free_text = request.get("free_text", "")
    patient_history = request.get("patient_history")
    
    try:
        symptom_list = "\n".join([
            f"- {s.get('symptom', 'Unknown')}: Intensity {s.get('intensity', 0)}/10"
            for s in symptoms
        ])
        
        history_context = f"\n\nPatient History:\n{patient_history}" if patient_history else ""
        
        prompt = f"""You are a medical AI assistant analyzing ONLY current symptoms. Do NOT consider any past medical history.

Current Session Symptoms:
{symptom_list}

Patient's Current Description:
{free_text}

Analyze ONLY these current symptoms and provide JSON response:
1. "summary": Brief summary of current symptoms only (max 150 chars)
2. "severity": Score 0-10 based ONLY on current symptoms (0=no concern, 5=moderate, 8+=urgent, 10=life-threatening)
3. "recommendation": "yes" if current symptoms need medical attention, "no" otherwise
4. "red_flags": Current concerning symptoms only
5. "suggested_actions": Actions for current symptoms
6. "specialization_needed": Doctor type for current symptoms ("Cardiologist", "Neurologist", "Dermatologist", "Gastroenterologist", "Orthopedist", "General Practitioner")

Severity Guidelines:
- 0-2: Minor symptoms, self-care
- 3-5: Moderate, routine appointment
- 6-7: Concerning, prompt care needed
- 8-9: Urgent, same-day care
- 10: Emergency, immediate care

Return ONLY valid JSON."""

        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        result = json.loads(text)
        
        # Validate and set defaults
        result.setdefault("summary", "Symptoms analyzed")
        result.setdefault("severity", 5.0)
        result.setdefault("recommendation", "no")
        result.setdefault("red_flags", [])
        result.setdefault("suggested_actions", [])
        result.setdefault("specialization_needed", "General Practitioner")
        
        return result
        
    except Exception as e:
        # Fallback heuristic analysis
        max_intensity = max([s.get('intensity', 0) for s in symptoms]) if symptoms else 0
        
        return {
            "summary": f"Reported {len(symptoms)} symptoms with max intensity {max_intensity}. {free_text[:100]}",
            "severity": float(max_intensity),
            "recommendation": "yes" if max_intensity >= 8 else "no",
            "red_flags": [s['symptom'] for s in symptoms if s.get('intensity', 0) >= 8],
            "suggested_actions": ["Consult a doctor" if max_intensity >= 8 else "Monitor symptoms"],
            "specialization_needed": "General Practitioner",
            "error": str(e)
        }

@app.post("/tools/check_severity_threshold")
async def check_severity_threshold(request: Dict[str, Any]):
    severity = request.get("severity", 0)
    symptoms = request.get("symptoms", [])
    
    max_intensity = max([s.get("intensity", 0) for s in symptoms]) if symptoms else 0
    
    is_emergency = severity >= 8 or max_intensity >= 8
    
    critical_symptoms = [
        s.get("symptom") for s in symptoms 
        if s.get("intensity", 0) >= 8
    ]
    
    return {
        "is_emergency": is_emergency,
        "severity_score": severity,
        "max_intensity": max_intensity,
        "critical_symptoms": critical_symptoms,
        "recommendation": "immediate_appointment" if is_emergency else "monitor",
        "message": "⚠️ EMERGENCY: Immediate medical attention required!" if is_emergency else "Symptoms logged. Monitor your condition."
    }

@app.post("/tools/find_available_doctor")
async def find_available_doctor(request: Dict[str, Any]):
    city = request.get("city", "")
    specialization = request.get("specialization")
    urgency = request.get("urgency", "normal")
    symptoms = request.get("symptoms", [])
    
    db = SessionLocal()
    try:
        # Get all doctors in the city
        doctors = db.query(models.Doctor).filter(models.Doctor.city == city).all()
        
        if not doctors:
            return {
                "success": False,
                "error": f"No doctors available in {city}"
            }
        
        # Use LLM to select best doctor
        doctors_list = "\n".join([
            f"{i+1}. Dr. {d.full_name} - {d.specialization} at {d.clinic_name}"
            for i, d in enumerate(doctors)
        ])
        
        symptoms_text = ", ".join([s.get("symptom", "") for s in symptoms]) if symptoms else "Not specified"
        
        prompt = f"""Select the BEST doctor for this patient:

Patient City: {city}
Needed Specialization: {specialization}
Symptoms: {symptoms_text}
Urgency: {urgency}

Available Doctors:
{doctors_list}

Return ONLY the number (1, 2, 3, etc.) of the BEST matching doctor. 
Prioritize exact specialization match, then general practitioners.
Return ONLY the number, nothing else."""

        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = model.generate_content(prompt)
        selected_index = int(response.text.strip()) - 1
        
        doctor = doctors[selected_index] if 0 <= selected_index < len(doctors) else doctors[0]
        
        return {
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
        
    except Exception as e:
        # Fallback to first specialist or any doctor
        if specialization:
            specialist = next((d for d in doctors if d.specialization == specialization), None)
            doctor = specialist if specialist else doctors[0]
        else:
            doctor = doctors[0]
            
        return {
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
    finally:
        db.close()

@app.post("/tools/save_session_to_database")
async def save_session_to_database(request: Dict[str, Any]):
    patient_id = request.get("patient_id")
    symptoms = request.get("symptoms", [])
    mood = request.get("mood", 3)
    free_text = request.get("free_text", "")
    ai_analysis = request.get("ai_analysis", {})
    
    db = SessionLocal()
    try:
        severity = ai_analysis.get("severity", 0)
        red_flag = severity >= 8 or any(s.get("intensity", 0) >= 8 for s in symptoms)
        
        # Create session
        session = models.Session(
            patient_id=patient_id,
            severity_score=severity,
            red_flag=red_flag,
            callback_required=red_flag,
            ai_summary=ai_analysis.get("summary", "")
        )
        db.add(session)
        db.flush()
        
        # Save chat logs
        crud.create_chat_log(db, session.session_id, "patient", free_text, intent="symptom_report")
        crud.create_chat_log(db, session.session_id, "bot", ai_analysis.get("summary", ""), intent="ai_summary")
        
        # Save symptoms
        for symptom in symptoms:
            crud.create_symptom_entry(
                db,
                session.session_id,
                mood,
                symptom.get("symptom", ""),
                symptom.get("intensity", 0),
                symptom.get("notes", ""),
                symptom.get("photo_url")
            )
        
        db.commit()
        
        return {
            "success": True,
            "session_id": str(session.session_id),
            "severity": severity,
            "red_flag": red_flag,
            "ai_summary": ai_analysis.get("summary", "")
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()

@app.post("/tools/get_patient_history")
async def get_patient_history(request: Dict[str, Any]):
    patient_id = request.get("patient_id")
    limit = request.get("limit", 5)
    
    db = SessionLocal()
    try:
        patient = db.query(models.Patient).filter(models.Patient.patient_id == patient_id).first()
        if not patient:
            return {
                "success": False,
                "error": "Patient not found"
            }
        
        sessions = db.query(models.Session).filter(
            models.Session.patient_id == patient_id
        ).order_by(models.Session.created_at.desc()).limit(limit).all()
        
        history = []
        for session in sessions:
            symptoms = db.query(models.SymptomEntry).filter(
                models.SymptomEntry.session_id == session.session_id
            ).all()
            
            history.append({
                "session_id": str(session.session_id),
                "date": session.start_time.isoformat() if session.start_time else None,
                "severity": float(session.severity_score) if session.severity_score else 0,
                "red_flag": session.red_flag,
                "summary": session.ai_summary,
                "symptoms": [
                    {
                        "symptom": s.symptom,
                        "intensity": s.intensity,
                        "mood": s.mood
                    } for s in symptoms
                ]
            })
        
        return {
            "success": True,
            "patient_id": str(patient.patient_id),
            "patient_name": patient.full_name,
            "city": patient.city,
            "history": history
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()

@app.post("/tools/create_appointment")
async def create_appointment(request: Dict[str, Any]):
    patient_id = request.get("patient_id")
    doctor_id = request.get("doctor_id")
    session_id = request.get("session_id")
    appointment_type = request.get("appointment_type", "emergency")
    notes = request.get("notes")
    
    db = SessionLocal()
    try:
        # Get patient and doctor info
        patient = db.query(models.Patient).filter(models.Patient.patient_id == patient_id).first()
        doctor = db.query(models.Doctor).filter(models.Doctor.doctor_id == doctor_id).first()
        
        if not patient or not doctor:
            return {
                "success": False,
                "error": "Patient or doctor not found"
            }
        
        # Calculate appointment date
        days_ahead = 1 if appointment_type == "emergency" else 3
        appointment_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        # Create appointment
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
        
        return {
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
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()

@app.post("/tools/send_appointment_emails")
async def send_appointment_emails(request: Dict[str, Any]):
    patient_email = request.get("patient_email")
    patient_name = request.get("patient_name")
    doctor_email = request.get("doctor_email")
    doctor_name = request.get("doctor_name")
    clinic_name = request.get("clinic_name")
    appointment_date = request.get("appointment_date")
    symptoms_summary = request.get("symptoms_summary")
    appointment_type = request.get("appointment_type", "emergency")
    
    try:
        if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASS:
            return {
                "success": False,
                "error": "Email configuration not set",
                "patient_email_sent": False,
                "doctor_email_sent": False
            }
        
        # Format appointment date
        try:
            apt_date = datetime.fromisoformat(appointment_date.replace('Z', '+00:00'))
            formatted_date = apt_date.strftime("%B %d, %Y at %I:%M %p")
        except:
            formatted_date = appointment_date
        
        # Patient Email
        patient_msg = MIMEMultipart("alternative")
        patient_msg["Subject"] = f"🏥 {'Emergency ' if appointment_type == 'emergency' else ''}Appointment Confirmation"
        patient_msg["From"] = settings.SMTP_USER
        patient_msg["To"] = patient_email
        
        patient_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>🏥 Appointment Confirmed</h2>
            <p>Dear <strong>{patient_name}</strong>,</p>
            <p>Your appointment has been scheduled.</p>
            <p><strong>Doctor:</strong> Dr. {doctor_name}</p>
            <p><strong>Clinic:</strong> {clinic_name}</p>
            <p><strong>Date:</strong> {formatted_date}</p>
            <p><strong>Symptoms:</strong> {symptoms_summary}</p>
        </body>
        </html>
        """
        patient_msg.attach(MIMEText(patient_html, "html"))
        
        # Doctor Email
        doctor_msg = MIMEMultipart("alternative")
        doctor_msg["Subject"] = f"🚨 New {'Emergency ' if appointment_type == 'emergency' else ''}Patient Appointment"
        doctor_msg["From"] = settings.SMTP_USER
        doctor_msg["To"] = doctor_email
        
        doctor_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>🚨 New Patient Appointment</h2>
            <p>Dear <strong>Dr. {doctor_name}</strong>,</p>
            <p><strong>Patient:</strong> {patient_name} ({patient_email})</p>
            <p><strong>Date:</strong> {formatted_date}</p>
            <p><strong>Symptoms:</strong> {symptoms_summary}</p>
        </body>
        </html>
        """
        doctor_msg.attach(MIMEText(doctor_html, "html"))
        
        # Send emails
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        
        patient_sent = False
        doctor_sent = False
        
        try:
            server.send_message(patient_msg)
            patient_sent = True
        except Exception as e:
            print(f"Failed to send patient email: {e}")
        
        try:
            server.send_message(doctor_msg)
            doctor_sent = True
        except Exception as e:
            print(f"Failed to send doctor email: {e}")
        
        server.quit()
        
        return {
            "success": patient_sent and doctor_sent,
            "patient_email_sent": patient_sent,
            "doctor_email_sent": doctor_sent,
            "patient_email": patient_email,
            "doctor_email": doctor_email
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "patient_email_sent": False,
            "doctor_email_sent": False
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8001)