"""Fixed LangGraph Agent for Symptom Tracker with MCP Integration"""
from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
import operator
import json
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from mcp_langgraph_app.config.settings import settings


class AgentState(TypedDict):
    """State for the symptom tracker agent."""
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


class SymptomTrackerAgent:
    """LangGraph-based agent for symptom tracking workflow."""
    
    def __init__(self, mcp_client):
        """
        Initialize the agent with MCP client.
        
        Args:
            mcp_client: MCP client instance for tool calls
        """
        self.mcp_client = mcp_client
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7
        )
        
        # Build the graph without checkpointer
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_symptoms", self.analyze_symptoms_node)
        workflow.add_node("check_severity", self.check_severity_node)
        workflow.add_node("save_session", self.save_session_node)
        workflow.add_node("find_doctor", self.find_doctor_node)
        workflow.add_node("create_appointment", self.create_appointment_node)
        workflow.add_node("send_emails", self.send_emails_node)
        workflow.add_node("complete", self.complete_node)
        workflow.add_node("error_handler", self.error_handler_node)
        
        # Set entry point
        workflow.set_entry_point("analyze_symptoms")
        
        # Add edges
        workflow.add_edge("analyze_symptoms", "check_severity")
        workflow.add_conditional_edges(
            "check_severity",
            self.route_after_severity_check,
            {
                "emergency": "find_doctor",
                "normal": "save_session"
            }
        )
        workflow.add_edge("save_session", "complete")
        workflow.add_edge("find_doctor", "save_session")
        workflow.add_conditional_edges(
            "save_session",
            self.route_after_save,
            {
                "create_appointment": "create_appointment",
                "complete": "complete",
                "error": "error_handler"
            }
        )
        workflow.add_edge("create_appointment", "send_emails")
        workflow.add_edge("send_emails", "complete")
        workflow.add_edge("complete", END)
        workflow.add_edge("error_handler", END)
        
        return workflow.compile()
    
    async def analyze_symptoms_node(self, state: AgentState) -> dict:
        """Node: Analyze symptoms using AI via MCP."""
        try:
            # Analyze current symptoms only (no history)
            analysis_result = await self.mcp_client.call_tool(
                "analyze_symptoms_with_ai",
                symptoms=state["symptoms"],
                free_text=state["free_text"]
            )
            
            return {
                "ai_analysis": analysis_result,
                "messages": [AIMessage(content=f"AI Analysis Complete: {analysis_result.get('summary', '')}")]
            }
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    async def check_severity_node(self, state: AgentState) -> dict:
        """Node: Check severity threshold."""
        try:
            severity = state["ai_analysis"].get("severity", 0)
            
            severity_result = await self.mcp_client.call_tool(
                "check_severity_threshold",
                severity=severity,
                symptoms=state["symptoms"]
            )
            
            return {
                "severity_check": severity_result,
                "messages": [AIMessage(content=f"Severity Check: {severity_result.get('message', '')}")]
            }
            
        except Exception as e:
            return {"error": f"Severity check failed: {str(e)}"}
    
    def route_after_severity_check(self, state: AgentState) -> Literal["emergency", "normal"]:
        """Route based on severity check."""
        if state["severity_check"].get("is_emergency", False):
            return "emergency"
        return "normal"
    
    async def find_doctor_node(self, state: AgentState) -> dict:
        """Node: Find available doctor for emergency."""
        try:
            # Get patient info to find city
            from app.db.session import SessionLocal
            from app.db import models
            
            db = SessionLocal()
            patient = db.query(models.Patient).filter(
                models.Patient.patient_id == state["patient_id"]
            ).first()
            db.close()
            
            if not patient:
                return {"error": "Patient not found"}
            
            specialization = state["ai_analysis"].get("specialization_needed", "General Practitioner")
            
            doctor_result = await self.mcp_client.call_tool(
                "find_available_doctor",
                city=patient.city,
                specialization=specialization,
                urgency="emergency"
            )
            
            msg = f"Found doctor: Dr. {doctor_result.get('full_name', '')} at {doctor_result.get('clinic_name', '')}" if doctor_result.get("success") else f"Doctor search: {doctor_result.get('error', 'No doctors available')}"
            
            return {
                "doctor_info": doctor_result,
                "messages": [AIMessage(content=msg)]
            }
            
        except Exception as e:
            return {"error": f"Doctor search failed: {str(e)}"}
    
    async def save_session_node(self, state: AgentState) -> dict:
        """Node: Save session to database."""
        try:
            save_result = await self.mcp_client.call_tool(
                "save_session_to_database",
                patient_id=state["patient_id"],
                symptoms=state["symptoms"],
                mood=state["mood"],
                free_text=state["free_text"],
                ai_analysis=state["ai_analysis"]
            )
            
            if save_result.get("success"):
                return {
                    "session_id": save_result.get("session_id", ""),
                    "messages": [AIMessage(content=f"Session saved successfully. ID: {save_result.get('session_id', '')}")]
                }
            else:
                return {"error": save_result.get("error", "Failed to save session")}
            
        except Exception as e:
            return {"error": f"Save session failed: {str(e)}"}
    
    def route_after_save(self, state: AgentState) -> Literal["create_appointment", "complete", "error"]:
        """Route after saving session."""
        if state.get("error"):
            return "error"
        
        # If emergency and doctor found, create appointment automatically
        if (state["severity_check"].get("is_emergency", False) and 
            state.get("doctor_info", {}).get("success", False)):
            return "create_appointment"
        
        return "complete"
    
    async def create_appointment_node(self, state: AgentState) -> dict:
        """Node: Create appointment."""
        try:
            appointment_result = await self.mcp_client.call_tool(
                "create_appointment",
                patient_id=state["patient_id"],
                doctor_id=state["doctor_info"]["doctor_id"],
                session_id=state["session_id"],
                appointment_type="emergency",
                notes=state["ai_analysis"].get("summary", "")
            )
            
            msg = f"Appointment created: {appointment_result.get('appointment_date', '')}" if appointment_result.get("success") else f"Appointment creation failed: {appointment_result.get('error', '')}"
            
            return {
                "appointment_info": appointment_result,
                "messages": [AIMessage(content=msg)]
            }
            
        except Exception as e:
            return {"error": f"Appointment creation failed: {str(e)}"}
    
    async def send_emails_node(self, state: AgentState) -> dict:
        """Node: Send email notifications."""
        try:
            if not state.get("appointment_info", {}).get("success"):
                return {"messages": [AIMessage(content="No appointment to send emails for")]}
            
            apt_info = state["appointment_info"]
            
            # Get chat logs for summary
            from app.db.session import SessionLocal
            from app import crud
            from app.core.security import decrypt_bytes
            
            db = SessionLocal()
            logs = crud.get_chat_logs(db, state["session_id"])
            
            chat_summary = ""
            for log in logs:
                if log.sender == "patient":
                    chat_summary += f"Patient: {decrypt_bytes(log.message)}\n"
                elif log.sender == "bot":
                    chat_summary += f"AI: {decrypt_bytes(log.message)}\n"
            db.close()
            
            if not chat_summary:
                chat_summary = state["ai_analysis"].get("summary", "Severe symptoms requiring immediate attention")
            
            # Extract photo URLs from symptoms
            photo_urls = [s.get("photo_url") for s in state["symptoms"] if s.get("photo_url")]
            
            email_result = await self.mcp_client.call_tool(
                "send_appointment_emails",
                patient_email=apt_info["patient_email"],
                patient_name=apt_info["patient_name"],
                doctor_email=apt_info["doctor_email"],
                doctor_name=apt_info["doctor_name"],
                clinic_name=apt_info["clinic_location"],
                appointment_date=apt_info["appointment_date"],
                symptoms_summary=chat_summary,
                appointment_type="emergency",
                photo_urls=photo_urls
            )
            
            msg = "Email notifications sent successfully to patient and doctor." if email_result.get("success") else f"Email sending failed: {email_result.get('error', '')}"
            
            return {
                "email_status": email_result,
                "messages": [AIMessage(content=msg)]
            }
            
        except Exception as e:
            return {"error": f"Email sending failed: {str(e)}"}
    
    async def complete_node(self, state: AgentState) -> dict:
        """Node: Complete the workflow."""
        summary_parts = [
            "✅ Symptom tracking completed!",
            f"\n📊 Severity: {state['ai_analysis'].get('severity', 0)}/10",
            f"\n📝 Summary: {state['ai_analysis'].get('summary', '')}",
        ]
        
        if state["severity_check"].get("is_emergency"):
            summary_parts.append("\n⚠️ Emergency case detected!")
            
            if state.get("appointment_info", {}).get("success"):
                apt = state["appointment_info"]
                summary_parts.append(f"\n🏥 Appointment scheduled with Dr. {apt.get('doctor_name', '')}")
                summary_parts.append(f"\n📍 Location: {apt.get('clinic_location', '')}")
                summary_parts.append(f"\n📅 Date: {apt.get('appointment_date', '')}")
                
                if state.get("email_status", {}).get("success"):
                    summary_parts.append("\n📧 Confirmation emails sent")
        
        return {"messages": [AIMessage(content="".join(summary_parts))]}
    
    async def error_handler_node(self, state: AgentState) -> dict:
        """Node: Handle errors."""
        error_msg = f"❌ Error occurred: {state.get('error', 'Unknown error')}"
        return {"messages": [AIMessage(content=error_msg)]}
    
    async def process_symptoms(
        self,
        patient_id: str,
        symptoms: list,
        mood: int,
        free_text: str,
        thread_id: str = None
    ) -> dict:
        """
        Process patient symptoms through the LangGraph workflow.
        
        Args:
            patient_id: Patient UUID
            symptoms: List of symptom dictionaries
            mood: Mood rating (1-5)
            free_text: Patient's description
            thread_id: Optional thread ID for conversation continuity
        
        Returns:
            Dictionary with workflow results
        """
        initial_state = {
            "messages": [
                SystemMessage(content="You are a medical symptom tracking assistant."),
                HumanMessage(content=f"Patient reporting symptoms: {free_text}")
            ],
            "patient_id": patient_id,
            "symptoms": symptoms,
            "mood": mood,
            "free_text": free_text,
            "ai_analysis": {},
            "severity_check": {},
            "doctor_info": {},
            "appointment_info": {},
            "email_status": {},
            "session_id": "",
            "error": ""
        }
        
        try:
            final_state = await self.graph.ainvoke(initial_state)
            
            return {
                "success": not bool(final_state.get("error")),
                "session_id": final_state.get("session_id", ""),
                "ai_analysis": final_state.get("ai_analysis", {}),
                "severity_check": final_state.get("severity_check", {}),
                "doctor_info": final_state.get("doctor_info", {}),
                "appointment_info": final_state.get("appointment_info", {}),
                "email_status": final_state.get("email_status", {}),
                "messages": [msg.content for msg in final_state["messages"]],
                "error": final_state.get("error", "")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "messages": [f"Workflow failed: {str(e)}"]
            }