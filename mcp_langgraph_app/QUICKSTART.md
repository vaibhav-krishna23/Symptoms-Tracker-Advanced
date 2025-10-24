# 🚀 Quick Start Guide - Symptom Tracker v2.0

## Prerequisites
- Python 3.11+
- PostgreSQL database (already configured)
- Gmail account with app password
- Google Gemini API key

## Step-by-Step Setup

### 1. Install Dependencies (5 minutes)

```bash
cd c:\symptom_tracker_project\symptom_tracker_project\mcp_langgraph_app
pip install -r requirements.txt
```

### 2. Verify Environment Variables

Check that `.env` file exists in parent directory with:
```env
DATABASE_URL=postgresql://...
GEMINI_API_KEY=your_key
SMTP_USER=your_email
SMTP_PASS=your_app_password
```

### 3. Add Sample Doctor (Required for Emergency Appointments)

Open a Python shell:
```python
import sys
sys.path.append('c:/symptom_tracker_project/symptom_tracker_project')

from app.db.session import SessionLocal
from app import crud

db = SessionLocal()
doctor = crud.create_doctor(
    db,
    full_name="Dr. Sarah Johnson",
    specialization="General Practitioner",
    clinic_name="City Health Clinic",
    city="New York",  # Use your city
    contact_email="doctor@example.com"
)
print(f"Doctor created: {doctor.doctor_id}")
db.close()
```

### 4. Start the Services

**Terminal 1 - MCP Server:**
```bash
cd c:\symptom_tracker_project\symptom_tracker_project\mcp_langgraph_app
python run_mcp_server.py
```
Wait for: "🚀 Starting MCP Server..."

**Terminal 2 - FastAPI Backend:**
```bash
cd c:\symptom_tracker_project\symptom_tracker_project\mcp_langgraph_app
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
Wait for: "Application startup complete"

**Terminal 3 - Streamlit Frontend:**
```bash
cd c:\symptom_tracker_project\symptom_tracker_project\mcp_langgraph_app
streamlit run streamlit_app/app_v2.py
```
Browser opens automatically at http://localhost:8501

### 5. Test the Application

1. **Register**: Create account with email, password, secret_key, and city
2. **Login**: Use your credentials
3. **Log Symptoms**: 
   - Select symptoms (try "Chest Pain" with intensity 9 for emergency test)
   - Describe symptoms
   - Click "Submit & Analyze with AI"
4. **View Results**: See AI analysis, severity score, and workflow steps
5. **Check Dashboard**: View your symptom history

## 🎯 Testing Emergency Workflow

To test the complete MCP + LangGraph emergency workflow:

1. Log symptoms with **intensity ≥ 8**:
   - Chest Pain: 9
   - Shortness of Breath: 8

2. Describe: "Severe chest pain and difficulty breathing for 30 minutes"

3. Expected workflow:
   - ✅ AI analyzes symptoms
   - ✅ Detects emergency (severity ≥ 8)
   - ✅ Finds available doctor in your city
   - ✅ Creates emergency appointment
   - ✅ Sends emails to patient and doctor
   - ✅ Displays appointment confirmation

## 🔍 Verify Everything Works

### Check MCP Server
```bash
curl http://localhost:8001/tools
```
Should return list of 7 tools

### Check FastAPI
```bash
curl http://localhost:8000/health
```
Should return: `{"status": "healthy"}`

### Check API Documentation
Open: http://localhost:8000/docs

## 📊 Understanding the Workflow

### Normal Symptoms (Severity < 8)
```
User Input → AI Analysis → Severity Check → Save to DB → Complete
```

### Emergency Symptoms (Severity ≥ 8)
```
User Input → AI Analysis → Severity Check → Find Doctor → 
Save to DB → Create Appointment → Send Emails → Complete
```

## 🛠️ Common Issues

### Issue: MCP Server won't start
**Solution**: Check database connection in `.env`

### Issue: "No doctors available"
**Solution**: Add a doctor using Step 3 above

### Issue: Emails not sending
**Solution**: Verify SMTP credentials in `.env`

### Issue: Import errors
**Solution**: Run from correct directory:
```bash
cd c:\symptom_tracker_project\symptom_tracker_project\mcp_langgraph_app
```

## 📱 Access Points

- **Frontend**: http://localhost:8501
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MCP Server**: http://localhost:8001

## 🎓 Next Steps

1. **Explore MCP Tools**: Check http://localhost:8000/api/v2/mcp/tools
2. **View Workflow**: Submit symptoms and check "Workflow Execution Log"
3. **Test Dashboard**: View your symptom history
4. **Try Different Severities**: Test both normal and emergency cases

## 💡 Pro Tips

- Use **intensity 8-10** to trigger emergency workflow
- Check terminal logs to see LangGraph execution
- View `checkpoints.db` for conversation history
- API docs at `/docs` show all available endpoints

## 🆘 Need Help?

1. Check terminal logs for errors
2. Verify all 3 services are running
3. Ensure database is accessible
4. Confirm Gemini API key is valid

---

**Ready to go!** 🎉 Start by registering a new account at http://localhost:8501
