# 🏗️ Architecture Documentation - Symptom Tracker v2.0

## System Overview

The Symptom Tracker v2.0 is built on a modern, modular architecture combining:
- **MCP (Model Context Protocol)** for tool orchestration
- **LangGraph** for stateful AI workflows
- **FastAPI** for REST API
- **Streamlit** for user interface
- **PostgreSQL** for data persistence
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
│  │         LangGraph Agent (agent.py)                    │  │
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
│  │                        │ MCP Tool Calls               │  │
│  │                        ▼                              │  │
│  │         MCP Client (mcp_client.py)                    │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server (FastMCP)                      │
│                  (mcp_server/tools.py)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  MCP Tools:                                           │  │
│  │  1. analyze_symptoms_with_ai                         │  │
│  │  2. find_available_doctor                            │  │
│  │  3. create_appointment                               │  │
│  │  4. send_appointment_emails                          │  │
│  │  5. get_patient_history                              │  │
│  │  6. save_session_to_database                         │  │
│  │  7. check_severity_threshold                         │  │
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

## Component Details

### 1. Streamlit Frontend (`streamlit_app/app_v2.py`)

**Purpose**: User interface for symptom logging and dashboard

**Features**:
- Login/Registration
- Symptom selection with intensity sliders
- Mood tracking
- Real-time AI analysis display
- Emergency alerts
- Appointment confirmation
- Health dashboard with history

**Technology**: Streamlit with custom CSS

**Communication**: REST API calls to FastAPI backend

### 2. FastAPI Backend (`api/main.py`)

**Purpose**: REST API server and orchestration layer

**Endpoints**:
- `/api/v1/auth/*` - Authentication (login, register)
- `/api/v2/symptoms/submit` - Submit symptoms via LangGraph
- `/api/v2/symptoms/history` - Get patient history via MCP
- `/api/v1/dashboard/*` - Dashboard data
- `/api/v2/mcp/tools` - List MCP tools

**Features**:
- JWT authentication
- Request validation with Pydantic
- CORS middleware
- Error handling
- Integration with LangGraph agent

### 3. LangGraph Agent (`langgraph_agent/agent.py`)

**Purpose**: Stateful workflow orchestration for symptom processing

**State Management**:
```python
class AgentState(TypedDict):
    messages: List[BaseMessage]
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
    next_action: str
    error: str
```

**Workflow Nodes**:
1. **analyze_symptoms_node**: Call MCP tool for AI analysis
2. **check_severity_node**: Determine emergency status
3. **find_doctor_node**: Find available doctor (emergency only)
4. **save_session_node**: Persist to database
5. **create_appointment_node**: Book appointment (emergency only)
6. **send_emails_node**: Send notifications
7. **complete_node**: Finalize workflow
8. **error_handler_node**: Handle errors

**Conditional Routing**:
```python
check_severity → emergency? → find_doctor → save_session → create_appointment
                           ↓
                         normal → save_session → complete
```

**Checkpointing**: SQLite-based conversation memory

### 4. MCP Server (`mcp_server/tools.py`)

**Purpose**: Modular tool server using FastMCP

**Tools**:

#### Tool 1: analyze_symptoms_with_ai
- **Input**: symptoms, free_text, patient_history
- **Process**: Call Google Gemini API with structured prompt
- **Output**: summary, severity, recommendation, red_flags, suggested_actions, specialization_needed
- **Fallback**: Heuristic analysis if AI fails

#### Tool 2: find_available_doctor
- **Input**: city, specialization, urgency
- **Process**: Query database for matching doctors
- **Output**: doctor details or error
- **Logic**: Try specialization first, fallback to any doctor in city

#### Tool 3: create_appointment
- **Input**: patient_id, doctor_id, session_id, appointment_type, notes
- **Process**: Create appointment record, encrypt notes
- **Output**: appointment details with confirmation
- **Date Logic**: +1 day for emergency, +3 days for routine

#### Tool 4: send_appointment_emails
- **Input**: patient/doctor details, appointment info, symptoms summary
- **Process**: Generate HTML emails, send via SMTP
- **Output**: email sending status
- **Features**: Separate emails for patient and doctor, emergency styling

#### Tool 5: get_patient_history
- **Input**: patient_id, limit
- **Process**: Query sessions and symptoms
- **Output**: patient info and session history
- **Decryption**: Decrypt sensitive data for display

#### Tool 6: save_session_to_database
- **Input**: patient_id, symptoms, mood, free_text, ai_analysis
- **Process**: Create session, chat logs, symptom entries
- **Output**: session_id and status
- **Encryption**: Encrypt chat messages and notes

#### Tool 7: check_severity_threshold
- **Input**: severity, symptoms
- **Process**: Evaluate emergency criteria
- **Output**: emergency status, critical symptoms, recommendation
- **Threshold**: severity >= 8 or any symptom intensity >= 8

**Resources**:
- `patient://{patient_id}` - Patient information resource

**Prompts**:
- `symptom_analysis_prompt` - Template for AI analysis

### 5. MCP Client (`langgraph_agent/mcp_client.py`)

**Purpose**: Communication layer between LangGraph and MCP server

**Classes**:
- `MCPClient`: Async client for LangGraph
- `SyncMCPClient`: Sync client for testing

**Methods**:
- `call_tool(tool_name, **kwargs)`: Execute MCP tool
- `list_tools()`: Get available tools
- `get_resource(uri)`: Fetch resource

**Error Handling**: Graceful degradation with error messages

### 6. Database Layer

**ORM**: SQLAlchemy 1.4.49

**Tables**:
- `patients`: User accounts (encrypted secret_key)
- `doctors`: Healthcare providers
- `sessions`: Symptom logging sessions
- `symptom_entries`: Individual symptoms (encrypted notes)
- `chat_logs`: AI conversations (encrypted messages)
- `appointments`: Scheduled appointments (encrypted notes)
- `notifications`: Email logs (encrypted messages)
- `patient_doctor_history`: Relationship tracking

**Encryption**: Fernet symmetric encryption for sensitive data

**Connection Pooling**: SQLAlchemy engine with connection pool

## Data Flow

### Normal Symptom Submission (Severity < 8)

```
1. User submits symptoms via Streamlit
   ↓
2. POST /api/v2/symptoms/submit
   ↓
3. LangGraph agent.process_symptoms()
   ↓
4. Node: analyze_symptoms
   → MCP Tool: analyze_symptoms_with_ai
   → Google Gemini API call
   → Return: {summary, severity: 5, recommendation: "no"}
   ↓
5. Node: check_severity
   → MCP Tool: check_severity_threshold
   → Return: {is_emergency: false}
   ↓
6. Conditional routing → "normal" path
   ↓
7. Node: save_session
   → MCP Tool: save_session_to_database
   → Database: INSERT sessions, chat_logs, symptom_entries
   → Return: {session_id}
   ↓
8. Node: complete
   → Return workflow summary
   ↓
9. API returns result to Streamlit
   ↓
10. Display: AI summary, severity score, recommendations
```

### Emergency Symptom Submission (Severity >= 8)

```
1. User submits severe symptoms via Streamlit
   ↓
2. POST /api/v2/symptoms/submit
   ↓
3. LangGraph agent.process_symptoms()
   ↓
4. Node: analyze_symptoms
   → MCP Tool: analyze_symptoms_with_ai
   → Google Gemini API call
   → Return: {summary, severity: 9, recommendation: "yes", red_flags: [...]}
   ↓
5. Node: check_severity
   → MCP Tool: check_severity_threshold
   → Return: {is_emergency: true, critical_symptoms: [...]}
   ↓
6. Conditional routing → "emergency" path
   ↓
7. Node: find_doctor
   → MCP Tool: find_available_doctor
   → Database: SELECT doctors WHERE city = patient.city
   → Return: {doctor_id, full_name, clinic_name}
   ↓
8. Node: save_session
   → MCP Tool: save_session_to_database
   → Database: INSERT sessions (red_flag=true), chat_logs, symptom_entries
   → Return: {session_id}
   ↓
9. Conditional routing → "create_appointment"
   ↓
10. Node: create_appointment
    → MCP Tool: create_appointment
    → Database: INSERT appointments
    → Return: {appointment_id, appointment_date}
    ↓
11. Node: send_emails
    → MCP Tool: send_appointment_emails
    → SMTP: Send HTML emails to patient and doctor
    → Return: {patient_email_sent: true, doctor_email_sent: true}
    ↓
12. Node: complete
    → Return workflow summary with appointment details
    ↓
13. API returns result to Streamlit
    ↓
14. Display: Emergency alert, AI summary, appointment confirmation
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
  - Notification messages

### Data Protection
- **Password Hashing**: SHA256
- **SQL Injection**: Protected by SQLAlchemy ORM
- **CORS**: Configured for specific origins
- **Input Validation**: Pydantic models

## Scalability Considerations

### Current Architecture
- **Single Server**: All components on one machine
- **Synchronous Processing**: Sequential workflow execution
- **SQLite Checkpoints**: Local file-based storage

### Scaling Options

#### Horizontal Scaling
- **Load Balancer**: Distribute requests across multiple API servers
- **MCP Server Cluster**: Multiple MCP servers behind load balancer
- **Database Replication**: Read replicas for dashboard queries

#### Vertical Scaling
- **Async Processing**: Convert to fully async workflow
- **Connection Pooling**: Increase database connection pool
- **Caching**: Redis for frequently accessed data

#### Distributed Architecture
- **Message Queue**: RabbitMQ/Kafka for async task processing
- **Microservices**: Separate services for auth, symptoms, appointments
- **Distributed Checkpoints**: PostgreSQL-based LangGraph checkpoints

## Monitoring & Observability

### Logging
- **FastAPI**: Uvicorn access logs
- **MCP Server**: Tool execution logs
- **LangGraph**: Workflow step logs
- **Database**: SQLAlchemy query logs (debug mode)

### Metrics
- **API Response Times**: Track endpoint latency
- **MCP Tool Performance**: Monitor tool execution time
- **Workflow Success Rate**: Track completion vs errors
- **Database Queries**: Monitor slow queries

### Health Checks
- `/health`: API health status
- Database connectivity check
- MCP server availability
- Gemini API status

## Error Handling

### LangGraph Error Recovery
- **Error Handler Node**: Catches workflow exceptions
- **Graceful Degradation**: Continue with partial results
- **User Feedback**: Clear error messages

### MCP Tool Errors
- **Fallback Logic**: Heuristic analysis if AI fails
- **Retry Mechanism**: Retry failed tool calls
- **Error Propagation**: Return structured error responses

### API Error Responses
- **HTTP Status Codes**: Proper status codes (401, 404, 500)
- **Error Details**: Descriptive error messages
- **Validation Errors**: Pydantic validation feedback

## Performance Optimization

### Database
- **Indexes**: On patient_id, session_id, doctor_id
- **Query Optimization**: Eager loading for relationships
- **Connection Pooling**: Reuse database connections

### AI Processing
- **Prompt Optimization**: Concise prompts for faster responses
- **Caching**: Cache AI responses for identical inputs
- **Streaming**: Stream AI responses for real-time feedback

### Frontend
- **Lazy Loading**: Load dashboard data on demand
- **Caching**: Browser cache for static assets
- **Compression**: Gzip compression for API responses

## Deployment Architecture

### Development
```
Local Machine:
- MCP Server: localhost:8001
- FastAPI: localhost:8000
- Streamlit: localhost:8501
- PostgreSQL: Railway (cloud)
- Redis: Railway (cloud)
```

### Production (Recommended)
```
Cloud Infrastructure:
- Load Balancer (AWS ALB / GCP Load Balancer)
  ├─ API Servers (3+ instances)
  ├─ MCP Servers (2+ instances)
  └─ Streamlit Servers (2+ instances)
- Database: Managed PostgreSQL (AWS RDS / GCP Cloud SQL)
- Cache: Managed Redis (AWS ElastiCache / GCP Memorystore)
- Storage: S3 / GCS for checkpoints
- Monitoring: CloudWatch / Stackdriver
```

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Streamlit | User interface |
| API | FastAPI | REST API server |
| Workflow | LangGraph | State management |
| Tools | FastMCP | Tool orchestration |
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
- Multi-turn conversations
- Symptom clarification questions
- Treatment plan generation
- Drug interaction checking

### Phase 2: Advanced Features
- Voice input for symptoms
- Image analysis for rashes
- Wearable device integration
- Telemedicine video calls

### Phase 3: Enterprise Features
- Multi-tenant architecture
- Role-based access control
- Audit logging
- Compliance reporting (HIPAA)

### Phase 4: Analytics
- Predictive health analytics
- Population health insights
- Outbreak detection
- Treatment effectiveness tracking

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Architecture**: MCP + LangGraph + FastAPI + Streamlit
