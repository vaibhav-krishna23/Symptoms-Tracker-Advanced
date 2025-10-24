"""Initialization or Placeholder File."""
# app/schemas/appointment.py
from pydantic import BaseModel
from datetime import datetime

class AppointmentCreate(BaseModel):
    patient_id: str
    doctor_id: str
    session_id: str | None = None
    appointment_date: datetime
    clinic_location: str
