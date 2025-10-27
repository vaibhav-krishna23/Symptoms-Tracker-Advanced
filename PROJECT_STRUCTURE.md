# 📁 Symptom Tracker - Complete Project Structure

## 🏗️ Architecture Overview

```
symptom_tracker_project/
├── app/                          # Shared Core Application (v1 + v2)
├── mcp_langgraph_app/           # v2 Application (MCP + LangGraph)
├── Docker Files                  # Deployment configurations
└── Documentation                 # Project guides
```

---

## 📂 Detailed File Structure

```
symptom_tracker_project/
│
├── app/                                    # 🔧 SHARED CORE MODULES
│   ├── __init__.py                        # Package initializer
│   ├── crud.py                            # Database CRUD operations
│   │
│   ├── core/                              # Core utilities
│   │   ├── __init__.py
│   │   ├── config.py                      # Configuration settings
│   │   └── security.py                    # Fernet encryption, password hashing
│   │
│   ├── db/                                # Database layer
│   │   ├── __init__.py
│   │   ├── models.py                      # SQLAlchemy models (Patient, Doctor, Session, etc.)
│   │   └── session.py                     # Database session management
│   │
│   └── schemas/                           # Pydantic schemas
│       ├── __init__.py
│       └── patient.py                     # Patient validation schemas
│
├── mcp_langgraph_app/                     # 🚀 V2 APPLICATION (MAIN)
│   │
│   ├── api/                               # FastAPI Backend
│   │   ├── __init__.py
│   │   ├── main.py                        # Main FastAPI app, routes, endpoints
│   │   ├── appointment_booking.py         # Manual appointment booking endpoint
│   │   └── fastmcp_routes.py             # Real FastMCP protocol routes
│   │
│   ├── config/                            # Configuration
│   │   ├── __init__.py
│   │   └── settings.py                    # Environment variables, settings
│   │
│   ├── langgraph_agent/                   # LangGraph Workflow
│   │   ├── __init__.py
│   │   ├── agent_fixed.py                 # LangGraph agent with workflow nodes
│   │   ├── mcp_client.py                  # HTTP MCP client (custom)
│   │   └── fastmcp_client.py             # Real FastMCP client (stdio)
│   │
│   ├── mcp_server/                        # MCP Tool Servers
│   │   ├── __init__.py
│   │   ├── http_server.py                 # Custom HTTP MCP server (default)
│   │   └── fastmcp_server.py             # Real FastMCP server (official protocol)
│   │
│   ├── streamlit_app/                     # Streamlit Frontend
│   │   ├── __init__.py
│   │   ├── app_v2.py                      # Main Streamlit UI
│   │   ├── api_client.py                  # API communication client
│   │   ├── components_auth.py             # Login/Register components
│   │   ├── components_dashboard.py        # Dashboard UI components
│   │   └── components_symptom_logging.py  # Symptom logging UI
│   │
│   ├── uploads/                           # File uploads
│   │   └── symptom_photos/               # Patient symptom images
│   │
│   ├── requirements.txt                   # Python dependencies
│   ├── run_mcp_server.py                 # Script to run MCP HTTP server
│   └── checkpoints.db                    # LangGraph conversation checkpoints
│
├── Dockerfile.mcp                         # 🐳 Docker image for MCP Server
├── Dockerfile.api                         # 🐳 Docker image for FastAPI
├── Dockerfile.web                         # 🐳 Docker image for Streamlit
├── docker-compose.yml                     # Docker Compose orchestration
├── .dockerignore                          # Docker ignore patterns
│
├── build-and-push.bat                     # 📦 Windows script to build/push Docker images
├── build-and-push.sh                      # 📦 Linux/Mac script to build/push Docker images
│
├── .env                                   # 🔐 Environment variables (NOT in git)
├── .env.example                           # 🔐 Example environment file
├── .gitignore                             # Git ignore patterns
│
├── README.md                              # 📖 Main project documentation
├── PROJECT_STRUCTURE.md                   # 📖 This file - project structure
├── DOCKER_DEPLOYMENT.md                   # 📖 Docker deployment guide
├── RAILWAY_DEPLOYMENT.md                  # 📖 Railway deployment guide
├── deploy-railway.md                      # 📖 Quick Railway deployment
└── MCP_IMPLEMENTATION.md                  # 📖 MCP implementation comparison
```

---

## 📄 File Descriptions

### 🔧 **app/** - Shared Core Modules

#### **crud.py**
- Database CRUD operations
- Functions: `create_patient()`, `create_doctor()`, `create_session()`, etc.
- Used by both v1 and v2 applications

#### **core/config.py**
- Loads environment variables
- Database URL, API keys, SMTP settings
- Singleton settings object

#### **core/security.py**
- **Fernet encryption** for sensitive data (notes, messages)
- **SHA256 password hashing**
- Functions: `encrypt_bytes()`, `decrypt_bytes()`, `hash_password()`

#### **db/models.py**
- SQLAlchemy ORM models
- Tables: `Patient`, `Doctor`, `Session`, `SymptomEntry`, `Appointment`, `ChatLog`, `Notification`
- Relationships and foreign keys

#### **db/session.py**
- Database session management
- Connection pooling
- `SessionLocal()` factory

#### **schemas/patient.py**
- Pydantic validation schemas
- `PatientCreate`, `PatientLogin`, `Token`
- Input validation and serialization

---

### 🚀 **mcp_langgraph_app/** - V2 Application

#### **api/main.py** (FastAPI Backend)
- Main FastAPI application
- REST API endpoints:
  - `/api/v1/auth/register` - User registration
  - `/api/v1/auth/login` - User login
  - `/api/v2/symptoms/submit` - Submit symptoms (HTTP MCP)
  - `/api/v2/fastmcp/submit-symptoms` - Submit symptoms (Real FastMCP)
  - `/api/v1/upload/symptom-photo` - Upload photos
  - `/api/v1/dashboard/*` - Dashboard endpoints
- CORS middleware
- Static file serving for uploads
- JWT authentication

#### **api/appointment_booking.py**
- Manual appointment booking endpoint
- Used when user clicks "Book Appointment" button
- Calls MCP tools for doctor matching and email sending
- Passes symptom photos to email tool

#### **api/fastmcp_routes.py**
- Real FastMCP protocol routes
- Alternative to HTTP MCP
- Uses stdio transport
- Compatible with Claude Desktop

#### **config/settings.py**
- Pydantic settings management
- Loads from `.env` file
- Environment variables:
  - `DATABASE_URL`, `GEMINI_API_KEY`, `SMTP_*`, `FERNET_KEY`, `JWT_SECRET_KEY`

#### **langgraph_agent/agent_fixed.py**
- LangGraph workflow orchestration
- Nodes:
  - `analyze_symptoms_node` - AI analysis
  - `check_severity_node` - Emergency detection
  - `find_doctor_node` - Doctor matching
  - `save_session_node` - Database storage
  - `create_appointment_node` - Appointment creation
  - `send_emails_node` - Email notifications
- Conditional routing based on severity

#### **langgraph_agent/mcp_client.py**
- HTTP client for custom MCP server
- Makes POST requests to `http://localhost:8001/tools/*`
- Used by default

#### **langgraph_agent/fastmcp_client.py**
- Real FastMCP client using stdio transport
- Follows official MCP specification
- Context manager for session handling

#### **mcp_server/http_server.py** (Default MCP Server)
- Custom FastAPI-based MCP server
- 7 tools:
  1. `analyze_symptoms_with_ai` - Gemini AI analysis
  2. `check_severity_threshold` - Emergency detection
  3. `find_available_doctor` - AI-powered doctor matching
  4. `save_session_to_database` - Session storage
  5. `create_appointment` - Appointment creation
  6. `send_appointment_emails` - Email with photo attachments
  7. `get_patient_history` - Patient history retrieval
- Runs on port 8001

#### **mcp_server/fastmcp_server.py** (Real MCP Server)
- Official FastMCP implementation
- Same 7 tools as HTTP server
- Uses stdio transport
- Compatible with Claude Desktop
- Follows MCP protocol specification

#### **streamlit_app/app_v2.py**
- Main Streamlit UI
- Dark theme healthcare design
- Pages:
  - Login/Register
  - Symptom Logging
  - Dashboard
  - Session Details
- Photo upload functionality
- Real-time AI analysis display

#### **streamlit_app/api_client.py**
- HTTP client for FastAPI backend
- Functions: `register()`, `login()`, `submit_symptoms()`, `upload_photo()`
- JWT token management

#### **streamlit_app/components_auth.py**
- Login and registration UI components
- Form validation
- Session state management

#### **streamlit_app/components_dashboard.py**
- Dashboard UI components
- Session history display
- Severity indicators
- Red flag alerts

#### **streamlit_app/components_symptom_logging.py**
- Symptom selection interface
- Intensity sliders (0-10)
- Mood rating
- Free text description
- Photo upload section

#### **run_mcp_server.py**
- Script to start HTTP MCP server
- Runs `uvicorn mcp_server.http_server:app`
- Port 8001

---

### 🐳 **Docker Files**

#### **Dockerfile.mcp**
- Docker image for MCP Server
- Base: `python:3.11-slim`
- Exposes port 8001
- CMD: `python run_mcp_server.py`

#### **Dockerfile.api**
- Docker image for FastAPI Backend
- Creates uploads directory
- Exposes port 8000
- CMD: `uvicorn api.main:app`

#### **Dockerfile.web**
- Docker image for Streamlit Frontend
- Exposes port 8501
- CMD: `streamlit run app_v2.py`

#### **docker-compose.yml**
- Orchestrates all 3 services
- Network: `symptom-network`
- Volume: `uploads` (persistent storage)
- Environment variables from `.env`

#### **.dockerignore**
- Excludes unnecessary files from Docker images
- Patterns: `__pycache__`, `.git`, `.env`, `*.db`, `uploads/`

---

### 📦 **Build Scripts**

#### **build-and-push.bat** (Windows)
- Builds 3 Docker images
- Tags with Docker Hub username
- Pushes to Docker Hub
- Usage: `build-and-push.bat`

#### **build-and-push.sh** (Linux/Mac)
- Same as .bat but for Unix systems
- Make executable: `chmod +x build-and-push.sh`

---

### 🔐 **Configuration Files**

#### **.env**
- Environment variables (NOT committed to git)
- Contains sensitive data:
  - Database credentials
  - API keys
  - SMTP passwords
  - Encryption keys

#### **.env.example**
- Template for `.env` file
- Shows required variables
- Safe to commit to git

#### **.gitignore**
- Git ignore patterns
- Excludes: `.env`, `__pycache__`, `*.db`, `uploads/`, `venv/`

---

### 📖 **Documentation Files**

#### **README.md**
- Main project documentation
- Features, tech stack, installation
- Quick start guide
- Usage instructions

#### **PROJECT_STRUCTURE.md** (This file)
- Complete project structure
- File descriptions
- Architecture overview

#### **DOCKER_DEPLOYMENT.md**
- Docker deployment guide
- Build and push instructions
- Environment variables
- Deployment to various platforms

#### **RAILWAY_DEPLOYMENT.md**
- Railway deployment guide
- Step-by-step instructions
- Environment variable setup
- Troubleshooting

#### **deploy-railway.md**
- Quick Railway deployment reference
- Condensed instructions
- Key generation commands

#### **MCP_IMPLEMENTATION.md**
- Comparison of HTTP MCP vs Real FastMCP
- Implementation differences
- Use cases and recommendations
- Claude Desktop integration

---

## 🔄 Data Flow

### Symptom Submission Flow:

```
User (Streamlit) 
    ↓ [HTTP POST]
FastAPI Backend (/api/v2/symptoms/submit)
    ↓ [Calls]
LangGraph Agent (agent_fixed.py)
    ↓ [Uses]
MCP Client (mcp_client.py)
    ↓ [HTTP POST]
MCP Server (http_server.py)
    ↓ [Executes Tools]
    ├─→ Gemini AI (analyze_symptoms_with_ai)
    ├─→ Database (save_session_to_database)
    ├─→ Doctor Matching (find_available_doctor)
    ├─→ Email Service (send_appointment_emails)
    └─→ Returns Results
    ↓
LangGraph Agent (processes workflow)
    ↓
FastAPI Backend (returns response)
    ↓
Streamlit UI (displays results)
```

### Photo Upload Flow:

```
User uploads photo (Streamlit)
    ↓
POST /api/v1/upload/symptom-photo
    ↓
FastAPI saves to uploads/symptom_photos/
    ↓
Returns photo URL
    ↓
URL stored in symptom_entries.photo_url
    ↓
When booking appointment:
    ↓
Photo URL passed to send_appointment_emails tool
    ↓
Email tool reads file from disk
    ↓
Attaches to doctor's email as MIME attachment
```

---

## 🗄️ Database Schema

### Tables:

1. **patients** - User accounts
2. **doctors** - Healthcare providers
3. **sessions** - Symptom logging sessions
4. **symptom_entries** - Individual symptoms with photos
5. **appointments** - Scheduled appointments
6. **chat_logs** - Conversation history
7. **notifications** - Email notifications

### Key Relationships:

- Patient → Sessions (1:N)
- Session → Symptoms (1:N)
- Session → Appointment (1:1)
- Patient → Appointments (1:N)
- Doctor → Appointments (1:N)

---

## 🔑 Key Technologies

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: Streamlit
- **AI**: Google Gemini 2.5 Flash
- **Workflow**: LangGraph
- **Tools**: MCP (Model Context Protocol)
- **Security**: Fernet encryption, JWT
- **Email**: SMTP (Gmail)
- **Deployment**: Docker, Railway, Render

---

## 🚀 Deployment

### Docker Images:
- `vaibhav547/symptom-tracker-mcp:latest`
- `vaibhav547/symptom-tracker-api:latest`
- `vaibhav547/symptom-tracker-web:latest`

### Platforms:
- Railway
- Render
- Fly.io
- DigitalOcean
- AWS ECS

---

## 📊 Project Statistics

- **Total Files**: ~50+
- **Lines of Code**: ~5,000+
- **Docker Images**: 3
- **API Endpoints**: 15+
- **MCP Tools**: 7
- **Database Tables**: 7

---

## 🔗 Important Links

- **GitHub**: https://github.com/vaibhav-krishna23/Symptoms-Tracker-Advanced
- **Docker Hub**: https://hub.docker.com/u/vaibhav547

---

**Last Updated**: January 2025
**Version**: 2.0 (MCP + LangGraph + FastMCP)
