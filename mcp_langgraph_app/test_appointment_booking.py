"""Debug script to test appointment booking endpoint"""
import requests
import json

# Configuration
API_BASE = "http://localhost:8000"

# Test data - replace with your actual token and session_id
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMzNmYWEyZC1kN2U2LTQ0NzgtYTQwNS0wNDFjN2FkN2IwMzIiLCJleHAiOjE3NjE0MTA0MTd9.dDV0Cd4ZBvqqCYjr-29_1NTYk_dCKyMkq0Pr-T3QY_8"
SESSION_ID = "7ce22091-8027-4fb8-a46a-5e0746a8cc4c"  # Replace with actual session ID from your last symptom submission

def test_appointment_booking():
    """Test the appointment booking endpoint"""
    url = f"{API_BASE}/api/v1/sessions/book-appointment"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }
    data = {
        "session_id": SESSION_ID
    }
    
    print("=" * 80)
    print("TESTING APPOINTMENT BOOKING ENDPOINT")
    print("=" * 80)
    print(f"\nURL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Data: {json.dumps(data, indent=2)}")
    print("\n" + "=" * 80)
    print("SENDING REQUEST...")
    print("=" * 80 + "\n")
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"\nResponse Headers: {dict(response.headers)}")
        print(f"\nResponse Body:")
        print("-" * 80)
        
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2))
        except:
            print(response.text)
        
        print("-" * 80)
        
        if response.status_code == 200:
            print("\n✅ SUCCESS: Appointment booking endpoint is working!")
            result = response.json()
            if result.get("success"):
                print(f"\n📅 Appointment Details:")
                print(f"   Doctor: Dr. {result.get('doctor_name', 'N/A')}")
                print(f"   Clinic: {result.get('clinic', 'N/A')}")
                print(f"   Date: {result.get('appointment_date', 'N/A')}")
                print(f"   Emails Sent: {result.get('emails_sent', False)}")
        else:
            print(f"\n❌ ERROR: Request failed with status {response.status_code}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ CONNECTION ERROR: Cannot connect to {API_BASE}")
        print(f"   Make sure FastAPI server is running on port 8000")
        print(f"   Error: {e}")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    print("\n🔍 APPOINTMENT BOOKING DEBUG SCRIPT\n")
    print("This script will test the appointment booking endpoint directly.")
    print("Make sure:")
    print("  1. FastAPI server is running (port 8000)")
    print("  2. MCP server is running (port 8001)")
    print("  3. You have a valid session_id from a recent symptom submission")
    print("\n")
    
    # Prompt for session ID
    user_session = input(f"Enter session_id (or press Enter to use default '{SESSION_ID}'): ").strip()
    if user_session:
        SESSION_ID = user_session
    
    test_appointment_booking()
