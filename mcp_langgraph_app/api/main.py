"""FastAPI application integrating MCP + LangGraph"""
from fastapi import FastAPI, Depends, HTTPException, Header, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from pathlib import Path
import uuid
import shutil
import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.db.session import get_db, engine, Base
from app.db import models
from app import crud
from app.schemas.patient import PatientCreate, PatientLogin, Token
from jose import jwt
from datetime import datetime, timedelta
from mcp_langgraph_app.config.settings import settings
from mcp_langgraph_app.langgraph_agent.mcp_client import MCPClient
from mcp_langgraph_app.langgraph_agent.agent_fixed import SymptomTrackerAgent
from mcp_langgraph_app.api.appointment_booking import router as appointment_router
from mcp_langgraph_app.api.fastmcp_routes import router as fastmcp_router

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title="Symptom Tracker with MCP + LangGraph",
    description="AI-Powered Healthcare Monitoring with MCP and LangGraph",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(appointment_router)
app.include_router(fastmcp_router)

# Create uploads directory and mount static files
UPLOAD_DIR = Path("uploads/symptom_photos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Initialize MCP client and LangGraph agent (lazy loading)
mcp_client = None
agent = None

def get_agent():
    global mcp_client, agent
    if agent is None:
        try:
            print(f"Initializing MCP client at http://{settings.MCP_SERVER_HOST}:{settings.MCP_SERVER_PORT}")
            mcp_client = MCPClient(server_url=f"http://{settings.MCP_SERVER_HOST}:{settings.MCP_SERVER_PORT}")
            print("Initializing LangGraph agent...")
            agent = SymptomTrackerAgent(mcp_client)
            print("Agent initialized successfully")
        except Exception as e:
            print(f"ERROR initializing agent: {e}")
            import traceback
            traceback.print_exc()
            raise
    return agent


# Pydantic Models
class SymptomInput(BaseModel):
    symptom: str
    intensity: int
    notes: Optional[str] = None
    photo_url: Optional[str] = None


class SymptomSubmission(BaseModel):
    symptoms: List[SymptomInput]
    mood: int
    free_text: str


class AppointmentBooking(BaseModel):
    session_id: str


# Helper Functions
def get_patient_id_from_token(authorization: str = Header(None)) -> str:
    """Extract patient ID from JWT token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        patient_id = payload.get("sub")
        if not patient_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return patient_id
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


# Routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Symptom Tracker API with MCP + LangGraph",
        "version": "2.0.0",
        "features": ["MCP Tools", "LangGraph Workflow", "AI Analysis", "Appointment Booking"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "mcp_server": f"{settings.MCP_SERVER_HOST}:{settings.MCP_SERVER_PORT}",
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat()
    }


# Authentication Routes
@app.post("/api/v1/auth/register", response_model=dict)
def register(payload: PatientCreate, db: Session = Depends(get_db)):
    """Register a new patient."""
    existing = crud.get_patient_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    patient = crud.create_patient(
        db,
        payload.full_name,
        payload.email,
        payload.password,
        payload.secret_key,
        payload.city
    )
    
    return {
        "patient_id": str(patient.patient_id),
        "message": "Registration successful"
    }


@app.post("/api/v1/auth/login", response_model=Token)
def login(payload: PatientLogin, db: Session = Depends(get_db)):
    """Login and get access token."""
    user = crud.verify_patient_credentials(db, payload.email, payload.password, payload.secret_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": str(user.patient_id)})
    return {
        "access_token": token,
        "token_type": "bearer"
    }


# Symptom Tracking Routes (MCP + LangGraph)
@app.post("/api/v2/symptoms/submit")
async def submit_symptoms_langgraph(
    payload: SymptomSubmission,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Submit symptoms using LangGraph workflow with MCP tools.
    This is the new MCP + LangGraph powered endpoint.
    """
    try:
        patient_id = get_patient_id_from_token(authorization)
        
        # Convert symptoms to dict format
        symptoms_list = [
            {
                "symptom": s.symptom,
                "intensity": s.intensity,
                "notes": s.notes,
                "photo_url": s.photo_url
            }
            for s in payload.symptoms
        ]
        
        # Process through LangGraph agent
        agent_instance = get_agent()
        result = await agent_instance.process_symptoms(
            patient_id=patient_id,
            symptoms=symptoms_list,
            mood=payload.mood,
            free_text=payload.free_text
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Processing failed"))
        
        return {
            "success": True,
            "session_id": result["session_id"],
            "ai_analysis": result["ai_analysis"],
            "severity_check": result["severity_check"],
            "appointment_info": result.get("appointment_info", {}),
            "workflow_messages": result["messages"]
        }
    except Exception as e:
        import traceback
        print("\n" + "="*60)
        print("ERROR IN /api/v2/symptoms/submit:")
        print("="*60)
        traceback.print_exc()
        print("="*60 + "\n")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/v2/symptoms/history")
async def get_symptom_history(
    authorization: str = Header(None),
    limit: int = 10
):
    """Get patient symptom history using MCP tool."""
    patient_id = get_patient_id_from_token(authorization)
    
    agent_instance = get_agent()
    result = await mcp_client.call_tool(
        "get_patient_history",
        patient_id=patient_id,
        limit=limit
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "History not found"))
    
    return result


# Dashboard Routes
@app.get("/api/v1/dashboard/sessions")
def get_patient_sessions(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get all patient sessions."""
    patient_id = get_patient_id_from_token(authorization)
    
    sessions = crud.get_sessions_by_patient(db, patient_id)
    
    return {
        "sessions": [
            {
                "session_id": str(s.session_id),
                "start_time": s.start_time.isoformat() if s.start_time else None,
                "severity_score": float(s.severity_score) if s.severity_score else 0,
                "red_flag": s.red_flag,
                "ai_summary": s.ai_summary
            }
            for s in sessions
        ]
    }


@app.get("/api/v1/dashboard/session/{session_id}/details")
def get_session_details(
    session_id: str,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get detailed session information including chat logs."""
    patient_id = get_patient_id_from_token(authorization)
    
    # Verify session belongs to patient
    session = db.query(models.Session).filter(
        models.Session.session_id == session_id,
        models.Session.patient_id == patient_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get symptoms
    symptoms = db.query(models.SymptomEntry).filter(
        models.SymptomEntry.session_id == session_id
    ).all()
    
    # Get chat logs
    from app.core.security import decrypt_bytes
    chat_logs = crud.get_chat_logs(db, session_id)
    
    return {
        "session": {
            "session_id": str(session.session_id),
            "start_time": session.start_time.isoformat() if session.start_time else None,
            "severity_score": float(session.severity_score) if session.severity_score else 0,
            "red_flag": session.red_flag,
            "ai_summary": session.ai_summary
        },
        "symptoms": [
            {
                "symptom": s.symptom,
                "intensity": s.intensity,
                "mood": s.mood,
                "notes": decrypt_bytes(s.notes) if s.notes else None
            }
            for s in symptoms
        ],
        "chat_logs": [
            {
                "sender": log.sender,
                "message": decrypt_bytes(log.message) if log.message else "",
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "intent": log.intent
            }
            for log in chat_logs
        ]
    }


# MCP Tools Info
@app.get("/api/v2/mcp/tools")
async def list_mcp_tools():
    """List available MCP tools."""
    agent_instance = get_agent()
    result = await mcp_client.list_tools()
    return result


# Doctor Management (Admin)
@app.post("/api/v1/admin/doctors")
def create_doctor(
    full_name: str,
    specialization: str,
    clinic_name: str,
    city: str,
    contact_email: str,
    contact_number: str = "",
    db: Session = Depends(get_db)
):
    """Create a new doctor (admin endpoint)."""
    doctor = crud.create_doctor(
        db,
        full_name=full_name,
        specialization=specialization,
        clinic_name=clinic_name,
        city=city,
        contact_email=contact_email
    )
    
    return {
        "doctor_id": str(doctor.doctor_id),
        "message": "Doctor created successfully"
    }


@app.get("/api/v1/admin/doctors")
def list_doctors(db: Session = Depends(get_db)):
    """List all doctors."""
    doctors = db.query(models.Doctor).all()
    
    return {
        "doctors": [
            {
                "doctor_id": str(d.doctor_id),
                "full_name": d.full_name,
                "specialization": d.specialization,
                "clinic_name": d.clinic_name,
                "city": d.city,
                "contact_email": d.contact_email
            }
            for d in doctors
        ]
    }


# Photo Upload
@app.post("/api/v1/upload/symptom-photo")
async def upload_symptom_photo(
    file: UploadFile = File(...),
    authorization: str = Header(None)
):
    """Upload symptom photo"""
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/jpg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Only image files allowed")
    
    # Validate file size (max 5MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File must be less than 5MB")
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with file_path.open("wb") as buffer:
        buffer.write(contents)
    
    return {
        "success": True,
        "photo_url": f"/uploads/symptom_photos/{unique_filename}",
        "filename": unique_filename
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
