# 🚀 Quick Start Guide - Symptom Tracker v2.0-fastmcp

## ⚡ TL;DR - Get Running in 2 Minutes

### 1. Install Dependencies
```bash
cd symptom_tracker_project/mcp_langgraph_app
pip install fastapi uvicorn streamlit sqlalchemy psycopg2-binary redis python-jose cryptography google-generativeai pydantic-settings requests fastmcp mcp langgraph langchain-google-genai
```

### 2. Configure Environment
Create `.env` file in `symptom_tracker_project/` with:
```env
DATABASE_URL=your_postgresql_url
GEMINI_API_KEY=your_gemini_key
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
JWT_SECRET_KEY=your_secret
FERNET_KEY=your_fernet_key
```

### 3. Run Application (2 Terminals)

**Terminal 1:**
```bash
cd symptom_tracker_project/mcp_langgraph_app
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2:**
```bash
cd symptom_tracker_project/mcp_langgraph_app
streamlit run streamlit_app/app_v2.py
```

### 4. Access
- **Frontend**: http://localhost:8501
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs

---

## 📋 What's New in v2.0-fastmcp

✅ **FastMCP** - Official Model Context Protocol  
✅ **2 Processes** - Down from 3 (no separate MCP server)  
✅ **stdio Transport** - Standard MCP communication  
✅ **Embedded Server** - FastMCP spawns automatically  

---

## 🔧 Git Commit Commands

```bash
cd symptom_tracker_project
git add .
git commit -m "feat: Migrate to FastMCP (Official Model Context Protocol)

- Implemented FastMCP with stdio transport
- Removed custom HTTP MCP server
- Updated all documentation
- Reduced from 3 to 2 processes

Version: 2.0.0-fastmcp"
git push origin main
```

---

## 📚 Full Documentation

- **README**: `mcp_langgraph_app/README.md`
- **Architecture**: `mcp_langgraph_app/ARCHITECTURE.md`
- **Changelog**: `mcp_langgraph_app/CHANGELOG.md`
- **Commit Guide**: `mcp_langgraph_app/COMMIT_GUIDE.md`
- **Migration Summary**: `mcp_langgraph_app/FASTMCP_MIGRATION_SUMMARY.md`

---

**Version**: 2.0.0-fastmcp  
**Status**: ✅ Production Ready
