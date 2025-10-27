"""Real MCP Server with SSE Transport - Production Ready"""
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
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

# Create MCP Server
mcp_server = Server("symptom-tracker-mcp")

@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools"""
    return [
        Tool(name="analyze_symptoms_with_ai", description="Analyze patient symptoms using AI", inputSchema={"type": "object", "properties": {"symptoms": {"type": "array"}, "free_text": {"type": "string"}}, "required": ["symptoms", "free_text"]}),
        Tool(name="check_severity_threshold", description="Check if symptoms meet emergency threshold", inputSchema={"type": "object", "properties": {"severity": {"type": "number"}, "symptoms": {"type": "array"}}, "required": ["severity", "symptoms"]}),
        Tool(name="find_available_doctor", description="Find available doctor using AI matching", inputSchema={"type": "object", "properties": {"city": {"type": "string"}, "specialization": {"type": "string"}, "urgency": {"type": "string"}, "symptoms": {"type": "array"}}, "required": ["city", "specialization"]}),
        Tool(name="save_session_to_database", description="Save symptom session to database", inputSchema={"type": "object", "properties": {"patient_id": {"type": "string"}, "symptoms": {"type": "array"}, "mood": {"type": "integer"}, "free_text": {"type": "string"}, "ai_analysis": {"type": "object"}}, "required": ["patient_id", "symptoms", "mood", "free_text", "ai_analysis"]}),
        Tool(name="create_appointment", description="Create appointment in database", inputSchema={"type": "object", "properties": {"patient_id": {"type": "string"}, "doctor_id": {"type": "string"}, "session_id": {"type": "string"}, "appointment_type": {"type": "string"}, "notes": {"type": "string"}}, "required": ["patient_id", "doctor_id", "session_id"]}),
        Tool(name="send_appointment_emails", description="Send appointment emails with photo attachments", inputSchema={"type": "object", "properties": {"patient_email": {"type": "string"}, "patient_name": {"type": "string"}, "doctor_email": {"type": "string"}, "doctor_name": {"type": "string"}, "clinic_name": {"type": "string"}, "appointment_date": {"type": "string"}, "symptoms_summary": {"type": "string"}, "appointment_type": {"type": "string"}, "photo_urls": {"type": "array"}}, "required": ["patient_email", "patient_name", "doctor_email", "doctor_name", "clinic_name", "appointment_date", "symptoms_summary"]}),
        Tool(name="get_patient_history", description="Get patient symptom history", inputSchema={"type": "object", "properties": {"patient_id": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["patient_id"]})
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle MCP tool calls"""
    
    if name == "analyze_symptoms_with_ai":
        result = await analyze_symptoms_with_ai(arguments["symptoms"], arguments["free_text"])
    elif name == "check_severity_threshold":
        result = await check_severity_threshold(arguments["severity"], arguments["symptoms"])
    elif name == "find_available_doctor":
        result = await find_available_doctor(arguments["city"], arguments["specialization"], arguments.get("urgency", "normal"), arguments.get("symptoms", []))
    elif name == "save_session_to_database":
        result = await save_session_to_database(arguments["patient_id"], arguments["symptoms"], arguments["mood"], arguments["free_text"], arguments["ai_analysis"])
    elif name == "create_appointment":
        result = await create_appointment(arguments["patient_id"], arguments["doctor_id"], arguments["session_id"], arguments.get("appointment_type", "emergency"), arguments.get("notes", ""))
    elif name == "send_appointment_emails":
        result = await send_appointment_emails(arguments["patient_email"], arguments["patient_name"], arguments["doctor_email"], arguments["doctor_name"], arguments["clinic_name"], arguments["appointment_date"], arguments["symptoms_summary"], arguments.get("appointment_type", "emergency"), arguments.get("photo_urls", []))
    elif name == "get_patient_history":
        result = await get_patient_history(arguments["patient_id"], arguments.get("limit", 5))
    else:
        result = {"error": f"Unknown tool: {name}"}
    
    return [TextContent(type="text", text=json.dumps(result))]

# Tool implementations
async def analyze_symptoms_with_ai(symptoms: list[dict[str, Any]], free_text: str) -> dict:
    try:
        symptom_list = "\n".join([f"- {s.get('symptom', 'Unknown')}: Intensity {s.get('intensity', 0)}/10" for s in symptoms])
        prompt = f"""Analyze symptoms and return JSON: {{"summary": "...", "severity": 0-10, "recommendation": "yes/no", "red_flags": [], "suggested_actions": [], "specialization_needed": "..."}}
Symptoms: {symptom_list}
Description: {free_text}"""
        
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = model.generate_content(prompt)
        text = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except:
        max_intensity = max([s.get('intensity', 0) for s in symptoms]) if symptoms else 0
        return {"summary": f"{len(symptoms)} symptoms", "severity": float(max_intensity), "recommendation": "yes" if max_intensity >= 8 else "no", "red_flags": [], "suggested_actions": [], "specialization_needed": "General Practitioner"}

async def check_severity_threshold(severity: float, symptoms: list[dict[str, Any]]) -> dict:
    max_intensity = max([s.get("intensity", 0) for s in symptoms]) if symptoms else 0
    is_emergency = severity >= 8 or max_intensity >= 8
    return {"is_emergency": is_emergency, "severity_score": severity, "max_intensity": max_intensity, "message": "⚠️ EMERGENCY" if is_emergency else "Logged"}

async def find_available_doctor(city: str, specialization: str, urgency: str = "normal", symptoms: list[dict[str, Any]] = []) -> dict:
    db = SessionLocal()
    try:
        doctors = db.query(models.Doctor).filter(models.Doctor.city == city).all()
        if not doctors:
            return {"success": False, "error": f"No doctors in {city}"}
        
        doctors_list = "\n".join([f"{i+1}. Dr. {d.full_name} - {d.specialization}" for i, d in enumerate(doctors)])
        symptoms_text = ", ".join([s.get("symptom", "") for s in symptoms]) if symptoms else ""
        prompt = f"Select best doctor number:\n{doctors_list}\nSymptoms: {symptoms_text}\nReturn only number."
        
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = model.generate_content(prompt)
        idx = int(response.text.strip()) - 1
        doctor = doctors[idx] if 0 <= idx < len(doctors) else doctors[0]
        
        return {"success": True, "doctor_id": str(doctor.doctor_id), "full_name": doctor.full_name, "specialization": doctor.specialization, "clinic_name": doctor.clinic_name, "city": doctor.city, "contact_email": doctor.contact_email, "contact_number": doctor.contact_number}
    except:
        doctor = doctors[0]
        return {"success": True, "doctor_id": str(doctor.doctor_id), "full_name": doctor.full_name, "specialization": doctor.specialization, "clinic_name": doctor.clinic_name, "city": doctor.city, "contact_email": doctor.contact_email, "contact_number": doctor.contact_number}
    finally:
        db.close()

async def save_session_to_database(patient_id: str, symptoms: list[dict[str, Any]], mood: int, free_text: str, ai_analysis: dict[str, Any]) -> dict:
    db = SessionLocal()
    try:
        severity = ai_analysis.get("severity", 0)
        red_flag = severity >= 8 or any(s.get("intensity", 0) >= 8 for s in symptoms)
        
        session = models.Session(patient_id=patient_id, severity_score=severity, red_flag=red_flag, callback_required=red_flag, ai_summary=ai_analysis.get("summary", ""))
        db.add(session)
        db.flush()
        
        crud.create_chat_log(db, session.session_id, "patient", free_text, intent="symptom_report")
        crud.create_chat_log(db, session.session_id, "bot", ai_analysis.get("summary", ""), intent="ai_summary")
        
        for symptom in symptoms:
            crud.create_symptom_entry(db, session.session_id, mood, symptom.get("symptom", ""), symptom.get("intensity", 0), symptom.get("notes", ""), symptom.get("photo_url"))
        
        db.commit()
        return {"success": True, "session_id": str(session.session_id), "severity": severity, "red_flag": red_flag}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()

async def create_appointment(patient_id: str, doctor_id: str, session_id: str, appointment_type: str = "emergency", notes: str = "") -> dict:
    db = SessionLocal()
    try:
        patient = db.query(models.Patient).filter(models.Patient.patient_id == patient_id).first()
        doctor = db.query(models.Doctor).filter(models.Doctor.doctor_id == doctor_id).first()
        
        if not patient or not doctor:
            return {"success": False, "error": "Not found"}
        
        appointment_date = datetime.utcnow() + timedelta(days=1 if appointment_type == "emergency" else 3)
        notes_encrypted = security.encrypt_bytes(notes) if notes else None
        
        appointment = models.Appointment(patient_id=patient_id, doctor_id=doctor_id, session_id=session_id, appointment_date=appointment_date, clinic_location=doctor.clinic_name, status="confirmed", notes=notes_encrypted)
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        
        return {"success": True, "appointment_id": str(appointment.appointment_id), "patient_name": patient.full_name, "patient_email": patient.email, "doctor_name": doctor.full_name, "doctor_email": doctor.contact_email, "clinic_location": doctor.clinic_name, "appointment_date": appointment_date.isoformat(), "status": "confirmed"}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()

async def send_appointment_emails(patient_email: str, patient_name: str, doctor_email: str, doctor_name: str, clinic_name: str, appointment_date: str, symptoms_summary: str, appointment_type: str = "emergency", photo_urls: list[str] = []) -> dict:
    try:
        if not settings.SMTP_HOST:
            return {"success": False, "error": "Email not configured"}
        
        try:
            apt_date = datetime.fromisoformat(appointment_date.replace('Z', '+00:00'))
            formatted_date = apt_date.strftime("%B %d, %Y at %I:%M %p")
        except:
            formatted_date = appointment_date
        
        patient_msg = MIMEMultipart()
        patient_msg["Subject"] = f"🏥 Appointment Confirmation"
        patient_msg["From"] = settings.SMTP_USER
        patient_msg["To"] = patient_email
        patient_msg.attach(MIMEText(f"<html><body><h2>Appointment Confirmed</h2><p>Dear {patient_name},</p><p>Doctor: Dr. {doctor_name}</p><p>Clinic: {clinic_name}</p><p>Date: {formatted_date}</p></body></html>", "html"))
        
        doctor_msg = MIMEMultipart()
        doctor_msg["Subject"] = f"🚨 New Patient Appointment"
        doctor_msg["From"] = settings.SMTP_USER
        doctor_msg["To"] = doctor_email
        doctor_msg.attach(MIMEText(f"<html><body><h2>New Appointment</h2><p>Dear Dr. {doctor_name},</p><p>Patient: {patient_name}</p><p>Date: {formatted_date}</p><p>Symptoms: {symptoms_summary}</p></body></html>", "html"))
        
        if photo_urls:
            uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "symptom_photos")
            for photo_url in photo_urls:
                try:
                    filename = photo_url.split("/")[-1]
                    filepath = os.path.join(uploads_dir, filename)
                    if os.path.exists(filepath):
                        with open(filepath, "rb") as f:
                            img = MIMEImage(f.read())
                        img.add_header("Content-Disposition", "attachment", filename=filename)
                        doctor_msg.attach(img)
                except:
                    pass
        
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(patient_msg)
        server.send_message(doctor_msg)
        server.quit()
        
        return {"success": True, "patient_email_sent": True, "doctor_email_sent": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_patient_history(patient_id: str, limit: int = 5) -> dict:
    db = SessionLocal()
    try:
        patient = db.query(models.Patient).filter(models.Patient.patient_id == patient_id).first()
        if not patient:
            return {"success": False, "error": "Not found"}
        
        sessions = db.query(models.Session).filter(models.Session.patient_id == patient_id).order_by(models.Session.created_at.desc()).limit(limit).all()
        history = []
        for session in sessions:
            symptoms = db.query(models.SymptomEntry).filter(models.SymptomEntry.session_id == session.session_id).all()
            history.append({"session_id": str(session.session_id), "date": session.start_time.isoformat() if session.start_time else None, "severity": float(session.severity_score) if session.severity_score else 0, "summary": session.ai_summary, "symptoms": [{"symptom": s.symptom, "intensity": s.intensity} for s in symptoms]})
        
        return {"success": True, "patient_id": str(patient.patient_id), "patient_name": patient.full_name, "history": history}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        db.close()

# Starlette app with SSE transport
async def handle_sse(request):
    async with SseServerTransport("/messages") as transport:
        await mcp_server.run(transport.reader, transport.writer, mcp_server.create_initialization_options())

async def health(request):
    return JSONResponse({"status": "healthy", "service": "MCP SSE Server", "protocol": "official"})

app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/health", endpoint=health)
    ]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
