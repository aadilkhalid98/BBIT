import json
import os
from datetime import datetime, date
import requests
import streamlit as st
from google import genai

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="My Study Guide VU",
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
    .announcement-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 20px;
        font-weight: 500;
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
            "sample_video_id": "Ng9KNHxbSf0", # Verified VU CS101 Lecture stream ID
            "handout_link": "https://vulms.vu.edu.pk/"
        },
        "ENG101": {
            "name": "English Comprehension", 
            "total_lectures": 45, 
            "completed": [],
            "sample_video_id": "iqncdxFLgoc", # Verified VU ENG101 Lecture stream ID
            "handout_link": "https://vulms.vu.edu.pk/"
        },
        "MGT211": {
            "name": "Introduction to Business", 
            "total_lectures": 45, 
            "completed": [],
            "sample_video_id": "hwz_IvcUL-8", # Verified VU MGT211 Crash Course ID
            "handout_link": "https://vulms.vu.edu.pk/"
        },
        "MGT503": {
            "name": "Principles of Management", 
            "total_lectures": 45, 
            "completed": [],
            "sample_video_id": "Ng9KNHxbSf0", 
            "handout_link": "https://vulms.vu.edu.pk/"
        },
        "ISL202": {
            "name": "Islamic Studies", 
            "total_lectures": 30, 
            "completed": [],
            "sample_video_id": "ZwbpXUZqWEw", # Verified VU ISL202 Lecture / Quiz prep ID
            "handout_link": "https://vulms.vu.edu.pk/"
        }
    },
    "deadlines": [
        {"title": "CS101 Assignment 1", "course": "CS101", "date": "2026-11-05", "type": "Assignment"},
        {"title": "ENG101 Quiz 1", "course": "ENG101", "date": "2026-10-25", "type": "Quiz"}
    ],
    "notifications": [
        "📢 **VU Official Update:** Mid-Term Exam Schedule for Fall Semester has been updated on VULMS.",
        "⚠️ **Assignment Alert:** CS101 Assignment 1 submission deadline is approaching soon. Complete your exercises!",
        "💡 **Tip:** Use the Gemini AI tab below to instantly clear concepts or generate practice mock MCQs."
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

# Ensure notifications key exists for older saved json files
if "notifications" not in data:
    data["notifications"] = DEFAULT_DATA["notifications"]

# --- GEMINI CLIENT INITIALIZATION ---
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", None))
gemini_client = None
if api_key:
    try:
        gemini_client = genai.Client(api_key=api_key)
    except Exception as e:
        st.warning(f"Gemini API initialization issue: {e}")

# --- SIDEBAR: NAVIGATION & EXTRA OPTIONS ---
with st.sidebar:
    st.title("🎓 My Study Guide VU")
    st.caption("BBIT Semester 1 | Student Portal")
    
    st.markdown("---")
    st.subheader("📌 Quick Menu")
    
    # Navigation Radio for Sidebar Additions
    sidebar_nav = st.radio("Go to Section:", ["🏠 Main Dashboard", "📝 Take Quizzes", "📚 Books & Handouts"])
    
    st.markdown("---")
    st.subheader("☁️ Google Drive Sync")
    drive_file_url = st.text_input("Direct JSON Backup URL", help="Paste shared direct link to JSON file to restore progress.")
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        if st.button("📥 Import"):
            if drive_file_url:
                try:
                    res = requests.get(drive_file_url)
                    if res.status_code == 200:
                        st.session_state.app_data = res.json()
                        save_local_data(st.session_state.app_data)
                        st.success("Synced!")
                        st.rerun()
                except Exception as ex:
                    st.error(f"Error: {ex}")
            else:
                st.info("Enter URL")
                
    with col_d2:
        st.download_button(
            label="📤 Export",
            data=json.dumps(data, indent=4),
            file_name="vu_study_guide_data.json",
            mime="application/json"
        )

# ==========================================
# SIDEBAR OPTION 2: TAKE QUIZZES
# ==========================================
if sidebar_nav == "📝 Take Quizzes":
    st.title("📝 Practice Mock Quizzes")
    st.caption("Test your conceptual understanding across Semester 1 subjects with AI-generated mock tests.")
    
    quiz_course = st.selectbox("Select Subject for Quiz", list(data["courses"].keys()), format_func=lambda x: f"{x} - {data['courses'][x]['name']}")
    quiz_topic = st.text_input("Enter Topic or Lecture Range (e.g. Lectures 1-5, Loops, Management Functions)")
    
    if st.button("🚀 Generate AI Practice Quiz"):
        if not gemini_client:
            st.error("Gemini API Key missing in secrets. Please configure it to use AI Quiz generation.")
        else:
            with st.spinner("Generating multiple-choice questions..."):
                try:
                    prompt = f"Create 3 multiple-choice practice questions with answers for Virtual University course {quiz_course} on topic: {quiz_topic}. Format clearly with options A, B, C, D and provide the correct answer at the end of each."
                    resp = gemini_client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                    st.markdown("### Quiz Generated:")
                    st.write(resp.text)
                except Exception as e:
                    st.error(f"Error generating quiz: {e}")

# ==========================================
# SIDEBAR OPTION 3: BOOKS & HANDOUTS
# ==========================================
elif sidebar_nav == "📚 Books & Handouts":
    st.title("📚 Semester 1 Books & Handouts Library")
    st.caption("Official Virtual University Course Handouts and Reference Material Repository.")
    
    for code, info in data["courses"].items():
        with st.expander(f"{code}: {info['name']}"):
            st.write(f"**Total Lectures:** {info['total_lectures']}")
            st.markdown(f"📥 [Access Official VULMS Handouts Portal]({info['handout_link']})")
            st.info(f"Tip: You can download PDF handouts directly from your official VULMS account login for offline reading.")

# ==========================================
# MAIN DASHBOARD VIEW
# ==========================================
else:
    st.title("📘 My Study Guide VU — Command Center")
    
    # --- NOTIFICATIONS AREA ---
    st.markdown("### 🔔 VU Update & Notification Center")
    for note in data.get("notifications", []):
        st.markdown(f'<div class="announcement-box">{note}</div>', unsafe_allow_html=True)
        
    with st.expander("➕ Add New Notification / Announcement"):
        with st.form("new_notif_form"):
            new_note_text = st.text_area("Announcement Details")
            if st.form_submit_button("Publish Notification"):
                if new_note_text:
                    data["notifications"].insert(0, f"📢 **Custom Note:** {new_note_text}")
                    save_local_data(data)
                    st.success("Notification added!")
                    st.rerun()

    st.markdown("---")

    # --- TABS FOR LMS, AI, DEADLINES, ANALYTICS ---
    tab_lms, tab_ai, tab_deadlines, tab_analytics = st.tabs([
        "📺 Lectures & Classroom", 
        "🤖 Gemini AI Study Assistant", 
        "⏰ Deadlines Tracker", 
        "📊 Study Analytics"
    ])

    # ==========================================
    # TAB 1: VU CLASSROOM & YOUTUBE LECTURES
    # ==========================================
    with tab_lms:
        st.subheader("📺 VU Video Lecture Classroom")
        
        selected_course = st.selectbox(
            "Select Course", 
            list(data["courses"].keys()), 
            format_func=lambda x: f"{x} - {data['courses'][x]['name']}"
        )
        
        course_data = data["courses"][selected_course]
        total_lecs = course_data["total_lectures"]
        completed_lecs = course_data["completed"]
        
        col_vid, col_check = st.columns([1.3, 0.7])
        
        with col_vid:
            st.markdown(f"### Studying: **{selected_course} - {course_data['name']}**")
            lec_num = st.number_input("Select Lecture Number", min_value=1, max_value=total_lecs, value=1)
            
            # Embed verified video stream
            video_id = course_data.get("sample_video_id", "Ng9KNHxbSf0")
            st.video(f"https://www.youtube.com/watch?v={video_id}")
            st.caption(f"Streaming official lecture material for {selected_course}.")
            
            # Direct link button to watch on YouTube app
            st.markdown(
                f"""
                <a href="https://www.youtube.com/results?search_query=Virtual+University+{selected_course}+Lecture+{lec_num}" target="_blank">
                    <button style="width:100%; padding:10px; border-radius:8px; background-color:#FF0000; color:white; border:none; font-weight:bold; cursor:pointer;">
                        ▶️ Open Lecture {lec_num} on YouTube App
                    </button>
                </a>
                """, 
                unsafe_allow_html=True
            )

        with col_check:
            st.markdown("### Lecture Checklist")
            st.write(f"Completed **{len(completed_lecs)} / {total_lecs}** lectures")
            st.progress(len(completed_lecs) / total_lecs if total_lecs > 0 else 0)
            
            grid_cols = st.columns(2)
            for idx in range(1, total_lecs + 1):
                col_target = grid_cols[(idx - 1) % 2]
                str_idx = str(idx)
                is_done = str_idx in completed_lecs
                
                with col_target:
                    check_val = st.checkbox(f"Lec {idx}", value=is_done, key=f"chk_{selected_course}_{idx}")
                    if check_val and str_idx not in completed_lecs:
                        data["courses"][selected_course]["completed"].append(str_idx)
                        save_local_data(data)
                    elif not check_val and str_idx in completed_lecs:
                        data["courses"][selected_course]["completed"].remove(str_idx)
                        save_local_data(data)

    # ==========================================
    # TAB 2: GEMINI AI TUTOR CHATBOT
    # ==========================================
    with tab_ai:
        st.subheader("🤖 Gemini Academic AI Assistant")
        st.caption("Ask questions about CS101, ENG101, MGT211, MGT503, ISL202, assignments, or midterm concepts.")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [
                {"role": "assistant", "content": "Hello! I am your My Study Guide VU AI Tutor. How can I help you with your BBIT studies today?"}
            ]

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if user_prompt := st.chat_input("Ask any subject question or assignment doubt..."):
            st.session_state.chat_history.append({"role": "user", "content": user_prompt})
            with st.chat_message("user"):
                st.write(user_prompt)

            with st.chat_message("assistant"):
                if not gemini_client:
                    response_text = "⚠️ **Gemini API Key missing.** Please set `GEMINI_API_KEY` in Streamlit secrets."
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
        st.subheader("⏰ VU Assignment, Quiz & Exam Deadlines")
        
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
