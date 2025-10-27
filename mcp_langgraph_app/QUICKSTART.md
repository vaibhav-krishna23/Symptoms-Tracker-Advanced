# 🚀 Quick Start - Symptom Tracker v2.0

## Prerequisites
- Python 3.11+
- Gmail account with app password
- Google Gemini API key

## Setup (5 minutes)

```bash
# 1. Install dependencies
cd mcp_langgraph_app
pip install -r requirements.txt

# 2. Configure .env (edit with your credentials)
cp .env.example .env

# 3. Add sample doctor
python add_doctor.py
```

## Run (3 Terminals)

**Terminal 1: MCP Server**
```bash
cd mcp_langgraph_app
python run_mcp_server.py
```

**Terminal 2: FastAPI Backend**
```bash
cd mcp_langgraph_app
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 3: Streamlit Frontend**
```bash
cd mcp_langgraph_app
streamlit run streamlit_app/app_v2.py
```

**Access**: http://localhost:8501

## Test Emergency Workflow

1. Register with your city name
2. Log symptoms with intensity ≥ 8 (e.g., Chest Pain: 9)
3. Describe: "Severe chest pain for 30 minutes"
4. Watch LangGraph execute emergency workflow!

## Workflow

**Normal (Severity < 8)**:
```
Analyze → Check Severity → Save → Complete
```

**Emergency (Severity ≥ 8)**:
```
Analyze → Check Severity → Find Doctor → Save → 
Create Appointment → Send Emails → Complete
```

## Troubleshooting

- **Database error**: Check `.env` DATABASE_URL
- **No doctors**: Run `python add_doctor.py`
- **Email fails**: Verify SMTP credentials in `.env`

---

**Ready!** 🎉 Register at http://localhost:8501
