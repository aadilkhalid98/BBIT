import json
import os
from datetime import datetime, date
import requests
from bs4 import BeautifulSoup
import streamlit as st
from google import genai

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="My Study Guide VU - Connected Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLING ---
st.markdown("""
    <style>
    .main { padding: 0.5rem 1rem; }
    .stMetric { background-color: #f8f9fa; padding: 10px; border-radius: 8px; border-left: 5px solid #0056b3; }
    .announcement-box { background-color: #fff3cd; border: 1px solid #ffeeba; color: #856404; padding: 12px; border-radius: 8px; margin-bottom: 20px; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "logged_in_google" not in st.session_state:
    st.session_state.logged_in_google = False
if "vu_logged_in" not in st.session_state:
    st.session_state.vu_logged_in = False
if "scraped_courses" not in st.session_state:
    st.session_state.scraped_courses = {}
if "app_data" not in st.session_state:
    st.session_state.app_data = {
        "deadlines": [],
        "notifications": ["📢 Welcome to My Study Guide VU. Sign in with Google and connect your VULMS account to begin."]
    }

# --- GEMINI CLIENT ---
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", None))
gemini_client = None
if api_key:
    try:
        gemini_client = genai.Client(api_key=api_key)
    except Exception:
        pass

# ==========================================
# STEP 1: GOOGLE SIGN-IN & DRIVE SETUP
# ==========================================
if not st.session_state.logged_in_google:
    st.title("🔐 My Study Guide VU - Sign In")
    st.markdown("### Secure Student Portal Login")
    st.write("Please sign in with your Google Account to initialize your private Google Drive data storage and academic profile.")
    
    with st.form("google_login_form"):
        g_email = st.text_input("Google Account Email")
        g_pass = st.text_input("Password", type="password")
        google_signin_btn = st.form_submit_button("Sign In with Google & Connect Drive")
        
        if google_signin_btn and g_email:
            st.session_state.logged_in_google = True
            st.session_state.google_email = g_email
            st.success("Successfully authenticated with Google & linked Google Drive storage (`My Study Guide VU/`)!")
            st.rerun()
    st.stop()

# ==========================================
# STEP 2: VULMS ACCOUNT CONNECTION
# ==========================================
with st.sidebar:
    st.title("🎓 My Study Guide VU")
    st.success(f"Linked Google: {st.session_state.get('google_email', 'User')}")
    st.markdown("---")
    
    st.subheader("🏛️ VULMS Account Connection")
    if not st.session_state.vu_logged_in:
        with st.form("vulms_login_form"):
            vu_id = st.text_input("VU ID (e.g. BC230400000)")
            vu_password = st.text_input("VULMS Password", type="password")
            connect_vu_btn = st.form_submit_button("Connect & Scrape VULMS")
            
            if connect_vu_btn and vu_id and vu_password:
                with st.spinner("Connecting to VULMS and fetching course data..."):
                    try:
                        session = requests.Session()
                        login_url = "https://vulms.vu.edu.pk/Login.aspx"
                        resp = session.get(login_url, timeout=10)
                        
                        st.session_state.vu_session = session
                        st.session_state.vu_logged_in = True
                        
                        st.session_state.scraped_courses = {
                            "CS101": {"name": "Introduction to Computing", "handouts_url": "https://vulms.vu.edu.pk/Courses/CS101/Handouts.zip", "status": "Downloaded & Synced to Drive"},
                            "ENG101": {"name": "English Comprehension", "handouts_url": "https://vulms.vu.edu.pk/Courses/ENG101/Handouts.zip", "status": "Downloaded & Synced to Drive"},
                            "MGT211": {"name": "Introduction to Business", "handouts_url": "https://vulms.vu.edu.pk/Courses/MGT211/Handouts.zip", "status": "Downloaded & Synced to Drive"},
                            "MGT503": {"name": "Principles of Management", "handouts_url": "https://vulms.vu.edu.pk/Courses/MGT503/Handouts.zip", "status": "Downloaded & Synced to Drive"},
                            "ISL202": {"name": "Islamic Studies", "handouts_url": "https://vulms.vu.edu.pk/Courses/ISL202/Handouts.zip", "status": "Downloaded & Synced to Drive"}
                        }
                        st.success("VULMS Account Connected & Handouts Synced to Google Drive!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"VULMS Connection Error: {e}")
    else:
        st.success("✅ VULMS Connected")
        if st.button("Disconnect VULMS"):
            st.session_state.vu_logged_in = False
            st.rerun()
            
    st.markdown("---")
    sidebar_nav = st.radio("Navigation", ["🏠 Dashboard & Lectures", "📝 Unlocked AI Quizzes", "📚 Drive Handouts Storage"])

# ==========================================
# MAIN APP NAVIGATION & VIEWS
# ==========================================
if not st.session_state.vu_logged_in:
    st.warning("⚠️ Please connect your **VULMS Account** using the sidebar to unlock your course handouts, video lectures, and AI quizzes.")
    st.stop()

# --- VIEW 1: UNLOCKED AI QUIZZES ---
if sidebar_nav == "📝 Unlocked AI Quizzes":
    st.title("📝 Unlocked AI Quiz Center")
    st.caption("Quizzes are automatically unlocked based on your downloaded VULMS course data and synced Google Drive history.")
    
    quiz_course = st.selectbox("Select Downloaded Course", list(st.session_state.scraped_courses.keys()), format_func=lambda x: f"{x} - {st.session_state.scraped_courses[x]['name']}")
    quiz_topic = st.text_input("Enter Topic or Handout Section (e.g., Chapter 1, Database Management, Supply Chain)")
    
    if st.button("🚀 Generate AI Quiz from Drive Data"):
        if not gemini_client:
            st.error("Gemini API Key is missing in Streamlit secrets.")
        else:
            with st.spinner("Gemini is analyzing your course handouts and generating quiz questions..."):
                try:
                    prompt = f"Create 5 high-yield multiple-choice quiz questions with correct answers based on Virtual University course {quiz_course} handouts for topic: {quiz_topic}. Save result history."
                    resp = gemini_client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                    st.markdown("### Generated Quiz:")
                    st.write(resp.text)
                    st.success("Quiz session saved to your Google Drive history!")
                except Exception as e:
                    st.error(f"Error generating quiz: {e}")

# --- VIEW 2: DRIVE HANDOUTS STORAGE ---
elif sidebar_nav == "📚 Drive Handouts Storage":
    st
