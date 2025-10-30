# 🏥 Symptom Tracker v2.0 - FastMCP + LangGraph Edition

A comprehensive healthcare monitoring system powered by **FastMCP (Model Context Protocol)**, **LangGraph**, and **Google Gemini AI**.

## 🌟 New Features in v2.0

### FastMCP Integration (Official MCP Protocol)
- **7 Specialized MCP Tools** using official FastMCP library:
  - `analyze_symptoms_with_ai` - AI-powered symptom analysis with Gemini
  - `check_severity_threshold` - Emergency detection system
  - `find_available_doctor` - Smart doctor matching by location and specialization
  - `save_session_to_database` - Persist symptom sessions
  - `create_appointment` - Automated appointment scheduling
  - `send_appointment_emails` - Email notifications to patients and doctors
  - `get_patient_history` - Retrieve patient medical history
  
- **MCP Protocol Compliant**: Uses stdio transport (standard MCP)
- **Embedded Server**: No separate MCP server process needed
- **Type-Safe Tools**: Proper tool definitions with Python type hints

### LangGraph Workflow
- **State-based Agent**: Multi-step workflow orchestration
- **Intelligent Routing**: Conditional edges based on severity
- **Error Handling**: Comprehensive error recovery nodes
- **Async Processing**: Full async/await support

### Workflow Steps
1. **Analyze Symptoms** → AI analysis with Gemini
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
│   └── fastmcp_server.py     # FastMCP server with 7 tools
├── langgraph_agent/
│   ├── agent_fixed.py         # LangGraph workflow agent
│   └── fastmcp_client.py      # FastMCP client (stdio transport)
├── api/
│   ├── main.py                # FastAPI with FastMCP integration
│   ├── fastmcp_routes.py      # FastMCP-specific routes
│   └── appointment_booking.py # Appointment booking endpoint
├── streamlit_app/
│   └── app_v2.py              # Enhanced Streamlit UI
├── config/
│   └── settings.py            # Configuration management
└── requirements.txt           # Dependencies
```

## 🚀 Installation

### 1. Install Dependencies

```bash
cd symptom_tracker_project/mcp_langgraph_app
pip install fastapi uvicorn streamlit sqlalchemy psycopg2-binary redis python-jose cryptography google-generativeai pydantic-settings requests fastmcp mcp langgraph langchain-google-genai
```

### 2. Configure Environment

Create `.env` file in `symptom_tracker_project/` directory:

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

# App
ENV=development
API_BASE=http://localhost:8000
```

## 🎯 Running the Application

### Simple 2-Step Startup (FastMCP is Embedded!)

**Terminal 1 - FastAPI Backend:**
```bash
cd symptom_tracker_project/mcp_langgraph_app
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Streamlit Frontend:**
```bash
cd symptom_tracker_project/mcp_langgraph_app
streamlit run streamlit_app/app_v2.py
```

**That's it!** FastMCP server runs automatically when needed (no separate process required).

### Access Points
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📡 API Endpoints

### v2.0 Endpoints (FastMCP + LangGraph)

- `POST /api/v2/symptoms/submit` - Submit symptoms via LangGraph workflow
- `GET /api/v2/symptoms/history` - Get patient history via FastMCP tool
- `GET /api/v2/mcp/tools` - List available FastMCP tools
- `POST /api/v2/fastmcp/submit-symptoms` - Direct FastMCP submission
- `POST /api/v1/sessions/book-appointment` - Manual appointment booking

### v1.0 Endpoints (Legacy - Still Available)

- `POST /api/v1/auth/register` - Register patient
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/dashboard/sessions` - Get sessions
- `GET /api/v1/dashboard/session/{id}/details` - Session details

## 🔄 LangGraph Workflow Example

```python
from mcp_langgraph_app.langgraph_agent.agent_fixed import SymptomTrackerAgent
from mcp_langgraph_app.langgraph_agent.fastmcp_client import FastMCPClient
import os

# FastMCP server script path
server_script = os.path.join("mcp_server", "fastmcp_server.py")

# Process symptoms with FastMCP
async with FastMCPClient(server_script) as mcp_client:
    agent = SymptomTrackerAgent(mcp_client)
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

## 🛠️ FastMCP Tools Details

### 1. analyze_symptoms_with_ai
**Purpose**: AI-powered symptom analysis using Google Gemini  
**Input**: symptoms (list), free_text (str)  
**Output**: JSON string with summary, severity (0-10), recommendation, red_flags, suggested_actions, specialization_needed  
**Protocol**: Returns JSON string (MCP compliant)

### 2. check_severity_threshold
**Purpose**: Determine if symptoms require emergency care  
**Input**: severity (float), symptoms (list)  
**Output**: JSON string with emergency status, critical symptoms, recommendation  
**Threshold**: severity >= 8 or any symptom intensity >= 8

### 3. find_available_doctor
**Purpose**: Find doctors by location and specialization using AI  
**Input**: city (str), specialization (str), urgency (str), symptoms (list)  
**Output**: JSON string with doctor details or error message  
**AI-Powered**: Uses Gemini to select best matching doctor

### 4. save_session_to_database
**Purpose**: Persist symptom session to database  
**Input**: patient_id, symptoms, mood, free_text, ai_analysis  
**Output**: JSON string with session_id and save status  
**Encryption**: Encrypts sensitive data with Fernet

### 5. create_appointment
**Purpose**: Create medical appointment  
**Input**: patient_id, doctor_id, session_id, appointment_type, notes  
**Output**: JSON string with appointment details  
**Date Logic**: +1 day for emergency, +3 days for routine

### 6. send_appointment_emails
**Purpose**: Send HTML emails to patient and doctor  
**Input**: patient/doctor details, appointment info, symptoms summary, photo_urls  
**Output**: JSON string with email sending status  
**Features**: Attaches symptom photos to doctor email

### 7. get_patient_history
**Purpose**: Retrieve patient's symptom history  
**Input**: patient_id, limit (int)  
**Output**: JSON string with patient info and session history  
**Decryption**: Decrypts sensitive data for display

## 🎨 Streamlit UI Features

- **Modern Design**: Healthcare-themed with custom CSS
- **Real-time Analysis**: Live AI processing with LangGraph
- **Emergency Alerts**: Animated alerts for severe symptoms
- **Smart Appointment Booking**: User-controlled appointment booking (no auto-booking)
- **Voice Input**: Record symptoms using speech-to-text (NEW!)
- **Enhanced Dashboard**: Comprehensive health insights with visualizations
- **Photo Upload**: Upload symptom photos
- **Separate Pages**: Log Symptoms, Dashboard, and History

### 🎤 Voice Recording Feature (NEW!)

- **Speech-to-Text**: Record symptoms using your voice
- **Google Speech Recognition**: Free, accurate transcription
- **Editable Transcription**: Review and edit before submitting
- **Fallback Option**: Type manually if voice fails
- **Simple Integration**: Uses Streamlit's built-in audio input

### 📊 Enhanced Dashboard (v2.0.1)

**Separate Navigation Pages:**
- 🌡️ **Log Symptoms** - Dedicated symptom logging with voice/text input
- 📊 **Dashboard** - Comprehensive health analytics
- 📋 **History** - Complete session history with details

**Dashboard Features:**
- **Quick Health Summary**: Status, check-ins, alerts at a glance
- **This Month Overview**: Current month statistics with color coding
- **Current Week Trend**: Daily severity chart (Mon-Sun)
- **Trend Interpretation**: AI insights (improving/worsening/stable)
- **Top Symptoms**: Bar chart of most common symptoms
- **Severity Distribution**: Low/Moderate/High breakdown
- **Quick Stats**: Total symptoms, appointments, average mood
- **Personalized Tips**: Context-aware health recommendations

**History Features:**
- **Session Numbering**: Easy tracking (Session #1, #2, etc.)
- **Color-Coded Status**: Red (high), Orange (moderate), Green (normal)
- **Detailed View**: Complete session breakdown with symptoms and chat logs
- **Back Navigation**: Easy return to history list

See [DASHBOARD_FEATURE.md](DASHBOARD_FEATURE.md) for technical details.

## 🔐 Security Features

- JWT authentication with Bearer tokens
- Fernet encryption for sensitive data
- HTTPS-ready configuration
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy ORM
- Encrypted chat logs and symptom notes

## 📊 Database Schema

Uses existing schema from v1.0:
- `patients` - User accounts (encrypted secret_key)
- `doctors` - Healthcare providers
- `sessions` - Symptom logging sessions
- `symptom_entries` - Individual symptoms (encrypted notes)
- `chat_logs` - AI conversation history (encrypted messages)
- `appointments` - Scheduled appointments (encrypted notes)
- `notifications` - Email logs

## 🧪 Testing

### Test FastMCP Tools Directly
```python
from mcp_langgraph_app.langgraph_agent.fastmcp_client import FastMCPClient
import asyncio

async def test_tool():
    async with FastMCPClient("mcp_server/fastmcp_server.py") as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")
        
        # Call a tool
        result = await client.call_tool(
            "check_severity_threshold",
            severity=9.0,
            symptoms=[{"symptom": "Chest Pain", "intensity": 9}]
        )
        print(result)

asyncio.run(test_tool())
```

### Test API Endpoints
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
- **FastMCP Tools**: `GET /api/v2/mcp/tools` - Available tools
- **API Docs**: `GET /docs` - Interactive API documentation

## 🔄 Migration from v1.0

v2.0 is **backward compatible** with v1.0:
- All v1.0 endpoints still work
- Database schema unchanged
- Existing data accessible
- Can run both versions simultaneously

**New in v2.0**:
- Use `/api/v2/symptoms/submit` for LangGraph workflow
- FastMCP tools provide modular functionality
- Enhanced AI analysis with Gemini
- Automatic emergency handling
- No separate MCP server needed

## 🐛 Troubleshooting

### FastMCP Connection Issues
- Ensure Python virtual environment is activated
- Check that `fastmcp` and `mcp` packages are installed
- Verify `fastmcp_server.py` path is correct

### LangGraph Workflow Fails
- Verify Gemini API key is valid
- Check database connection
- Ensure all dependencies installed

### Email Not Sending
- Verify SMTP credentials
- Check Gmail app password
- Ensure SMTP_HOST/PORT correct

## 📚 Documentation

- **FastMCP**: https://github.com/jlowin/fastmcp
- **MCP Protocol**: https://modelcontextprotocol.io/
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **Google Gemini**: https://ai.google.dev/

## 🎯 What's New in FastMCP Implementation

### ✅ Advantages Over Previous Version
1. **Official Protocol**: Uses standard MCP specification
2. **No Separate Server**: Embedded FastMCP (no port 8001 needed)
3. **stdio Transport**: Standard MCP communication method
4. **Type Safety**: Proper Python type hints
5. **Simpler Deployment**: 2 processes instead of 3
6. **Better Error Handling**: MCP protocol error responses
7. **Interoperable**: Works with any MCP-compatible client

### 🔄 Architecture Changes
- **Before**: Custom HTTP server on port 8001
- **After**: FastMCP with stdio transport (embedded)
- **Before**: 3 separate processes (MCP server, API, Streamlit)
- **After**: 2 processes (API with embedded FastMCP, Streamlit)

## 📞 Support

- **Technical Issues**: Check logs in terminal
- **API Documentation**: http://localhost:8000/docs
- **FastMCP Tools**: Use `/api/v2/mcp/tools` endpoint

---

**Version**: 2.0.1  
**Powered by**: FastMCP + LangGraph + Google Gemini AI + Speech Recognition  
**Developed by**: Value Health AI Inc.

## 🆕 Version 2.0.1 Updates

### New Features
- ✅ Voice recording for symptom description
- ✅ Separate navigation pages (Log Symptoms, Dashboard, History)
- ✅ Current week daily severity trend (instead of 4-week)
- ✅ Severity distribution chart
- ✅ Average mood tracking
- ✅ User-controlled appointment booking (no auto-booking)
- ✅ Enhanced dashboard with personalized insights
- ✅ Improved session history with color coding

### Dependencies Added
- `SpeechRecognition` - Voice-to-text conversion
- `PyAudio` - Audio recording support
- `pandas` - Data manipulation for charts

### Bug Fixes
- Fixed timezone handling in dashboard insights
- Fixed session details view navigation
- Improved error handling in API endpoints
