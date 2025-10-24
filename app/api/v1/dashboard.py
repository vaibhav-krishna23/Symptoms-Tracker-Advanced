"""Initialization or Placeholder File."""
# app/api/v1/dashboard.py
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app import crud
from app.core.config import settings
from jose import jwt
from app.core.security import decrypt_bytes

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

def get_patient_id_from_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    try:
        scheme, token = authorization.split()
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    return payload.get("sub")

@router.get("/sessions")
def list_sessions(authorization: str = Header(None), db: Session = Depends(get_db)):
    pid = get_patient_id_from_token(authorization)
    if not pid:
        raise HTTPException(status_code=401)
    rows = crud.get_sessions_by_patient(db, pid)
    out = []
    for r in rows:
        out.append({"session_id": str(r.session_id), "start_time": str(r.start_time), "severity_score": float(r.severity_score) if r.severity_score else None, "red_flag": r.red_flag, "ai_summary": r.ai_summary})
    return out

@router.get("/logs/{session_id}")
def get_logs(session_id: str, authorization: str = Header(None), db: Session = Depends(get_db)):
    pid = get_patient_id_from_token(authorization)
    if not pid:
        raise HTTPException(status_code=401)
    logs = crud.get_chat_logs(db, session_id)
    result = []
    for l in logs:
        try:
            text = decrypt_bytes(l.message)
        except Exception:
            text = "<decryption failed>"
        result.append({"sender": l.sender, "message": text, "timestamp": str(l.timestamp)})
    return result
