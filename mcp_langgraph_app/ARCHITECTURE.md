# 🏗️ Architecture Documentation - Symptom Tracker v2.0 (FastMCP)

## System Overview

The Symptom Tracker v2.0 uses a modern, modular architecture with:
- **FastMCP (Official Model Context Protocol)** for tool orchestration
- **LangGraph** for stateful AI workflows
- **FastAPI** for REST API
- **Streamlit** for user interface
- **SQLite/PostgreSQL** for data persistence
- **Google Gemini** for AI analysis

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
│                    (streamlit_app/app_v2.py)                │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│                     (api/main.py)                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         LangGraph Agent (agent_fixed.py)             │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │  State Graph with Conditional Routing          │  │  │
│  │  │  - analyze_symptoms                            │  │  │
│  │  │  - check_severity                              │  │  │
│  │  │  - find_doctor (if emergency)                  │  │  │
│  │  │  - save_session                                │  │  │
│  │  │  - create_appointment (if emergency)           │  │  │
│  │  │  - send_emails                                 │  │  │
│  │  │  - complete                                    │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │                        │                              │  │
│  │                        │ FastMCP Tool Calls           │  │
│  │                        ▼                              │  │
│  │         FastMCP Client (fastmcp_client.py)           │  │
│  │         - stdio transport                            │  │
│  │         - spawns subprocess                          │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ stdio (subprocess)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              FastMCP Server (Embedded Process)               │
│              (mcp_server/fastmcp_server.py)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FastMCP Tools (@mcp.tool() decorators):             │  │
│  │  1. analyze_symptoms_with_ai                         │  │
│  │  2. check_severity_threshold                         │  │
│  │  3. find_available_doctor                            │  │
│  │  4. save_session_to_database                         │  │
│  │  5. create_appointment                               │  │
│  │  6. send_appointment_emails                          │  │
│  │  7. get_patient_history                              │  │
│  │                                                       │  │
│  │  Returns: JSON strings (MCP protocol compliant)      │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┬──────────────┐
         │               │               │              │
         ▼               ▼               ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────────┐
│  PostgreSQL  │ │ Google Gemini│ │   SMTP   │ │    Redis     │
│   Database   │ │      AI      │ │  Server  │ │    Cache     │
└──────────────┘ └──────────────┘ └──────────┘ └──────────────┘
```

## Current Architecture (v2.0)

```
3 Processes:
1. MCP Server (run_mcp_server.py)
2. FastAPI Backend (port 8000)
3. Streamlit Frontend (port 8501)

Communication: stdio subprocess (standard MCP protocol)
```

## Component Details

### 1. Streamlit Frontend (`streamlit_app/app_v2.py`)

**Purpose**: User interface for symptom logging and dashboard

**Features**:
- Login/Registration
- Symptom selection with intensity sliders
- Mood tracking
- Real-time AI analysis display
- Emergency alerts with appointment booking
- Health dashboard with history
- Photo upload for symptoms

**Technology**: Streamlit with custom CSS

**Communication**: REST API calls to FastAPI backend

### 2. FastAPI Backend (`api/main.py`)

**Purpose**: REST API server with embedded FastMCP

**Endpoints**:
- `/api/v1/auth/*` - Authentication (login, register)
- `/api/v2/symptoms/submit` - Submit symptoms via LangGraph + FastMCP
- `/api/v2/symptoms/history` - Get patient history via FastMCP
- `/api/v1/sessions/book-appointment` - Manual appointment booking
- `/api/v1/dashboard/*` - Dashboard data
- `/api/v2/mcp/tools` - List FastMCP tools
- `/api/v2/fastmcp/*` - Direct FastMCP routes

**Features**:
- JWT authentication
- Request validation with Pydantic
- CORS middleware
- Error handling
- FastMCP client integration (spawns subprocess)

**FastMCP Integration**:
```python
# Embedded FastMCP - no separate server needed
FASTMCP_SERVER_SCRIPT = os.path.join("mcp_server", "fastmcp_server.py")

async with FastMCPClient(FASTMCP_SERVER_SCRIPT) as mcp_client:
    agent = SymptomTrackerAgent(mcp_client)
    result = await agent.process_symptoms(...)
```

### 3. LangGraph Agent (`langgraph_agent/agent_fixed.py`)

**Purpose**: Stateful workflow orchestration for symptom processing

**State Management**:
```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    patient_id: str
    symptoms: list
    mood: int
    free_text: str
    ai_analysis: dict
    severity_check: dict
    doctor_info: dict
    appointment_info: dict
    email_status: dict
    session_id: str
    error: str
```

**Workflow Nodes**:
1. **analyze_symptoms_node**: Call FastMCP tool for AI analysis
2. **check_severity_node**: Determine emergency status
3. **find_doctor_node**: Find available doctor (emergency only)
4. **save_session_node**: Persist to database
5. **create_appointment_node**: Book appointment (emergency only)
6. **send_emails_node**: Send notifications
7. **complete_node**: Finalize workflow
8. **error_handler_node**: Handle errors

**Conditional Routing**:
```python
check_severity → is_emergency? 
                 ├─ Yes → find_doctor → save_session → create_appointment → send_emails → complete
                 └─ No  → save_session → complete
```

### 4. FastMCP Server (`mcp_server/fastmcp_server.py`)

**Purpose**: Official MCP protocol server using FastMCP library

**Protocol**: Model Context Protocol (MCP) with stdio transport

**Tools** (7 total):

#### Tool 1: analyze_symptoms_with_ai
```python
@mcp.tool()
async def analyze_symptoms_with_ai(symptoms: list[dict], free_text: str) -> str:
    # Returns JSON string (MCP compliant)
    return json.dumps({
        "summary": "...",
        "severity": 5.0,
        "recommendation": "yes/no",
        "red_flags": [...],
        "suggested_actions": [...],
        "specialization_needed": "..."
    })
```
- **Input**: symptoms, free_text
- **Process**: Call Google Gemini API with structured prompt
- **Output**: JSON string with analysis
- **Fallback**: Heuristic analysis if AI fails

#### Tool 2: check_severity_threshold
```python
@mcp.tool()
async def check_severity_threshold(severity: float, symptoms: list[dict]) -> str:
    # Returns JSON string
    return json.dumps({
        "is_emergency": bool,
        "severity_score": float,
        "max_intensity": int,
        "critical_symptoms": [...],
        "recommendation": "...",
        "message": "..."
    })
```
- **Threshold**: severity >= 8 or any symptom intensity >= 8

#### Tool 3: find_available_doctor
```python
@mcp.tool()
async def find_available_doctor(city: str, specialization: str, urgency: str, symptoms: list[dict]) -> str:
    # AI-powered doctor selection
    # Returns JSON string
```
- **AI-Powered**: Uses Gemini to select best matching doctor
- **Fallback**: Returns first available doctor if AI fails

#### Tool 4: save_session_to_database
```python
@mcp.tool()
async def save_session_to_database(patient_id: str, symptoms: list[dict], mood: int, free_text: str, ai_analysis: dict) -> str:
    # Saves session, chat logs, symptom entries
    # Returns JSON string with session_id
```
- **Encryption**: Encrypts chat messages and notes with Fernet

#### Tool 5: create_appointment
```python
@mcp.tool()
async def create_appointment(patient_id: str, doctor_id: str, session_id: str, appointment_type: str, notes: str) -> str:
    # Creates appointment record
    # Returns JSON string with appointment details
```
- **Date Logic**: +1 day for emergency, +3 days for routine

#### Tool 6: send_appointment_emails
```python
@mcp.tool()
async def send_appointment_emails(patient_email: str, patient_name: str, doctor_email: str, doctor_name: str, clinic_name: str, appointment_date: str, symptoms_summary: str, appointment_type: str, photo_urls: list[str]) -> str:
    # Sends HTML emails via SMTP
    # Attaches symptom photos to doctor email
    # Returns JSON string with status
```
- **Features**: Separate emails for patient and doctor, photo attachments

#### Tool 7: get_patient_history
```python
@mcp.tool()
async def get_patient_history(patient_id: str, limit: int) -> str:
    # Retrieves patient sessions and symptoms
    # Returns JSON string with history
```
- **Decryption**: Decrypts sensitive data for display

**MCP Protocol Compliance**:
- All tools return JSON strings (not dicts)
- Uses `@mcp.tool()` decorator
- Proper type hints for parameters
- Runs via `mcp.run()` with stdio transport

### 5. FastMCP Client (`langgraph_agent/fastmcp_client.py`)

**Purpose**: Communication layer between LangGraph and FastMCP server

**Protocol**: stdio transport (spawns subprocess)

**Implementation**:
```python
class FastMCPClient:
    async def __aenter__(self):
        # Start FastMCP server as subprocess
        server_params = StdioServerParameters(
            command=sys.executable,  # Use current Python
            args=[self.server_script_path],
            env=None
        )
        self.client = stdio_client(server_params)
        self.read, self.write = await self.client.__aenter__()
        self.session = ClientSession(self.read, self.write)
        await self.session.initialize()
        return self
    
    async def call_tool(self, tool_name: str, **kwargs):
        # Call MCP tool and parse JSON response
        result = await self.session.call_tool(tool_name, arguments=kwargs)
        text = result.content[0].text
        return json.loads(text)  # Parse JSON string to dict
```

**Features**:
- Spawns FastMCP server as subprocess
- Uses MCP ClientSession for communication
- Parses JSON responses automatically
- Proper cleanup with context manager

### 6. Database Layer

**ORM**: SQLAlchemy 1.4.49

**Tables**:
- `patients`: User accounts (encrypted secret_key)
- `doctors`: Healthcare providers
- `sessions`: Symptom logging sessions (red_flag for emergencies)
- `symptom_entries`: Individual symptoms (encrypted notes)
- `chat_logs`: AI conversations (encrypted messages)
- `appointments`: Scheduled appointments (encrypted notes)
- `notifications`: Email logs

**Encryption**: Fernet symmetric encryption for sensitive data

**Connection**: SQLite (local) or PostgreSQL (cloud)

## Data Flow

### Normal Symptom Submission (Severity < 8)

```
1. User submits symptoms via Streamlit
   ↓
2. POST /api/v2/symptoms/submit
   ↓
3. FastAPI spawns FastMCP subprocess
   ↓
4. LangGraph agent.process_symptoms()
   ↓
5. Node: analyze_symptoms
   → FastMCP Tool: analyze_symptoms_with_ai (via stdio)
   → Google Gemini API call
   → Return: JSON string {"summary": "...", "severity": 5, ...}
   → Client parses JSON to dict
   ↓
6. Node: check_severity
   → FastMCP Tool: check_severity_threshold
   → Return: JSON string {"is_emergency": false, ...}
   ↓
7. Conditional routing → "normal" path
   ↓
8. Node: save_session
   → FastMCP Tool: save_session_to_database
   → Database: INSERT sessions, chat_logs, symptom_entries
   → Return: JSON string {"session_id": "...", ...}
   ↓
9. Node: complete
   → Return workflow summary
   ↓
10. FastMCP subprocess terminates
   ↓
11. API returns result to Streamlit
   ↓
12. Display: AI summary, severity score, recommendations
```

### Emergency Symptom Submission (Severity >= 8)

```
1. User submits severe symptoms via Streamlit
   ↓
2. POST /api/v2/symptoms/submit
   ↓
3. FastAPI spawns FastMCP subprocess
   ↓
4. LangGraph agent.process_symptoms()
   ↓
5. Node: analyze_symptoms
   → FastMCP Tool: analyze_symptoms_with_ai
   → Return: JSON {"severity": 9, "red_flags": [...], ...}
   ↓
6. Node: check_severity
   → FastMCP Tool: check_severity_threshold
   → Return: JSON {"is_emergency": true, ...}
   ↓
7. Conditional routing → "emergency" path
   ↓
8. Node: find_doctor
   → FastMCP Tool: find_available_doctor
   → Database: SELECT doctors WHERE city = patient.city
   → Gemini AI selects best doctor
   → Return: JSON {"doctor_id": "...", ...}
   ↓
9. Node: save_session
   → FastMCP Tool: save_session_to_database
   → Database: INSERT sessions (red_flag=true)
   → Return: JSON {"session_id": "...", ...}
   ↓
10. Node: create_appointment
    → FastMCP Tool: create_appointment
    → Database: INSERT appointments
    → Return: JSON {"appointment_id": "...", ...}
    ↓
11. Node: send_emails
    → FastMCP Tool: send_appointment_emails
    → SMTP: Send HTML emails with photo attachments
    → Return: JSON {"success": true, ...}
    ↓
12. Node: complete
    → Return workflow summary with appointment details
    ↓
13. FastMCP subprocess terminates
    ↓
14. API returns result to Streamlit
    ↓
15. Display: Emergency alert, appointment confirmation
```

## Security Architecture

### Authentication
- **JWT Tokens**: Bearer token authentication
- **Token Expiry**: 1440 minutes (24 hours)
- **Algorithm**: HS256

### Encryption
- **Method**: Fernet symmetric encryption
- **Encrypted Fields**:
  - Patient secret_key
  - Chat log messages
  - Symptom notes
  - Appointment notes

### Data Protection
- **Password Hashing**: SHA256
- **SQL Injection**: Protected by SQLAlchemy ORM
- **CORS**: Configured for specific origins
- **Input Validation**: Pydantic models

## FastMCP vs Custom HTTP MCP

| Feature | Custom HTTP MCP | FastMCP (Current) |
|---------|----------------|-------------------|
| Protocol | Custom HTTP | Official MCP |
| Transport | HTTP (port 8001) | stdio (subprocess) |
| Processes | 3 (MCP, API, UI) | 2 (API+MCP, UI) |
| Tool Returns | Python dicts | JSON strings |
| Interoperability | None | Works with any MCP client |
| Deployment | Separate server | Embedded |
| Startup | Manual | Automatic |
| Standard | Custom | MCP Specification |

## Performance Considerations

### FastMCP Subprocess Model
- **Pros**: 
  - Isolated process per request
  - No shared state issues
  - Clean resource cleanup
- **Cons**: 
  - Subprocess spawn overhead (~100-200ms)
  - Not suitable for high-frequency calls

### Optimization Strategies
1. **Connection Pooling**: Reuse database connections
2. **Caching**: Cache AI responses for identical inputs
3. **Async Processing**: Full async/await throughout
4. **Database Indexes**: On patient_id, session_id, doctor_id

## Deployment Architecture

### Development
```
Local Machine:
- MCP Server: stdio subprocess
- FastAPI: localhost:8000
- Streamlit: localhost:8501
- Database: SQLite (local file)
```

### Production (Recommended)
```
Cloud Infrastructure:
- Load Balancer
  ├─ API Servers (3+ instances with embedded FastMCP)
  └─ Streamlit Servers (2+ instances)
- Database: Managed PostgreSQL (AWS RDS / GCP Cloud SQL)
- Cache: Managed Redis
- Monitoring: CloudWatch / Stackdriver
```

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Streamlit | User interface |
| API | FastAPI | REST API server |
| Workflow | LangGraph | State management |
| MCP | FastMCP | Official MCP protocol |
| Transport | stdio | MCP communication |
| AI | Google Gemini 2.5 Flash | Symptom analysis |
| Database | PostgreSQL | Data persistence |
| Cache | Redis | Session caching |
| ORM | SQLAlchemy | Database abstraction |
| Auth | JWT (python-jose) | Authentication |
| Encryption | Cryptography (Fernet) | Data encryption |
| Email | SMTP (smtplib) | Notifications |
| Validation | Pydantic | Data validation |

## Future Enhancements

### Phase 1: Enhanced AI
- Multi-turn conversations with memory
- Symptom clarification questions
- Treatment plan generation
- Drug interaction checking

### Phase 2: Advanced Features
- Voice input for symptoms
- Image analysis for rashes/wounds
- Wearable device integration
- Telemedicine video calls

### Phase 3: MCP Extensions
- Additional MCP resources (lab results, medications)
- MCP prompts for common scenarios
- MCP sampling for interactive AI
- Multi-agent MCP workflows

### Phase 4: Enterprise Features
- Multi-tenant architecture
- Role-based access control
- Audit logging
- HIPAA compliance reporting

---

**Document Version**: 2.0-fastmcp  
**Last Updated**: 2024  
**Architecture**: FastMCP + LangGraph + FastAPI + Streamlit  
**MCP Protocol**: Official Model Context Protocol (stdio transport)
