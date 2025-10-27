import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.db.session import SessionLocal
from app.db import models

def get_patient_sessions(patient_id: str) -> List[Dict]:
    db = SessionLocal()
    sessions = db.query(models.Session).filter(models.Session.patient_id == patient_id).order_by(models.Session.start_time.desc()).all()
    db.close()
    
    session_data = []
    for session in sessions:
        session_data.append({
            "session_id": str(session.session_id),
            "start_time": session.start_time.isoformat(),
            "severity_score": float(session.severity_score) if session.severity_score else None,
            "red_flag": session.red_flag,
            "ai_summary": session.ai_summary
        })
    return session_data

def get_agent_memory(patient_id: str) -> Dict:
    all_sessions = get_patient_sessions(patient_id)
    
    if not all_sessions:
        return {"current_memory": [], "previous_memory": []}
    
    last_session_time = datetime.fromisoformat(all_sessions[0]["start_time"])
    
    current_memory = []
    previous_memory = []
    
    for session in all_sessions:
        session_start_time = datetime.fromisoformat(session["start_time"])
        
        if last_session_time - timedelta(hours=12) <= session_start_time <= last_session_time:
            current_memory.append(session)
        elif last_session_time - timedelta(hours=24) <= session_start_time < last_session_time - timedelta(hours=12):
            previous_memory.append(session)
            
    return {
        "current_memory": current_memory,
        "previous_memory": previous_memory
    }