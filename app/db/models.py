"""Initialization or Placeholder File."""
# app/db/models.py
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, BYTEA, TIMESTAMP
import uuid
from app.db.session import Base
import sqlalchemy as sa
from datetime import datetime

class Patient(Base):
    __tablename__ = "patients"
    patient_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True)
    password_hash = Column(String(255))
    secret_key_encrypted = Column(BYTEA)
    city = Column(String(100))
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Doctor(Base):
    __tablename__ = "doctors"
    doctor_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(100), nullable=False)
    specialization = Column(String(100))
    clinic_name = Column(String(150))
    city = Column(String(100))
    contact_email = Column(String(120))
    contact_number = Column(String(20))
    available_slots = Column(JSON)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

class Session(Base):
    __tablename__ = "sessions"
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.patient_id", ondelete="CASCADE"))
    start_time = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    end_time = Column(TIMESTAMP(timezone=True))
    severity_score = Column(sa.Numeric(3,1))
    red_flag = Column(Boolean, default=False)
    callback_required = Column(Boolean, default=False)
    ai_summary = Column(Text)
    summary_sent_to = Column(String(20))
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

class ChatLog(Base):
    __tablename__ = "chat_logs"
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.session_id", ondelete="CASCADE"))
    sender = Column(String(10))
    message = Column(BYTEA)
    timestamp = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    intent = Column(String(100))

class SymptomEntry(Base):
    __tablename__ = "symptom_entries"
    entry_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.session_id", ondelete="CASCADE"))
    date = Column(DateTime, default=datetime.utcnow)
    mood = Column(Integer)
    symptom = Column(String(100))
    intensity = Column(Integer)
    notes = Column(BYTEA)
    photo_url = Column(Text)
    red_flag = Column(Boolean, default=False)

class Appointment(Base):
    __tablename__ = "appointments"
    appointment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.patient_id", ondelete="CASCADE"))
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.doctor_id", ondelete="CASCADE"))
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.session_id"))
    appointment_date = Column(TIMESTAMP(timezone=True))
    status = Column(String(30), default="pending")
    clinic_location = Column(String(200))
    notes = Column(BYTEA)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    notification_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipient_type = Column(String(20))
    recipient_id = Column(UUID(as_uuid=True))
    channel = Column(String(30))
    message = Column(BYTEA)
    sent_time = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    status = Column(String(30), default="sent")

class PatientDoctorHistory(Base):
    __tablename__ = "patient_doctor_history"
    pd_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.patient_id", ondelete="CASCADE"))
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.doctor_id", ondelete="CASCADE"))
    relationship_type = Column(String(10), default="past")
    last_appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.appointment_id"))
    notes = Column(BYTEA)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
