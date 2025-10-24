"""Initialization or Placeholder File."""
# app/schemas/patient.py
from pydantic import BaseModel, EmailStr

class PatientCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    secret_key: str
    city: str | None = None

class PatientLogin(BaseModel):
    email: EmailStr
    password: str
    secret_key: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
