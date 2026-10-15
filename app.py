import json
import os
from datetime import datetime, date
import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="VU BBIT Command Center",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS FOR MOBILE OPTIMIZATION ---
st.markdown("""
    <style>
    .main {
        padding: 0rem 0.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ff4b4b !important;
        color: white !important;
    }
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA PERSISTENCE SETUP (JSON FILE) ---
DATA_FILE = "academic_data.json"

DEFAULT_DATA = {
    "courses": {
        "CS101": {"name": "Introduction to Computing", "total_lectures": 45, "completed": []},
        "ENG101": {"name": "English Comprehension", "total_lectures": 45, "completed": []},
        "MGT211": {"name": "Introduction to Business", "total_lectures": 45, "completed": []},
        "MGT503": {"name": "Principles of Management", "total_lectures": 45, "completed": []},
        "ISL202": {"name": "Islamic Studies", "total_lectures": 30, "completed": []}
    },
    "deadlines": [
        {"title": "CS101 Assignment 1", "course": "CS101", "date": "2026-11-05", "type": "Assignment"},
        {"title": "ENG101 Quiz 1", "course": "ENG101", "date": "2026-10-25", "type": "Quiz"},
        {"title": "MGT211 Mid-Term Exam", "course": "MGT211", "date": "2026-12-10", "type": "Mid-Term"},
        {"title": "ISL202 Assignment 1", "course": "ISL202", "date": "2026-11-15", "type": "Assignment"}
    ]
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_DATA
    return DEFAULT_DATA

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Initialize Session State Data
if "app_data" not in st.session_state:
    st.session_state.app_data = load_data()

data = st.session_state.app_data

# --- APP HEADER ---
st.title("🎓 BBIT Command Center")
st.caption("Semester 1 | Virtual University of Pakistan")

# --- NAVIGATION TABS ---
tab1, tab2, tab3 = st.tabs(["📚 Lectures", "⏰ Deadlines", "📊 Analytics"])

# ==========================================
# TAB 1: COURSES & LECTURES CHECKLIST
# ==========================================
with tab1:
    st.subheader("Lecture Progress Tracker")
    
    # Course selection dropdown
    course_keys = list(data["courses"].keys())
    selected_course_key = st.selectbox(
        "Select Course", 
        course_keys, 
        format_func=lambda x: f"{x} - {data['courses'][x]['name']}"
    )
    
    course_info = data["courses"][selected_course_key]
    total_lects = course_info["total_lectures"]
    completed_lects = course_info["completed"]
    
    # Course specific progress bar
    progress_pct = len(completed_lects) / total_lects if total_lects > 0 else 0
    st.progress(progress_pct, text=f"Course Progress: {len(completed_lects)} / {total_lects} Lectures Completed ({int(progress_pct * 100)}%)")
    
    st.markdown("---")
    st.write("**Interactive Lecture Checklist:**")
    
    # Render checkboxes in a clean grid/list layout
    cols_per_row = 3
    for i in range(1, total_lects + 1, cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            lect_num = i + j
            if lect_num <= total_lects:
                lect_str = str(lect_num)
                is_checked = lect_str in completed_lects
                
                with cols[j]:
                    checked = st.checkbox(f"Lec {lect_num}", value=is_checked, key=f"{selected_course_key}_lec_{lect_num}")
                    
                    # Update state logic
                    if checked and lect_str not in completed_lects:
                        data["courses"][selected_course_key]["completed"].append(lect_str)
                        save_data(data)
                    elif not checked and lect_str in completed_lects:
                        data["courses"][selected_course_key]["completed"].remove(lect_str)
                        save_data(data)

# ==========================================
# TAB 2: DEADLINES & COUNTDOWN TIMER
# ==========================================
with tab2:
    st.subheader("Upcoming Deadlines & Exams")
    
    # Display existing deadlines
    if not data["deadlines"]:
        st.info("No upcoming deadlines added yet.")
    else:
        # Sort deadlines by date
        sorted_deadlines = sorted(data["deadlines"], key=lambda x: x["date"])
        
        today = date.today()
        for idx, item in enumerate(sorted_deadlines):
            deadline_date = datetime.strptime(item["date"], "%Y-%m-%d").date()
            delta_days = (deadline_date - today).days
            
            # Badge styling based on urgency
            if delta_days < 0:
                status_text = "⚠️ Overdue"
                box_color = "🔴"
            elif delta_days == 0:
                status_text = "🔥 Due Today!"
                box_color = "🔥"
            elif delta_days <= 3:
                status_text = f"⏳ Due in {delta_days} days"
                box_color = "⚠️"
            else:
                status_text = f"📅 In {delta_days} days"
                box_color = "✅"
            
            with st.container():
                st.markdown(f"**{box_color} {item['title']}** ({item['course']})")
                st.caption(f"Type: {item['type']} | Due Date: {item['date']} | {status_text}")
                
                if st.button("Delete", key=f"del_deadline_{idx}"):
                    data["deadlines"].remove(item)
                    save_data(data)
                    st.rerun()
                st.markdown("---")

    # Add New Deadline Expander
    with st.expander("➕ Add New Assignment/Quiz"):
        with st.form("new_deadline_form"):
            new_title = st.text_input("Task Title (e.g. CS101 Assignment 2)")
            new_course = st.selectbox("Course", course_keys)
            new_type = st.selectbox("Category", ["Assignment", "Quiz", "Mid-Term", "GDB"])
            new_date = st.date_input("Due Date", value=date.today())
            
            submit_btn = st.form_submit_button("Save Deadline")
            if submit_btn and new_title:
                data["deadlines"].append({
                    "title": new_title,
                    "course": new_course,
                    "date": new_date.strftime("%Y-%m-%d"),
                    "type": new_type
                })
                save_data(data)
                st.success("Deadline added successfully!")
                st.rerun()

# ==========================================
# TAB 3: ANALYTICS & SEMESTER OVERVIEW
# ==========================================
with tab3:
    st.subheader("Semester 1 Performance Analytics")
    
    total_semester_lectures = sum(c["total_lectures"] for c in data["courses"].values())
    total_completed_lectures = sum(len(c["completed"]) for c in data["courses"].values())
    overall_progress = total_completed_lectures / total_semester_lectures if total_semester_lectures > 0 else 0
    
    # Overall Metric Cards
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Completed", f"{total_completed_lectures} / {total_semester_lectures}")
    with col2:
        st.metric("Overall Completion", f"{int(overall_progress * 100)}%")
        
    st.markdown("### Overall Progress Bar")
    st.progress(overall_progress, text=f"Semester 1 Completion: {int(overall_progress * 100)}%")
    
    st.markdown("---")
    st.subheader("Course-wise Breakdown")
    
    for code, info in data["courses"].items():
        comp_count = len(info["completed"])
        tot_count = info["total_lectures"]
        pct = comp_count / tot_count if tot_count > 0 else 0
        
        st.write(f"**{code}: {info['name']}** ({comp_count}/{tot_count})")
        st.progress(pct)
