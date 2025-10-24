# 🏥 Symptom Tracker Advanced - AI-Powered Healthcare Monitoring

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)

An advanced healthcare monitoring system with **LangGraph workflow orchestration**, **AI-powered symptom analysis**, **intelligent doctor matching**, and **automated appointment booking**.

## 🌟 Key Features

- 🤖 **LangGraph Workflow**: Stateful multi-node workflow with conditional routing
- 🧠 **AI-Powered Analysis**: Google Gemini 2.5 Flash for symptom severity scoring
- 🏥 **Intelligent Doctor Matching**: LLM-based doctor selection by specialization
- 📅 **Smart Appointment Booking**: User-confirmed emergency appointments
- 📧 **Email Notifications**: Automated emails to patients and doctors
- 🎨 **Modern Dark UI**: Professional healthcare-themed Streamlit interface
- 🔐 **Secure Authentication**: JWT-based auth with encrypted data storage

---

## 📁 Project Structure

```
symptom_tracker_project/
│
├── app/                          # 🔧 SHARED CORE MODULES (Used by v2)
│   ├── api/v1/                   # v1 API endpoints (auth, dashboard)
│   ├── core/                     # Security, encryption, config
│   ├── db/                       # 📊 Database models & session
│   │   ├── models.py            # SQLAlchemy models (Patient, Doctor, etc.)
│   │   └── session.py           # Database connection
│   ├── schemas/                  # Pydantic validation schemas
│   ├── services/                 # Business logic (legacy)
│   └── crud.py                   # 🔄 Database CRUD operations
│
└── mcp_langgraph_app/           # 🚀 V2.0 APPLICATION
    ├── api/
    │   ├── main.py              # FastAPI v2 backend
    │   └── appointment_booking.py  # Manual appointment endpoint
    │
    ├── config/
    │   └── settings.py          # Centralized configuration
    │
    ├── langgraph_agent/         # 🧠 LANGGRAPH WORKFLOW
    │   ├── agent_fixed.py       # 8-node workflow with routing
    │   └── mcp_client.py        # HTTP client for MCP tools
    │
    ├── mcp_server/              # 🛠️ MCP-LIKE TOOL SERVER
    │   └── http_server.py       # 7 tools (AI, doctor, appointments, etc.)
    │
    ├── streamlit_app/           # 🎨 FRONTEND UI
    │   └── app_v2.py            # Dark theme Streamlit interface
    │
    ├── .env.example             # Environment template
    ├── requirements.txt         # Python dependencies
    └── README.md                # This file
```

---

## 🔗 How Folders Are Interconnected

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT UI (app_v2.py)                 │
│                  Dark Theme Healthcare Interface             │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP REST API
┌────────────────────────────▼────────────────────────────────┐
│              FASTAPI BACKEND (main.py)                       │
│         • v2 endpoints (/api/v2/symptoms/submit)            │
│         • v1 auth endpoints (backward compatible)           │
│         • Appointment booking endpoint                      │
└────────────────────────────┬────────────────────────────────┘
                             │ Calls
┌────────────────────────────▼────────────────────────────────┐
│          LANGGRAPH AGENT (agent_fixed.py)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  8 Nodes: analyze → check_severity → find_doctor    │  │
│  │           → save_session → create_appointment        │  │
│  │           → send_emails → complete                   │  │
│  │  Conditional Routing: emergency vs normal paths     │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP Calls
┌────────────────────────────▼────────────────────────────────┐
│         MCP TOOL SERVER (http_server.py)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  7 Tools:                                            │  │
│  │  1. analyze_symptoms_with_ai (Gemini AI)            │  │
│  │  2. check_severity_threshold                         │  │
│  │  3. find_available_doctor (LLM-powered)             │  │
│  │  4. save_session_to_database                         │  │
│  │  5. create_appointment                               │  │
│  │  6. send_appointment_emails                          │  │
│  │  7. get_patient_history                              │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │ Uses
┌────────────────────────────▼────────────────────────────────┐
│              SHARED CORE (app/ folder)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • app/db/models.py - Database models               │  │
│  │  • app/db/session.py - DB connection                │  │
│  │  • app/crud.py - CRUD operations                    │  │
│  │  • app/core/security.py - Encryption                │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   PostgreSQL    │
                    │   (Railway)     │
                    └─────────────────┘
```

---

## 🎯 Why the `app/` Folder Exists

The `app/` folder contains **SHARED CORE MODULES** that are used by the entire v2 application:

### ✅ Used by v2 Components:

| Module | Used By | Purpose |
|--------|---------|---------|
| `app/db/models.py` | MCP Server, LangGraph Agent | Database models (Patient, Doctor, Session, Appointment) |
| `app/db/session.py` | MCP Server, Appointment Booking | Database connection and session management |
| `app/crud.py` | MCP Server | CRUD operations for all database entities |
| `app/core/security.py` | MCP Server | Fernet encryption for sensitive data |
| `app/api/v1/auth.py` | FastAPI v2 Backend | Authentication endpoints (login/register) |

**Without the `app/` folder, v2 would NOT work!** It's the foundation that v2 is built upon.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database (Railway or local)
- Gmail account with app password
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/vaibhav-krishna23/Symptoms-Tracker-Advanced.git
   cd Symptoms-Tracker-Advanced
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   cd mcp_langgraph_app
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Copy example env file
   cp .env.example .env
   
   # Edit .env with your credentials
   nano .env  # or use any text editor
   ```

   Required variables:
   ```env
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   GEMINI_API_KEY=your_gemini_api_key
   SMTP_USER=your_email@gmail.com
   SMTP_PASS=your_app_password
   JWT_SECRET_KEY=your_secret_key
   FERNET_KEY=your_fernet_key
   ```

5. **Setup database**
   ```bash
   python setup_database.py
   ```

---

## 🏃 Running the Application

You need to run **3 services** in separate terminals:

### Terminal 1: MCP Tool Server
```bash
cd mcp_langgraph_app
python mcp_server/http_server.py
```
**Runs on:** `http://localhost:8001`

### Terminal 2: FastAPI Backend
```bash
cd mcp_langgraph_app
uvicorn api.main:app --reload --port 8000
```
**Runs on:** `http://localhost:8000`
**API Docs:** `http://localhost:8000/docs`

### Terminal 3: Streamlit Frontend
```bash
cd mcp_langgraph_app
streamlit run streamlit_app/app_v2.py
```
**Runs on:** `http://localhost:8501`

---

## 📊 Workflow Diagram

```
User Submits Symptoms
         ↓
    [Streamlit UI]
         ↓
   [FastAPI Backend]
         ↓
  [LangGraph Agent]
         ↓
    ┌────────────┐
    │ Analyze    │ → AI analyzes symptoms
    │ Symptoms   │    (Gemini 2.5 Flash)
    └─────┬──────┘
          ↓
    ┌────────────┐
    │ Check      │ → Severity score 0-10
    │ Severity   │
    └─────┬──────┘
          ↓
    Is Emergency? (≥8)
    ├─ YES → Find Doctor (LLM matches specialist)
    │         ↓
    │    Save Session
    │         ↓
    │    User Confirms?
    │    ├─ YES → Create Appointment → Send Emails
    │    └─ NO  → Complete
    │
    └─ NO  → Save Session → Complete
```

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit (Dark Theme UI) |
| **Backend** | FastAPI (Async REST API) |
| **Workflow** | LangGraph (State Management) |
| **AI** | Google Gemini 2.5 Flash |
| **Database** | PostgreSQL (Railway) |
| **Cache** | Redis (Railway) |
| **Auth** | JWT + Fernet Encryption |
| **Email** | Gmail SMTP |

---

## 📝 API Endpoints

### v2 Endpoints (LangGraph)
- `POST /api/v2/symptoms/submit` - Submit symptoms (LangGraph workflow)
- `POST /api/v1/sessions/book-appointment` - Manual appointment booking

### v1 Endpoints (Backward Compatible)
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/dashboard/sessions` - Get user sessions

---

## 🧪 Testing

```bash
# Test appointment booking
cd mcp_langgraph_app
python test_appointment_booking.py
```

---

## 🔒 Security Features

- ✅ JWT-based authentication
- ✅ Fernet encryption for sensitive data
- ✅ Password hashing (SHA256)
- ✅ Environment variable protection
- ✅ Input validation with Pydantic

---

## 📄 License

Developed by **Value Health AI Inc.**

---

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/vaibhav-krishna23/Symptoms-Tracker-Advanced/issues)
- **Medical Emergencies**: Contact emergency services immediately

---

## ⚠️ Medical Disclaimer

This application is for symptom tracking and monitoring purposes only. It does **NOT** replace professional medical advice, diagnosis, or treatment. Always consult healthcare professionals for medical concerns.

---

**Made with ❤️ by Vaibhav Krishna**
