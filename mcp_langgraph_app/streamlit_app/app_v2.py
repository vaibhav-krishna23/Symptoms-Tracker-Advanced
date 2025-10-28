"""Streamlit App for MCP + LangGraph Symptom Tracker"""
import streamlit as st
import requests
import json
import os
from datetime import datetime
from typing import Dict, Any

# Configuration
# Configuration - works in both local and Streamlit Cloud
try:
    API_BASE = st.secrets.get("API_BASE", os.getenv("API_BASE", "http://localhost:8000"))
except:
    API_BASE = os.getenv("API_BASE", "http://localhost:8000")


# Page config
st.set_page_config(
    page_title="Symptom Tracker v2.0 - MCP + LangGraph",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Healthcare Theme CSS
st.markdown("""
<style>
/* Main app background */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #1a2332 100%);
    color: #ffffff;
}

/* Headers with better contrast */
.main-header {
    font-size: 2.8rem;
    color: #00e5ff;
    font-weight: 800;
    text-align: center;
    padding: 2rem 0;
    border-bottom: 4px solid #00e5ff;
    margin-bottom: 2rem;
    text-shadow: 0 0 20px rgba(0, 229, 255, 0.6);
    background: linear-gradient(135deg, rgba(0, 229, 255, 0.1) 0%, rgba(26, 35, 50, 0.8) 100%);
    border-radius: 15px;
}
.sub-header {
    font-size: 1.8rem;
    color: #4fc3f7;
    font-weight: 700;
    margin-top: 2rem;
    margin-bottom: 1.5rem;
    text-shadow: 0 0 10px rgba(79, 195, 247, 0.5);
}

/* Enhanced info boxes */
.info-box {
    background: linear-gradient(135deg, #1e3a5f 0%, #2d5aa0 100%);
    color: #ffffff;
    padding: 2rem;
    border-radius: 15px;
    border-left: 6px solid #00e5ff;
    margin: 1.5rem 0;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
    font-weight: 600;
    font-size: 1.1rem;
}
.success-box {
    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
    color: #ffffff;
    padding: 2rem;
    border-radius: 15px;
    border-left: 6px solid #4caf50;
    margin: 1.5rem 0;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
    font-weight: 600;
    font-size: 1.1rem;
}
.warning-box {
    background: linear-gradient(135deg, #e65100 0%, #ff9800 100%);
    color: #ffffff;
    padding: 2rem;
    border-radius: 15px;
    border-left: 6px solid #ffc107;
    margin: 1.5rem 0;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
    font-weight: 600;
    font-size: 1.1rem;
}
.error-box {
    background: linear-gradient(135deg, #b71c1c 0%, #d32f2f 100%);
    color: #ffffff;
    padding: 2rem;
    border-radius: 15px;
    border-left: 6px solid #f44336;
    margin: 1.5rem 0;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
    font-weight: 600;
    font-size: 1.1rem;
}
.emergency-box {
    background: linear-gradient(135deg, #d32f2f 0%, #f44336 100%);
    color: #ffffff;
    padding: 2.5rem;
    border-radius: 20px;
    border: 5px solid #ff1744;
    margin: 2rem 0;
    animation: pulse 2s infinite;
    box-shadow: 0 0 40px rgba(255, 23, 68, 0.7);
    font-weight: 700;
    font-size: 1.2rem;
}

/* Sidebar styling */
.css-1d391kg {
    background: linear-gradient(180deg, #0a0e1a 0%, #1a2332 100%);
}

/* Input fields with dark theme */
.stTextInput > div > div > input {
    background-color: #2d3748 !important;
    color: #ffffff !important;
    border: 2px solid #4a5568 !important;
    border-radius: 10px !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
}
.stTextArea > div > div > textarea {
    background-color: #2d3748 !important;
    color: #ffffff !important;
    border: 2px solid #4a5568 !important;
    border-radius: 10px !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
}
.stSelectbox > div > div > select {
    background-color: #2d3748 !important;
    color: #ffffff !important;
    border: 2px solid #4a5568 !important;
    border-radius: 10px !important;
}

/* Enhanced buttons */
.stButton > button {
    background: linear-gradient(135deg, #00e5ff 0%, #0099cc 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    padding: 0.75rem 2rem !important;
    box-shadow: 0 6px 20px rgba(0, 229, 255, 0.4) !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #0099cc 0%, #007399 100%) !important;
    box-shadow: 0 8px 25px rgba(0, 229, 255, 0.6) !important;
    transform: translateY(-3px) !important;
}

/* Metrics styling */
.css-1xarl3l {
    background: linear-gradient(135deg, #1a2332 0%, #2d3748 100%) !important;
    border-radius: 15px !important;
    padding: 1.5rem !important;
    border: 2px solid #4a5568 !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
}

/* Expanders */
.streamlit-expanderHeader {
    background-color: #2d3748 !important;
    color: #ffffff !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}

/* Text contrast improvements */
h1, h2, h3, h4, h5, h6 {
    color: #ffffff !important;
    font-weight: 700 !important;
}
.stMarkdown {
    color: #ffffff !important;
}
label {
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
}
.stRadio > label {
    color: #ffffff !important;
    font-weight: 600 !important;
}
.stCheckbox > label {
    color: #ffffff !important;
    font-weight: 600 !important;
}
.stSlider > label {
    color: #ffffff !important;
    font-weight: 600 !important;
}

/* Sidebar text */
.css-1v0mbdj {
    color: #ffffff !important;
    font-weight: 600 !important;
}

/* Animation */
@keyframes pulse {
    0%, 100% { 
        opacity: 1;
        box-shadow: 0 0 40px rgba(255, 23, 68, 0.7);
        transform: scale(1);
    }
    50% { 
        opacity: 0.9;
        box-shadow: 0 0 60px rgba(255, 23, 68, 1);
        transform: scale(1.02);
    }
}

/* Success/Error messages */
.stSuccess {
    background-color: #2e7d32 !important;
    color: #ffffff !important;
    font-weight: 600 !important;
}
.stError {
    background-color: #d32f2f !important;
    color: #ffffff !important;
    font-weight: 600 !important;
}
.stWarning {
    background-color: #f57c00 !important;
    color: #ffffff !important;
    font-weight: 600 !important;
}
.stInfo {
    background-color: #1976d2 !important;
    color: #ffffff !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)


# API Helper Functions
def api_request(method: str, endpoint: str, data: Dict = None, token: str = None) -> Dict[str, Any]:
    """Make API request."""
    url = f"{API_BASE}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    print(f"API Request: {method} {url}")
    print(f"Headers: {headers}")
    print(f"Data: {data}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            return {"error": "Invalid method"}
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return {"error": str(e)}


# Authentication Functions
def login_page():
    """Login page."""
    st.markdown("<div class='main-header'>🏥 Symptom Tracker v2.0</div>", unsafe_allow_html=True)
    st.markdown("<div class='info-box'><b>Powered by:</b> MCP (Model Context Protocol) + LangGraph + Google Gemini AI</div>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        secret_key = st.text_input("Secret Key", type="password", key="login_secret")
        
        if st.button("Login", type="primary", use_container_width=True):
            if email and password and secret_key:
                result = api_request("POST", "/api/v1/auth/login", {
                    "email": email,
                    "password": password,
                    "secret_key": secret_key
                })
                
                if "access_token" in result:
                    st.session_state["token"] = result["access_token"]
                    st.session_state["email"] = email
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error(f"❌ Login failed: {result.get('error', 'Invalid credentials')}")
            else:
                st.warning("⚠️ Please fill all fields")
    
    with tab2:
        st.subheader("Create New Account")
        full_name = st.text_input("Full Name", key="reg_name")
        email = st.text_input("Email", key="reg_email")
        city = st.text_input("City", key="reg_city")
        password = st.text_input("Password", type="password", key="reg_password")
        secret_key = st.text_input("Secret Key (Keep this safe!)", type="password", key="reg_secret")
        
        if st.button("Register", type="primary", use_container_width=True):
            if full_name and email and city and password and secret_key:
                result = api_request("POST", "/api/v1/auth/register", {
                    "full_name": full_name,
                    "email": email,
                    "city": city,
                    "password": password,
                    "secret_key": secret_key
                })
                
                if "patient_id" in result:
                    st.success("✅ Registration successful! Please login.")
                else:
                    st.error(f"❌ Registration failed: {result.get('error', 'Unknown error')}")
            else:
                st.warning("⚠️ Please fill all fields")


def symptom_logger_page():
    """Symptom logger page with MCP + LangGraph."""
    st.markdown("<div class='main-header'>🌡️ Log Your Symptoms</div>", unsafe_allow_html=True)
    st.markdown("<div class='info-box'>✨ <b>AI-Powered Analysis:</b> Your symptoms will be analyzed using LangGraph workflow with MCP tools</div>", unsafe_allow_html=True)
    
    # Check if appointment booking was triggered
    if st.session_state.get("book_appointment"):
        session_id = st.session_state.get("current_session_id", "")
        
        with st.spinner("📅 Booking your appointment..."):
            booking_result = api_request(
                "POST",
                "/api/v1/sessions/book-appointment",
                {"session_id": session_id},
                token=st.session_state["token"]
            )
            
            if "error" in booking_result:
                st.error(f"❌ Appointment booking failed: {booking_result['error']}")
            elif booking_result.get("success"):
                st.markdown(f"""
                <div class='success-box'>
                    <h3>✅ Appointment Successfully Booked!</h3>
                    <p><b>Doctor:</b> Dr. {booking_result.get('doctor_name', 'N/A')}</p>
                    <p><b>Clinic:</b> {booking_result.get('clinic', 'N/A')}</p>
                    <p><b>Date:</b> {booking_result.get('appointment_date', 'N/A')}</p>
                    <p>📧 Confirmation emails have been sent to you and the doctor.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning(f"Unexpected response: {booking_result}")
        
        # Clear the flag and session data
        st.session_state["book_appointment"] = False
        if "last_analysis_result" in st.session_state:
            del st.session_state["last_analysis_result"]
        if "current_session_id" in st.session_state:
            del st.session_state["current_session_id"]
        return
    
    # Check if appointment was declined
    if st.session_state.get("decline_appointment"):
        st.info("✅ Symptoms logged. Please monitor your condition and seek medical attention if symptoms worsen.")
        st.session_state["decline_appointment"] = False
        if "last_analysis_result" in st.session_state:
            del st.session_state["last_analysis_result"]
        if "current_session_id" in st.session_state:
            del st.session_state["current_session_id"]
        return
    
    # Mood selector
    st.markdown("<div class='sub-header'>😊 How are you feeling today?</div>", unsafe_allow_html=True)
    mood_options = ["😄 Great", "🙂 Good", "😐 Okay", "😟 Not Good", "😢 Terrible"]
    mood = st.select_slider("Mood", options=mood_options, value="😐 Okay")
    mood_value = mood_options.index(mood) + 1
    
    # Symptoms
    st.markdown("<div class='sub-header'>🩺 Select Your Symptoms</div>", unsafe_allow_html=True)
    
    symptom_categories = {
        "General": ["Fever", "Fatigue", "Weakness", "Chills", "Night Sweats"],
        "Pain": ["Headache", "Chest Pain", "Abdominal Pain", "Back Pain", "Joint Pain", "Muscle Pain"],
        "Respiratory": ["Cough", "Shortness of Breath", "Sore Throat", "Runny Nose", "Congestion"],
        "Digestive": ["Nausea", "Vomiting", "Diarrhea", "Constipation", "Loss of Appetite"],
        "Neurological": ["Dizziness", "Confusion", "Memory Loss", "Numbness", "Tingling"],
        "Other": ["Rash", "Swelling", "Bleeding", "Vision Changes", "Hearing Loss"]
    }
    
    selected_symptoms = []
    
    for category, symptoms in symptom_categories.items():
        with st.expander(f"📋 {category} Symptoms"):
            for symptom in symptoms:
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.checkbox(symptom, key=f"symptom_{symptom}"):
                        with col2:
                            intensity = st.slider(
                                "Intensity",
                                1, 10, 5,
                                key=f"intensity_{symptom}",
                                help="1=Mild, 10=Severe"
                            )
                        selected_symptoms.append({
                            "symptom": symptom,
                            "intensity": intensity,
                            "notes": None,
                            "photo_url": None
                        })
    
    # Photo upload section
    st.markdown("<div class='sub-header'>📷 Upload Symptom Photos (Optional)</div>", unsafe_allow_html=True)
    st.info("💡 Upload photos of rashes, wounds, swelling, or any visible symptoms")
    
    uploaded_files = st.file_uploader(
        "Choose image files",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
        help="Max 5MB per image. Supported formats: JPG, PNG, WEBP"
    )
    
    photo_urls = []
    if uploaded_files:
        for uploaded_file in uploaded_files:
            with st.spinner(f"Uploading {uploaded_file.name}..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                headers = {"Authorization": f"Bearer {st.session_state['token']}"}
                
                try:
                    response = requests.post(
                        f"{API_BASE}/api/v1/upload/symptom-photo",
                        files=files,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        photo_urls.append(result["photo_url"])
                        st.success(f"✅ {uploaded_file.name} uploaded successfully")
                    else:
                        st.error(f"❌ Failed to upload {uploaded_file.name}")
                except Exception as e:
                    st.error(f"❌ Upload error: {str(e)}")
    
    # Assign photo URLs to symptoms
    if photo_urls and selected_symptoms:
        st.info(f"📎 {len(photo_urls)} photo(s) will be attached to your first symptom")
        selected_symptoms[0]["photo_url"] = photo_urls[0] if photo_urls else None
    
    # Free text description
    st.markdown("<div class='sub-header'>📝 Describe Your Symptoms</div>", unsafe_allow_html=True)
    free_text = st.text_area(
        "Tell us more about how you're feeling",
        placeholder="Describe your symptoms in detail... When did they start? How severe are they? Any other relevant information?",
        height=150
    )
    
    # Submit button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Submit & Analyze with AI", type="primary", use_container_width=True):
            if not selected_symptoms:
                st.warning("⚠️ Please select at least one symptom")
            elif not free_text:
                st.warning("⚠️ Please describe your symptoms")
            else:
                with st.spinner("🤖 AI is analyzing your symptoms using LangGraph workflow..."):
                    result = api_request(
                        "POST",
                        "/api/v2/symptoms/submit",
                        {
                            "symptoms": selected_symptoms,
                            "mood": mood_value,
                            "free_text": free_text
                        },
                        token=st.session_state["token"]
                    )
                    
                    if "error" in result:
                        st.error(f"❌ Error: {result['error']}")
                    else:
                        # Store result in session state so it persists across reruns
                        st.session_state["last_analysis_result"] = result
                        display_analysis_results(result)


def handle_book_appointment():
    """Callback to set booking flag."""
    print("\n" + "="*60)
    print("BUTTON CLICKED: Book Appointment")
    print("="*60)
    st.session_state["book_appointment"] = True
    print(f"Session state 'book_appointment' set to: {st.session_state['book_appointment']}")
    print("="*60 + "\n")

def handle_decline_appointment():
    """Callback to set decline flag."""
    print("\n" + "="*60)
    print("BUTTON CLICKED: Decline Appointment")
    print("="*60)
    st.session_state["decline_appointment"] = True
    print("="*60 + "\n")


def display_analysis_results(result: Dict[str, Any]):
    """Display AI analysis results."""
    st.markdown("---")
    st.markdown("<div class='main-header'>📊 AI Analysis Results</div>", unsafe_allow_html=True)
    
    ai_analysis = result.get("ai_analysis", {})
    severity_check = result.get("severity_check", {})
    appointment_info = result.get("appointment_info", {})
    
    # Severity score
    severity = ai_analysis.get("severity", 0)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Severity Score", f"{severity}/10")
    with col2:
        st.metric("Status", "🚨 EMERGENCY" if severity >= 8 else "✅ Normal")
    with col3:
        st.metric("Session ID", result.get("session_id", "N/A")[:8])
    
    # AI Summary
    st.markdown("<div class='sub-header'>🤖 AI Medical Summary</div>", unsafe_allow_html=True)
    summary = ai_analysis.get("summary", "No summary available")
    
    if severity >= 8:
        st.markdown(f"<div class='emergency-box'><h3>⚠️ HIGH SEVERITY DETECTED</h3><p>{summary}</p></div>", unsafe_allow_html=True)
        
        # Ask user for appointment confirmation
        st.markdown("<div class='sub-header'>📅 Appointment Recommendation</div>", unsafe_allow_html=True)
        st.markdown("<div class='warning-box'>⚠️ Based on your current symptoms, we recommend scheduling an appointment with a doctor.</div>", unsafe_allow_html=True)
        
        session_id = result.get("session_id", "")
        st.session_state["current_session_id"] = session_id
        
        # Show buttons
        st.write("👇 Choose an option:")
        col1, col2 = st.columns(2)
        with col1:
            st.button(
                "📅 Yes, Book Appointment",
                type="primary",
                use_container_width=True,
                key=f"book_apt_{session_id}",
                on_click=handle_book_appointment
            )
        with col2:
            st.button(
                "❌ No, Just Log Symptoms",
                use_container_width=True,
                key=f"no_apt_{session_id}",
                on_click=handle_decline_appointment
            )
    else:
        st.markdown(f"<div class='info-box'>{summary}</div>", unsafe_allow_html=True)
    
    # Red flags
    red_flags = ai_analysis.get("red_flags", [])
    if red_flags:
        st.markdown("<div class='sub-header'>🚩 Red Flags Detected</div>", unsafe_allow_html=True)
        for flag in red_flags:
            st.markdown(f"<div class='warning-box'>⚠️ {flag}</div>", unsafe_allow_html=True)
    
    # Suggested actions
    actions = ai_analysis.get("suggested_actions", [])
    if actions:
        st.markdown("<div class='sub-header'>💡 Recommended Actions</div>", unsafe_allow_html=True)
        for action in actions:
            st.markdown(f"- {action}")
    
    # Appointment info
    if appointment_info.get("success"):
        st.markdown("<div class='sub-header'>📅 Appointment Scheduled</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='success-box'>
            <h4>✅ Emergency Appointment Confirmed</h4>
            <p><b>Doctor:</b> Dr. {appointment_info.get('doctor_name', 'N/A')}</p>
            <p><b>Clinic:</b> {appointment_info.get('clinic_location', 'N/A')}</p>
            <p><b>Date:</b> {appointment_info.get('appointment_date', 'N/A')}</p>
            <p><b>Status:</b> {appointment_info.get('status', 'N/A').upper()}</p>
            <p>📧 Confirmation emails have been sent to you and the doctor.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Workflow messages
    st.markdown("<div class='sub-header'>🔄 Workflow Execution Log</div>", unsafe_allow_html=True)
    with st.expander("View LangGraph Workflow Steps"):
        messages = result.get("workflow_messages", [])
        for i, msg in enumerate(messages, 1):
            st.text(f"{i}. {msg}")
    
    st.success("✅ Analysis complete! Your symptoms have been logged.")


def dashboard_page():
    """Dashboard page."""
    st.markdown("<div class='main-header'>📊 Your Health Dashboard</div>", unsafe_allow_html=True)
    
    # Get sessions
    result = api_request("GET", "/api/v1/dashboard/sessions", token=st.session_state["token"])
    
    if "error" in result:
        st.error(f"❌ Error loading dashboard: {result['error']}")
        return
    
    sessions = result.get("sessions", [])
    
    if not sessions:
        st.info("📝 No symptom logs yet. Start by logging your symptoms!")
        return
    
    # Statistics
    st.markdown("<div class='sub-header'>📈 Statistics</div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Sessions", len(sessions))
    with col2:
        red_flags = sum(1 for s in sessions if s.get("red_flag"))
        st.metric("Red Flags", red_flags)
    with col3:
        avg_severity = sum(s.get("severity_score", 0) for s in sessions) / len(sessions) if sessions else 0
        st.metric("Avg Severity", f"{avg_severity:.1f}/10")
    with col4:
        recent = sessions[0] if sessions else {}
        st.metric("Last Check", recent.get("start_time", "N/A")[:10] if recent else "N/A")
    
    # Session history
    st.markdown("<div class='sub-header'>📋 Session History</div>", unsafe_allow_html=True)
    
    for session in sessions:
        severity = session.get("severity_score", 0)
        red_flag = session.get("red_flag", False)
        
        with st.expander(
            f"{'🚨' if red_flag else '✅'} {session.get('start_time', 'N/A')[:19]} - Severity: {severity}/10"
        ):
            st.markdown(f"**Session ID:** {session.get('session_id', 'N/A')}")
            st.markdown(f"**Severity:** {severity}/10")
            st.markdown(f"**Red Flag:** {'Yes ⚠️' if red_flag else 'No ✅'}")
            st.markdown(f"**AI Summary:** {session.get('ai_summary', 'No summary')}")
            
            if st.button("View Details", key=f"details_{session.get('session_id')}"):
                view_session_details(session.get('session_id'))


def view_session_details(session_id: str):
    """View detailed session information."""
    result = api_request(
        "GET",
        f"/api/v1/dashboard/session/{session_id}/details",
        token=st.session_state["token"]
    )
    
    if "error" in result:
        st.error(f"❌ Error: {result['error']}")
        return
    
    session = result.get("session", {})
    symptoms = result.get("symptoms", [])
    chat_logs = result.get("chat_logs", [])
    
    st.markdown("### 📝 Symptoms")
    for symptom in symptoms:
        st.markdown(f"- **{symptom['symptom']}**: Intensity {symptom['intensity']}/10")
    
    st.markdown("### 💬 Chat Logs")
    for log in chat_logs:
        sender = "👤 You" if log['sender'] == 'patient' else "🤖 AI"
        st.markdown(f"**{sender}:** {log['message']}")


# Sidebar
def render_sidebar():
    """Render sidebar."""
    st.sidebar.markdown("### 🏥 Symptom Tracker v2.0")
    st.sidebar.markdown("**Powered by MCP + LangGraph**")
    st.sidebar.markdown("---")
    
    if "token" in st.session_state:
        st.sidebar.markdown(f"👤 **Logged in as:**")
        st.sidebar.markdown(f"{st.session_state.get('email', 'User')}")
        st.sidebar.markdown("---")
        
        page = st.sidebar.radio(
            "Navigation",
            ["🌡️ Log Symptoms", "📊 Dashboard"],
            label_visibility="collapsed"
        )
        
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        return page
    
    return None


# Main App
def main():
    """Main application."""
    page = render_sidebar()
    
    if "token" not in st.session_state:
        login_page()
    else:
        if page == "🌡️ Log Symptoms":
            symptom_logger_page()
        elif page == "📊 Dashboard":
            dashboard_page()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Value Health Inc.**")
    st.sidebar.markdown("Version 2.0.0")
    st.sidebar.markdown("*AI-Powered Healthcare*")


if __name__ == "__main__":
    main()
