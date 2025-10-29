"""Script to run the FastMCP server"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

if __name__ == "__main__":
    print("🚀 Starting FastMCP Server...")
    print("🛠️  Available tools:")
    print("   - analyze_symptoms_with_ai")
    print("   - check_severity_threshold")
    print("   - find_available_doctor")
    print("   - save_session_to_database")
    print("   - create_appointment")
    print("   - send_appointment_emails")
    print("   - get_patient_history")
    print("\n📧 Email Configuration:")
    from mcp_langgraph_app.config.settings import settings
    print(f"   SMTP Host: {settings.SMTP_HOST}")
    print(f"   SMTP User: {settings.SMTP_USER}")
    print(f"   SMTP Pass: {'*' * len(settings.SMTP_PASS) if settings.SMTP_PASS else 'NOT SET'}")
    print("\nPress Ctrl+C to stop the server\n")
    
    from mcp_langgraph_app.mcp_server.fastmcp_server import mcp
    mcp.run()
