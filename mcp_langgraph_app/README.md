# 🏥 Symptom Tracker v2.0 - MCP + LangGraph Edition

A comprehensive healthcare monitoring system powered by **Model Context Protocol (MCP)**, **LangGraph**, and **Google Gemini AI**.

## 🌟 New Features in v2.0

### MCP Integration (FastMCP)
- **8 Specialized MCP Tools**:
  - `analyze_symptoms_with_ai` - AI-powered symptom analysis with Gemini
  - `find_available_doctor` - Smart doctor matching by location and specialization
  - `create_appointment` - Automated appointment scheduling
  - `send_appointment_emails` - Email notifications to patients and doctors
  - `get_patient_history` - Retrieve patient medical history
  - `save_session_to_database` - Persist symptom sessions
  - `check_severity_threshold` - Emergency detection system
  
- **MCP Resources**: Patient data accessible via `patient://{patient_id}` URI
- **MCP Prompts**: Pre-configured symptom analysis prompts

### LangGraph Workflow
- **State-based Agent**: Multi-step workflow with checkpointing
- **Intelligent Routing**: Conditional edges based on severity
- **Conversation Memory**: SQLite-based checkpoint system
- **Error Handling**: Comprehensive error recovery nodes

### Workflow Steps
1. **Analyze Symptoms** → AI analysis with patient history
2. **Check Severity** → Emergency threshold detection
3. **Route Decision** → Emergency vs Normal path
4. **Find Doctor** (if emergency) → Location-based matching
5. **Save Session** → Database persistence
6. **Create Appointment** (if emergency) → Automated booking
7. **Send Emails** → Notifications to patient and doctor
8. **Complete** → Workflow summary

## 🏗️ Architecture

```
mcp_langgraph_app/
├── mcp_server/
│   └── tools.py              # FastMCP tools (8 tools + resources)
├── langgraph_agent/
│   ├── agent.py              # LangGraph workflow agent
│   └── mcp_client.py         # MCP client for tool calls
├── api/
│   └── main.py               # FastAPI with MCP + LangGraph
├── streamlit_app/
│   └── app_v2.py             # Enhanced Streamlit UI
├── config/
│   └── settings.py           # Configuration management
└── requirements.txt          # Dependencies
```

## 🚀 Installation

### 1. Install Dependencies

```bash
cd c:\symptom_tracker_project\symptom_tracker_project\mcp_langgraph_app
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env` from parent directory or create new one:

```env
# Database
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# Security
FERNET_KEY=your_fernet_key
JWT_SECRET_KEY=your_jwt_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password

# MCP Server
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8001

# LangGraph
LANGGRAPH_CHECKPOINT_DB=checkpoints.db
```

## 🎯 Running the Application

### Option 1: Run All Services (Recommended)

**Terminal 1 - MCP Server:**
```bash
cd c:\symptom_tracker_project\symptom_tracker_project\mcp_langgraph_app
python run_mcp_server.py
```

**Terminal 2 - FastAPI Backend:**
```bash
cd c:\symptom_tracker_project\symptom_tracker_project\mcp_langgraph_app
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 3 - Streamlit Frontend:**
```bash
cd c:\symptom_tracker_project\symptom_tracker_project\mcp_langgraph_app
streamlit run streamlit_app/app_v2.py
```

### Option 2: Test MCP Tools Directly

```python
from mcp_langgraph_app.langgraph_agent.mcp_client import SyncMCPClient

client = SyncMCPClient("http://localhost:8001")

# Test symptom analysis
result = client.call_tool(
    "analyze_symptoms_with_ai",
    symptoms=[{"symptom": "Headache", "intensity": 8}],
    free_text="Severe headache for 2 days"
)
print(result)
```

## 📡 API Endpoints

### v2.0 Endpoints (MCP + LangGraph)

- `POST /api/v2/symptoms/submit` - Submit symptoms via LangGraph workflow
- `GET /api/v2/symptoms/history` - Get patient history via MCP tool
- `GET /api/v2/mcp/tools` - List available MCP tools

### v1.0 Endpoints (Legacy - Still Available)

- `POST /api/v1/auth/register` - Register patient
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/dashboard/sessions` - Get sessions
- `GET /api/v1/dashboard/session/{id}/details` - Session details

## 🔄 LangGraph Workflow Example

```python
from mcp_langgraph_app.langgraph_agent.agent import SymptomTrackerAgent
from mcp_langgraph_app.langgraph_agent.mcp_client import MCPClient

# Initialize
mcp_client = MCPClient("http://localhost:8001")
agent = SymptomTrackerAgent(mcp_client)

# Process symptoms
result = await agent.process_symptoms(
    patient_id="uuid-here",
    symptoms=[
        {"symptom": "Chest Pain", "intensity": 9},
        {"symptom": "Shortness of Breath", "intensity": 8}
    ],
    mood=2,
    free_text="Severe chest pain and difficulty breathing"
)

# Result includes:
# - AI analysis
# - Severity check
# - Doctor info (if emergency)
# - Appointment details (if booked)
# - Email status
# - Complete workflow messages
```

## 🛠️ MCP Tools Details

### 1. analyze_symptoms_with_ai
**Purpose**: AI-powered symptom analysis using Google Gemini  
**Input**: symptoms (list), free_text (str), patient_history (optional)  
**Output**: summary, severity (0-10), recommendation, red_flags, suggested_actions, specialization_needed

### 2. find_available_doctor
**Purpose**: Find doctors by location and specialization  
**Input**: city (str), specialization (optional), urgency (str)  
**Output**: doctor details or error message

### 3. create_appointment
**Purpose**: Create medical appointment  
**Input**: patient_id, doctor_id, session_id, appointment_type, notes  
**Output**: appointment details with confirmation

### 4. send_appointment_emails
**Purpose**: Send HTML emails to patient and doctor  
**Input**: patient/doctor details, appointment info, symptoms summary  
**Output**: email sending status

### 5. get_patient_history
**Purpose**: Retrieve patient's symptom history  
**Input**: patient_id, limit (int)  
**Output**: patient info and session history

### 6. save_session_to_database
**Purpose**: Persist symptom session to database  
**Input**: patient_id, symptoms, mood, free_text, ai_analysis  
**Output**: session_id and save status

### 7. check_severity_threshold
**Purpose**: Determine if symptoms require emergency care  
**Input**: severity (float), symptoms (list)  
**Output**: emergency status, critical symptoms, recommendation

## 🎨 Streamlit UI Features

- **Modern Design**: Healthcare-themed with custom CSS
- **Real-time Analysis**: Live AI processing with LangGraph
- **Workflow Visualization**: View LangGraph execution steps
- **Emergency Alerts**: Animated alerts for severe symptoms
- **Appointment Tracking**: Complete appointment management
- **History Dashboard**: Comprehensive health history view

## 🔐 Security Features

- JWT authentication with Bearer tokens
- Fernet encryption for sensitive data
- HTTPS-ready configuration
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy ORM

## 📊 Database Schema

Uses existing schema from v1.0:
- `patients` - User accounts
- `doctors` - Healthcare providers
- `sessions` - Symptom logging sessions
- `symptom_entries` - Individual symptoms
- `chat_logs` - AI conversation history
- `appointments` - Scheduled appointments
- `notifications` - Email logs

## 🧪 Testing

### Test MCP Server
```bash
# List available tools
curl http://localhost:8001/tools

# Call a tool
curl -X POST http://localhost:8001/tools/check_severity_threshold \
  -H "Content-Type: application/json" \
  -d '{"severity": 9, "symptoms": [{"symptom": "Chest Pain", "intensity": 9}]}'
```

### Test LangGraph Workflow
```bash
# Submit symptoms via v2 API
curl -X POST http://localhost:8000/api/v2/symptoms/submit \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": [{"symptom": "Fever", "intensity": 8}],
    "mood": 3,
    "free_text": "High fever for 2 days"
  }'
```

## 📈 Monitoring

- **Health Check**: `GET /health` - System status
- **MCP Tools**: `GET /api/v2/mcp/tools` - Available tools
- **Workflow Logs**: Included in API responses

## 🔄 Migration from v1.0

v2.0 is **backward compatible** with v1.0:
- All v1.0 endpoints still work
- Database schema unchanged
- Existing data accessible
- Can run both versions simultaneously

**New in v2.0**:
- Use `/api/v2/symptoms/submit` for LangGraph workflow
- MCP tools provide modular functionality
- Enhanced AI analysis with patient history
- Automatic emergency handling

## 🐛 Troubleshooting

### MCP Server Not Starting
- Check port 8001 is available
- Verify database connection in `.env`
- Ensure all dependencies installed

### LangGraph Workflow Fails
- Check MCP server is running
- Verify Gemini API key is valid
- Check `checkpoints.db` permissions

### Email Not Sending
- Verify SMTP credentials
- Check Gmail app password
- Ensure SMTP_HOST/PORT correct

## 📚 Documentation

- **FastMCP**: https://github.com/jlowin/fastmcp
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **Google Gemini**: https://ai.google.dev/

## 🎯 Next Steps

1. **Add More MCP Tools**:
   - Medication tracking
   - Lab results integration
   - Telemedicine scheduling

2. **Enhance LangGraph**:
   - Multi-turn conversations
   - Symptom clarification questions
   - Treatment plan generation

3. **Advanced Features**:
   - Voice input for symptoms
   - Image analysis for rashes
   - Wearable device integration

## 📞 Support

- **Technical Issues**: Check logs in terminal
- **API Documentation**: http://localhost:8000/docs
- **MCP Tools**: http://localhost:8001/tools

---

**Version**: 2.0.0  
**Powered by**: MCP + LangGraph + Google Gemini AI  
**Developed by**: Value Health Inc.
