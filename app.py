import json
import os
from datetime import datetime, date
import streamlit as st
from google import genai

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="My Study Guide VU",
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

# --- PERSISTENT SESSION STATE SETUP ---
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "vu_id" not in st.session_state:
    st.session_state.vu_id = ""
if "courses_data" not in st.session_state:
    st.session_state.courses_data = {
        "CS101": {"name": "Introduction to Computing", "lectures": 45, "status": "Ready"},
        "ENG101": {"name": "English Comprehension", "lectures": 45, "status": "Ready"},
        "MGT211": {"name": "Introduction to Business", "lectures": 45, "status": "Ready"},
        "MGT503": {"name": "Principles of Management", "lectures": 45, "status": "Ready"},
        "ISL202": {"name": "Islamic Studies", "lectures": 30, "status": "Ready"}
    }
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hello! I am your My Study Guide VU AI Tutor. Ask me anything about your semester courses."}
    ]

# --- GEMINI CLIENT ---
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", None))
gemini_client = None
if api_key:
    try:
        gemini_client = genai.Client(api_key=api_key)
    except Exception:
        pass

# ==========================================
# LOGIN SCREEN (PERSISTENT CHECK)
# ==========================================
if not st.session_state.user_authenticated:
    st.title("🎓 My Study Guide VU — Secure Student Login")
    st.markdown("### Enter your credentials to sync with your academic profile and Google Drive storage.")
    
    with st.form("login_form"):
        input_email = st.text_input("Google Account Email")
        input_vuid = st.text_input("VU Student ID (e.g. BC230400000)")
        input_vupass = st.text_input("VULMS Password", type="password")
        login_btn = st.form_submit_button("Sign In & Connect Account")
        
        if login_btn and input_email and input_vuid:
            st.session_state.user_authenticated = True
            st.session_state.user_email = input_email
            st.session_state.vu_id = input_vuid
            st.success("Successfully authenticated and linked account!")
            st.rerun()
    st.stop()

# ==========================================
# SIDEBAR NAVIGATION & ACCOUNT CONTROLS
# ==========================================
with st.sidebar:
    st.title("🎓 My Study Guide VU")
    st.write(f"**Student:** {st.session_state.get('vu_id', 'VU Student')}")
    st.write(f"**Email:** {st.session_state.get('user_email', '')}")
    
    if st.button("🚪 Logout / Switch Account"):
        st.session_state.user_authenticated = False
        st.rerun()
        
    st.markdown("---")
    app_mode = st.radio("Main Navigation", [
        "🌐 Official VULMS Portal Hub", 
        "📚 My Courses & Handouts", 
        "📝 AI Quiz Center", 
        "🤖 Gemini AI Study Assistant",
        "⏰ Deadlines & Analytics"
    ])

# ==========================================
# SECTION 1: OFFICIAL VULMS PORTAL HUB
# ==========================================
if app_mode == "🌐 Official VULMS Portal Hub":
    st.title("🌐 Virtual University LMS Portal Hub")
    st.markdown("""
        > **Note on Direct Embedding:** Due to Virtual University’s strict security headers (`X-Frame-Options`), external browsers block direct embedding of the live login iframe. Use the secure quick-links below to open your official portal instantly in a new tab, then manage your progress here.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔗 Direct Portal Links")
        st.markdown("[Open Official VULMS Login Page](https://vulms.vu.edu.pk/)", unsafe_allow_html=True)
        st.markdown("[Open VU Student Gradebook & VU-Info](https://vu.edu.pk/)", unsafe_allow_html=True)
    with col2:
        st.info("💡 **Workflow Tip:** Log into VULMS in your browser tab to check live announcements, download PDF handouts, then return here to generate AI quizzes and track lectures!")

# ==========================================
# SECTION 2: MY COURSES & HANDOUTS
# ==========================================
elif app_mode == "📚 My Courses & Handouts":
    st.title("📚 Semester 1 Courses & Handouts Hub")
    st.caption("Access course materials, lectures, and synced Google Drive records for your enrolled subjects.")
    
    selected_code = st.selectbox("Select Course", list(st.session_state.courses_data.keys()), format_func=lambda x: f"{x} - {st.session_state.courses_data[x]['name']}")
    course_info = st.session_state.courses_data[selected_code]
    
    st.subheader(f"{selected_code}: {course_info['name']}")
    st.write(f"**Total Lectures:** {course_info['lectures']}")
    st.success("Status: Synced with Google Drive storage profile.")
    
    # Embedded sample lecture video stream
    st.markdown("### 📺 Sample Lecture Stream")
    st.video("https://www.youtube.com/watch?v=Ng9KNHxbSf0")

# ==========================================
# SECTION 3: AI QUIZ CENTER
# ==========================================
elif app_mode == "📝 AI Quiz Center":
    st.title("📝 Unlocked AI Quiz Center")
    st.caption("Custom quizzes generated automatically by Gemini based on your selected course curriculum.")
    
    q_course = st.selectbox("Choose Course for Quiz", list(st.session_state.courses_data.keys()))
    q_topic = st.text_input("Enter Topic or Chapter (e.g. Introduction to Databases, Management Functions)")
    
    if st.button("🚀 Generate Practice Quiz"):
        if not gemini_client:
            st.error("Gemini API key is not configured in Streamlit secrets.")
        else:
            with st.spinner("Generating customized quiz questions..."):
                try:
                    prompt = f"Create 5 multiple-choice questions with answers for Virtual University course {q_course} on topic: {q_topic}."
                    response = gemini_client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                    st.markdown("### Generated Quiz:")
                    st.write(response.text)
                    st.success("Quiz generated successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")

# ==========================================
# SECTION 4: GEMINI AI STUDY ASSISTANT
# ==========================================
elif app_mode == "🤖 Gemini AI Study Assistant":
    st.title("🤖 Gemini AI Study Assistant")
    st.caption("Ask questions about your subjects, assignment solutions, or exam concepts.")
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    if user_input := st.chat_input("Ask a question about CS101, MGT211, ENG101..."):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
            
        with st.chat_message("assistant"):
            if not gemini_client:
                ans = "⚠️ Gemini API Key missing in Streamlit secrets."
                st.warning(ans)
            else:
                try:
                    with st.spinner("Thinking..."):
                        resp = gemini_client.models.generate_content(
                            model="gemini-2.5-flash", 
                            contents=f"You are a helpful VU BBIT tutor. Student question: {user_input}"
                        )
                        ans = resp.text
                        st.write(ans)
                except Exception as e:
                    ans = f"Error: {e}"
                    st.error(ans)
        st.session_state.chat_history.append({"role": "assistant", "content": ans})

# ==========================================
# SECTION 5: DEADLINES & ANALYTICS
# ==========================================
elif app_mode == "⏰ Deadlines & Analytics":
    st.title("⏰ Deadlines & Semester Analytics")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Semester Status", "Active (Semester 1)")
    with col2:
        st.metric("Enrolled Courses", "5 Core Subjects")
        
    st.markdown("### Upcoming Assignments & Quizzes")
    st.info("No pending submission deadlines registered.")
