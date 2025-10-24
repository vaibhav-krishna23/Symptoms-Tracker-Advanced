"""Initialization or Placeholder File."""
# app/crud.py
from sqlalchemy.orm import Session
from app.db import models
from app.core import security
from typing import Optional
from sqlalchemy import select

def create_patient(db: Session, full_name: str, email: str, password: str, secret_key_plain: str, city: Optional[str] = None):
    hashed = security.hash_password(password)
    encrypted = security.encrypt_bytes(secret_key_plain)
    p = models.Patient(full_name=full_name, email=email, password_hash=hashed, secret_key_encrypted=encrypted, city=city)
    db.add(p); db.commit(); db.refresh(p)
    return p

def get_patient_by_email(db: Session, email: str):
    return db.query(models.Patient).filter(models.Patient.email == email).first()

def get_patient_by_id(db: Session, patient_id):
    return db.query(models.Patient).filter(models.Patient.patient_id == patient_id).first()

def verify_patient_credentials(db: Session, email: str, password: str, secret_key_plain: str):
    p = get_patient_by_email(db, email)
    if not p:
        return None
    if not security.verify_password(password, p.password_hash):
        return None
    try:
        stored = security.decrypt_bytes(p.secret_key_encrypted)
    except Exception:
        return None
    if stored != secret_key_plain:
        return None
    return p

def create_session(db: Session, patient_id, severity_score=None, red_flag=False, callback_required=False, ai_summary=None):
    s = models.Session(patient_id=patient_id, severity_score=severity_score, red_flag=red_flag,
                       callback_required=callback_required, ai_summary=ai_summary)
    db.add(s); db.commit(); db.refresh(s)
    return s

def create_symptom_entry(db: Session, session_id, mood, symptom, intensity, notes_plain=None, photo_url=None):
    notes_enc = security.encrypt_bytes(notes_plain) if notes_plain else None
    red_flag = True if intensity and intensity >= 8 else False
    e = models.SymptomEntry(session_id=session_id, mood=mood, symptom=symptom, intensity=intensity,
                            notes=notes_enc, photo_url=photo_url, red_flag=red_flag)
    db.add(e); db.commit(); db.refresh(e)
    return e

def create_chat_log(db: Session, session_id, sender, message_plain, intent=None):
    msg_enc = security.encrypt_bytes(message_plain) if message_plain else None
    l = models.ChatLog(session_id=session_id, sender=sender, message=msg_enc, intent=intent)
    db.add(l); db.commit(); db.refresh(l)
    return l

def get_sessions_by_patient(db: Session, patient_id):
    return db.query(models.Session).filter(models.Session.patient_id == patient_id).order_by(models.Session.created_at.desc()).all()

def get_chat_logs(db: Session, session_id):
    return db.query(models.ChatLog).filter(models.ChatLog.session_id == session_id).order_by(models.ChatLog.timestamp.asc()).all()

def create_doctor(db: Session, full_name: str, specialization: str, clinic_name: str, city: str, contact_email: str):
    d = models.Doctor(full_name=full_name, specialization=specialization, clinic_name=clinic_name, city=city, contact_email=contact_email)
    db.add(d); db.commit(); db.refresh(d)
    return d
