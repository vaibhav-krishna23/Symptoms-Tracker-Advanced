"""Initialization or Placeholder File."""
# app/services/ai_processor.py
import google.generativeai as genai
from app.core.config import settings
import logging
import json

genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_summary_structured(free_text: str, symptoms: list) -> dict:
    """
    Returns a dict: {"summary": str, "severity": float, "recommendation": "yes"/"no"}
    Uses Gemini model to produce JSON output. Falls back to heuristic on error.
    """
    items = "\n".join([f"- {s['symptom']} (intensity {s['intensity']})" for s in symptoms])
    prompt = f"""
You are an assistant for a medical symptom-tracker. Input:
Symptoms:
{items}

Additional notes:
{free_text}

Produce a JSON object only with fields:
- summary (<=120 chars)
- severity (0-10 numeric)
- recommendation ("yes" or "no") where "yes" means patient should book an appointment.

Return JSON only.
"""
    try:
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = model.generate_content(prompt)
        text = response.text.strip()
        # try to parse JSON
        try:
            parsed = json.loads(text)
            return parsed
        except Exception:
            # attempt to extract JSON-like substring
            import re
            m = re.search(r'\{.*\}', text, re.S)
            if m:
                try:
                    return json.loads(m.group(0))
                except Exception:
                    logging.exception("Failed parse extracted JSON")
            logging.info("Gemini gave non-JSON: %s", text)
    except Exception as e:
        logging.exception("Gemini API failed: %s", e)

    # fallback heuristic
    max_int = max([s.get("intensity", 0) for s in symptoms]) if symptoms else 0
    summary = f"Reported symptoms with max intensity {max_int}. {free_text[:120]}"
    rec = "yes" if max_int >= 8 else "no"
    return {"summary": summary, "severity": float(max_int), "recommendation": rec}
