import json
import os
from datetime import datetime, date
import requests
import streamlit as st
from google import genai

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="VU BBIT - Smart Academic Center",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM VU LMS STYLING ---
st.markdown("""
    <style>
    .main {
        padding: 0.5rem 1rem;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        border-left: 5px solid #0056b3;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        border-radius: 6px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0056b3 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- LOCAL FILE DATA SETUPS ---
DATA_FILE = "academic_data.json"

DEFAULT_DATA = {
    "courses": {
        "CS101": {
            "name": "Introduction to Computing", 
            "total_lectures": 45, 
            "completed": [],
            "playlist_id": "PL_c9i4GzY3f3wWpP_qPjL6-o3mI5C9g1-" # Example playlist or video search tag
        },
        "ENG101": {
            "name": "English Comprehension", 
            "total_lectures": 45, 
            "completed": [],
            "playlist_id": "PL_c9i4GzY3f3_eng101_sample"
        },
        "MGT211": {
            "name": "Introduction to Business", 
            "total_lectures": 45, 
            "completed": [],
            "playlist_id": "PL_c9i4GzY3f3_mgt211_sample"
        },
        "MGT503": {
            "name": "Principles of Management", 
            "total_lectures": 45, 
            "completed": [],
            "playlist_id": "PL_c9i4GzY3f3_mgt503_sample"
        },
        "ISL202": {
            "name": "Islamic Studies", 
            "total_lectures": 30, 
            "completed": [],
            "playlist_id": "PL_c9i4GzY3f3_isl202_sample"
        }
    },
    "deadlines": [
        {"title": "CS101 Assignment 1", "course": "CS101", "date": "2026-11-05", "type": "Assignment"},
        {"title": "ENG101 Quiz 1", "course": "ENG101", "date": "2026-10-25", "type": "Quiz"}
    ]
}

def load_local_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_DATA
    return DEFAULT_DATA

def save_local_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

if "app_data" not in st.session_state:
    st.session_state.app_data = load_local_data()

data = st.session_state.app_data

# --- GEMINI CLIENT INITIALIZATION ---
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", None))
gemini_client = None
if api_key:
    try:
        gemini_client = genai.Client(api_key=api_key)
    except Exception as e:
        st.warning(f"Gemini API initialization issue: {e}")

# --- SIDEBAR: NAVIGATION & GOOGLE DRIVE BACKUP ---
with st.sidebar:
    st.title("🎓 VU Student Portal")
    st.caption("BBIT Semester 1 | Smart LMS")
    
    st.markdown("---")
    st.subheader("☁️ Google Drive Sync")
    drive_file_url = st.text_input("Direct JSON Download URL (Optional)", help="Paste public or shared Google Drive direct JSON link here to restore backup.")
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        if st.button("📥 Import Drive"):
            if drive_file_url:
                try:
                    res = requests.get(drive_file_url)
                    if res.status_code == 200:
                        st.session_state.app_data = res.json()
                        save_local_data(st.session_state.app_data)
                        st.success("Synced from Google Drive!")
                        st.rerun()
                except Exception as ex:
                    st.error(f"Failed to fetch file: {ex}")
            else:
                st.info("Provide a direct URL")
                
    with col_d2:
        # Download local state to manually upload to Google Drive
        st.download_button(
            label="📤 Backup Data",
            data=json.dumps(data, indent=4),
            file_name="academic_data_backup.json",
            mime="application/json"
        )
        
    st.markdown("---")
    st.info("💡 **Quick Tip:** Use the AI Study Assistant to summarize VU handouts or solve quiz questions instantly!")

# --- MAIN LMS APPS NAVIGATION ---
st.title("📘 VU BBIT Smart Command Center")

tab_lms, tab_ai, tab_deadlines, tab_analytics = st.tabs([
    "📺 Classrooms & Lectures", 
    "🤖 Gemini AI Study Assistant", 
    "⏰ Deadlines Tracker", 
    "📊 Study Analytics"
])

# ==========================================
# TAB 1: VU CLASSROOM & YOUTUBE LECTURES
# ==========================================
with tab_lms:
    st.subheader("VU Video Lecture Classroom")
    
    selected_course = st.selectbox(
        "Select Course", 
        list(data["courses"].keys()), 
        format_func=lambda x: f"{x} - {data['courses'][x]['name']}"
    )
    
    course_data = data["courses"][selected_course]
    total_lecs = course_data["total_lectures"]
    completed_lecs = course_data["completed"]
    
    col_vid, col_check = st.columns([1.2, 0.8])
    
    with col_vid:
        st.markdown(f"### Currently Studying: **{selected_course}**")
        lec_num = st.number_input("Select Lecture Number to Watch", min_value=1, max_value=total_lecs, value=1)
        
        # Generates VU YouTube search string for instant access
        search_query = f"Virtual University {selected_course} Lecture {lec_num}"
        st.write(f"🔍 Streaming: **Lecture {lec_num}**")
        
        # YouTube direct search frame or search preview
        st.video(f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}")
        st.caption("Tip: Search and watch full VU official playlists directly on YouTube for uninterrupted viewing.")

    with col_check:
        st.markdown("### Lecture Checklist")
        st.write(f"Completed **{len(completed_lecs)} / {total_lecs}** lectures")
        st.progress(len(completed_lecs) / total_lecs)
        
        # Checklist in compact multi-column grid
        grid_cols = st.columns(2)
        for idx in range(1, total_lecs + 1):
            col_target = grid_cols[(idx - 1) % 2]
            str_idx = str(idx)
            is_done = str_idx in completed_lecs
            
            with col_target:
                check_val = st.checkbox(f"Lecture {idx}", value=is_done, key=f"chk_{selected_course}_{idx}")
                if check_val and str_idx not in completed_lecs:
                    data["courses"][selected_course]["completed"].append(str_idx)
                    save_local_data(data)
                elif not check_val and str_idx in completed_lecs:
                    data["courses"][selected_course]["completed"].remove(str_idx)
                    save_local_data(data)

# ==========================================
# TAB 2: GEMINI AI STUDY TUTOR CHATBOT
# ==========================================
with tab_ai:
    st.subheader("🤖 Gemini Academic AI Assistant")
    st.caption("Ask questions about CS101, ENG101, MGT211, MGT503, ISL202, assignments, or midterm concepts.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hello! I am your VU Academic AI Tutor. How can I help you with your BBIT studies today?"}
        ]

    # Render previous messages
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat Input Box
    if user_prompt := st.chat_input("Ask any subject question, assignment doubt, or concept query..."):
        # Append user query
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.write(user_prompt)

        # Generate Gemini Response
        with st.chat_message("assistant"):
            if not gemini_client:
                response_text = "⚠️ **Gemini API Key missing.** Please set `GEMINI_API_KEY` in Streamlit secrets or environment variables."
                st.warning(response_text)
            else:
                try:
                    system_instructions = (
                        "You are an expert Virtual University (VU) academic tutor for the BBIT program. "
                        "Help the student with quick, clear, and structured answers regarding CS101, ENG101, MGT211, "
                        "MGT503, and ISL202 subjects, past paper concepts, assignments, and study schedules."
                    )
                    prompt_content = f"{system_instructions}\n\nStudent Question: {user_prompt}"
                    
                    with st.spinner("AI is thinking..."):
                        response = gemini_client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt_content
                        )
                        response_text = response.text
                        st.write(response_text)
                except Exception as e:
                    response_text = f"Error communicating with Gemini: {e}"
                    st.error(response_text)
            
        st.session_state.chat_history.append({"role": "assistant", "content": response_text})

# ==========================================
# TAB 3: ASSIGNMENT & QUIZ DEADLINES
# ==========================================
with tab_deadlines:
    st.subheader("⏰ VU Assignment, Quiz & Exam Deadline Tracker")
    
    if not data["deadlines"]:
        st.info("No active deadlines registered.")
    else:
        sorted_deadlines = sorted(data["deadlines"], key=lambda x: x["date"])
        today = date.today()
        
        for idx, item in enumerate(sorted_deadlines):
            d_date = datetime.strptime(item["date"], "%Y-%m-%d").date()
            remaining = (d_date - today).days
            
            if remaining < 0:
                badge = "🔴 OVERDUE"
            elif remaining == 0:
                badge = "🔥 DUE TODAY"
            elif remaining <= 3:
                badge = f"⚠️ DUE IN {remaining} DAYS"
            else:
                badge = f"🟢 IN {remaining} DAYS"
                
            with st.container():
                st.markdown(f"**{item['title']}** (`{item['course']}`) — **{badge}**")
                st.caption(f"Category: {item['type']} | Deadline Date: {item['date']}")
                if st.button("Mark Completed / Remove", key=f"del_{idx}"):
                    data["deadlines"].remove(item)
                    save_local_data(data)
                    st.rerun()
                st.markdown("---")
                
    with st.expander("➕ Add New VU Deadline"):
        with st.form("add_dl_form"):
            t_title = st.text_input("Title (e.g. MGT211 GDB 1)")
            t_course = st.selectbox("Select Course", list(data["courses"].keys()))
            t_type = st.selectbox("Type", ["Assignment", "Quiz", "GDB", "Mid-Term Exam"])
            t_date = st.date_input("Target Date", value=date.today())
            
            if st.form_submit_button("Save Deadline"):
                if t_title:
                    data["deadlines"].append({
                        "title": t_title,
                        "course": t_course,
                        "date": t_date.strftime("%Y-%m-%d"),
                        "type": t_type
                    })
                    save_local_data(data)
                    st.success("Deadline added!")
                    st.rerun()

# ==========================================
# TAB 4: SEMESTER ANALYTICS & OVERVIEW
# ==========================================
with tab_analytics:
    st.subheader("📊 Overall Semester Performance")
    
    total_lecs = sum(c["total_lectures"] for c in data["courses"].values())
    done_lecs = sum(len(c["completed"]) for c in data["courses"].values())
    overall_pct = (done_lecs / total_lecs) if total_lecs > 0 else 0
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Total Lectures Completed", f"{done_lecs} / {total_lecs}")
    with col_b:
        st.metric("Semester Completion", f"{int(overall_pct * 100)}%")
        
    st.progress(overall_pct)
    st.markdown("---")
    
    st.subheader("Course Wise Completion Summary")
    for code, info in data["courses"].items():
        c_done = len(info["completed"])
        c_tot = info["total_lectures"]
        c_pct = c_done / c_tot if c_tot > 0 else 0
        st.write(f"**{code} - {info['name']}**: {c_done}/{c_tot} completed ({int(c_pct*100)}%)")
        st.progress(c_pct)
