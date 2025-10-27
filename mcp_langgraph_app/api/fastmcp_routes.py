"""FastAPI routes using real FastMCP"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db.session import get_db
from mcp_langgraph_app.langgraph_agent.fastmcp_client import FastMCPClient
from mcp_langgraph_app.langgraph_agent.agent_fixed import SymptomTrackerAgent
from mcp_langgraph_app.config.settings import settings
from jose import jwt
import os

router = APIRouter()

def get_patient_id_from_token(authorization: str = Header(None)) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    try:
        scheme, token = authorization.split()
    except:
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    return payload.get("sub")

@router.post("/api/v2/fastmcp/submit-symptoms")
async def submit_symptoms_fastmcp(request: dict, authorization: str = Header(None), db: Session = Depends(get_db)):
    """Submit symptoms using real FastMCP protocol"""
    patient_id = get_patient_id_from_token(authorization)
    
    symptoms = request.get("symptoms", [])
    mood = request.get("mood", 3)
    free_text = request.get("free_text", "")
    
    if not symptoms or not free_text:
        raise HTTPException(status_code=400, detail="Symptoms and description required")
    
    # Use FastMCP
    server_script = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp_server", "fastmcp_server.py")
    
    async with FastMCPClient(server_script) as mcp_client:
        agent = SymptomTrackerAgent(mcp_client)
        result = await agent.process_symptoms(patient_id, symptoms, mood, free_text)
    
    return result

@router.get("/api/v2/fastmcp/tools")
async def list_fastmcp_tools():
    """List available FastMCP tools"""
    server_script = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp_server", "fastmcp_server.py")
    
    async with FastMCPClient(server_script) as mcp_client:
        tools = await mcp_client.list_tools()
    
    return {"tools": [{"name": t.name, "description": t.description} for t in tools]}
