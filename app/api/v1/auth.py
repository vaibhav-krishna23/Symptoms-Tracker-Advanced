"""Initialization or Placeholder File."""
# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app import crud
from app.schemas.patient import PatientCreate, PatientLogin, Token
from jose import jwt
from app.core.config import settings
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=dict)
def register(payload: PatientCreate, db: Session = Depends(get_db)):
    existing = crud.get_patient_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    p = crud.create_patient(db, payload.full_name, payload.email, payload.password, payload.secret_key, payload.city)
    return {"patient_id": str(p.patient_id)}

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded

@router.post("/login", response_model=Token)
def login(payload: PatientLogin, db: Session = Depends(get_db)):
    user = crud.verify_patient_credentials(db, payload.email, payload.password, payload.secret_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.patient_id)})
    return {"access_token": token, "token_type": "bearer"}
