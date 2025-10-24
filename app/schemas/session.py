"""Initialization or Placeholder File."""
# app/schemas/session.py
from pydantic import BaseModel
from typing import List
from datetime import datetime

class SymptomItem(BaseModel):
    symptom: str
    intensity: int
    notes: str | None = None
    photo_url: str | None = None

class SessionCreate(BaseModel):
    mood: int
    symptoms: List[SymptomItem]
    free_text: str
