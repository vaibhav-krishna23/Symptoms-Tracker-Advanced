# Changelog

All notable changes to the Symptom Tracker project will be documented in this file.

## [2.0.0] - 2024

### 🎉 Major Release - Real MCP + LangGraph Architecture

#### Added
- **FastMCP Integration**: Migrated to official Model Context Protocol (MCP) using `fastmcp` library
- **stdio Transport**: Standard MCP communication via subprocess (replaces HTTP)
- **Embedded MCP Server**: No separate server process needed - FastMCP runs on-demand
- **7 MCP Tools**: All tools now return JSON strings (MCP protocol compliant)
  - `analyze_symptoms_with_ai`
  - `check_severity_threshold`
  - `find_available_doctor`
  - `save_session_to_database`
  - `create_appointment`
  - `send_appointment_emails`
  - `get_patient_history`
- **FastMCP Client**: New client using `mcp.ClientSession` with stdio transport
- **Type-Safe Tools**: Proper Python type hints for all tool parameters
- **Automatic Subprocess Management**: FastMCP server spawns and terminates automatically

#### Changed
- **Architecture**: Reduced from 3 processes to 2 (API+FastMCP, Streamlit)
- **Tool Returns**: Changed from Python dicts to JSON strings (MCP standard)
- **Client Communication**: Changed from HTTP requests to stdio subprocess
- **Server Startup**: Changed from manual `python run_mcp_server.py` to automatic embedding
- **Python Executable**: Client now uses `sys.executable` for correct virtual environment

#### Removed
- **http_server.py**: Deleted custom HTTP MCP server (replaced by FastMCP)
- **Old MCPClient**: Removed HTTP-based MCP client
- **Port 8001**: No longer need separate MCP server port
- **Manual MCP Server**: No need to run `python run_mcp_server.py`

#### Fixed
- **Connection Issues**: Resolved "Connection closed" errors with proper stdio transport
- **JSON Parsing**: Fixed tool response parsing (JSON strings → dicts)
- **Subprocess Spawning**: Fixed Python path issues in virtual environments
- **Appointment Booking**: Updated to use FastMCP instead of old HTTP client

### 📝 Migration Guide

#### v2.0 Setup (3 Terminals)
```bash
# Terminal 1: MCP Server
python run_mcp_server.py

# Terminal 2: FastAPI Backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Streamlit Frontend
streamlit run streamlit_app/app_v2.py
```

### 🔧 Technical Details

#### FastMCP Server (`mcp_server/fastmcp_server.py`)
- Uses `@mcp.tool()` decorators
- Returns JSON strings via `json.dumps()`
- Runs with `mcp.run()` entry point
- stdio transport (standard MCP)

#### FastMCP Client (`langgraph_agent/fastmcp_client.py`)
- Uses `StdioServerParameters` for subprocess
- Uses `ClientSession` for MCP communication
- Parses JSON responses automatically
- Proper cleanup with context manager

#### API Integration (`api/main.py`)
```python
# Old way (HTTP)
mcp_client = MCPClient("http://localhost:8001")
result = await mcp_client.call_tool("analyze_symptoms", ...)

# New way (FastMCP)
async with FastMCPClient("mcp_server/fastmcp_server.py") as mcp_client:
    result = await mcp_client.call_tool("analyze_symptoms", ...)
```

### 📊 Performance Impact

- **Architecture**: Real MCP protocol with stdio transport
- **Database**: SQLite support for local development
- **Deployment**: Simplified with 3 clear processes
- **Documentation**: Cleaned up, removed Docker files

### 🔒 Security

- No changes to encryption or authentication
- Same JWT and Fernet encryption
- stdio transport is more secure than HTTP (no network exposure)

### 🐛 Known Issues

None currently identified.

### 📚 Documentation Updates

- Updated `README.md` with FastMCP instructions
- Updated `ARCHITECTURE.md` with new architecture diagrams
- Added this `CHANGELOG.md` for version tracking

---

## [1.0.0] - 2024

### Initial Release

#### Features
- Custom HTTP-based MCP server
- LangGraph workflow for symptom processing
- Google Gemini AI integration
- PostgreSQL database with encryption
- Streamlit user interface
- Email notifications
- Appointment booking system
- 7 MCP tools for healthcare operations

#### Components
- FastAPI backend
- Custom MCP HTTP server (port 8001)
- Streamlit frontend
- PostgreSQL database (Railway)
- Redis cache (Railway)

---

## Version Numbering

- **Major**: Breaking changes (e.g., 1.0 → 2.0)
- **Minor**: New features, backward compatible (e.g., 2.0 → 2.1)
- **Patch**: Bug fixes (e.g., 2.0.0 → 2.0.1)
- **Suffix**: Special releases (e.g., -fastmcp, -beta)
