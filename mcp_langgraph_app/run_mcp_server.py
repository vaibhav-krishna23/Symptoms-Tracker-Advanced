"""Script to run the MCP HTTP server"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

if __name__ == "__main__":
    print("🚀 Starting MCP HTTP Server...")
    print("📡 Server will be available at http://localhost:8001")
    print("🛠️  Available tools:")
    print("   - analyze_symptoms_with_ai")
    print("   - find_available_doctor")
    print("   - create_appointment")
    print("   - send_appointment_emails")
    print("   - get_patient_history")
    print("   - save_session_to_database")
    print("   - check_severity_threshold")
    print("\nPress Ctrl+C to stop the server\n")
    
    import uvicorn
    from mcp_langgraph_app.mcp_server.http_server import app
    uvicorn.run(app, host="localhost", port=8001)
