import streamlit as st

# Page configuration for mobile browsers
st.set_page_config(
    page_title="BBIT Academic Command Center",
    page_icon="🎓",
    layout="centered"
)

# Complete VU BBIT Semester 1 Academic Hierarchy
if "hierarchy" not in st.session_state:
    st.session_state.hierarchy = {
        "BBIT": {
            "Semester 1": {
                "CS101 - Introduction to Computing": [
                    {"name": "Lecture_01_Introduction_to_Computing.pdf", "status": "Pending"},
                    {"name": "Lecture_02_History_and_Data_Storage.pdf", "status": "Pending"},
                    {"name": "Lecture_03_Operating_Systems_Basics.pdf", "status": "Pending"},
                    {"name": "CS101_Midterm_Past_Papers.pdf", "status": "Pending"}
                ],
                "ENG101 - English Comprehension": [
                    {"name": "Lecture_01_Reading_and_Dictionary.pdf", "status": "Pending"},
                    {"name": "Lecture_02_Main_Ideas_and_Topic_Sentences.pdf", "status": "Pending"},
                    {"name": "Paragraph_Writing_Guide.docx", "status": "Pending"}
                ],
                "MGT211 - Introduction to Business": [
                    {"name": "Lecture_01_History_and_Introduction_of_Business.pdf", "status": "Pending"},
                    {"name": "Lecture_02_Forms_of_Business_Ownership.pdf", "status": "Pending"},
                    {"name": "Operations_Management_Notes.pdf", "status": "Pending"}
                ],
                "MGT503 - Principles of Management": [
                    {"name": "Lecture_01_Management_Foundations.pdf", "status": "Pending"},
                    {"name": "Lecture_02_Planning_and_Decision_Making.pdf", "status": "Pending"}
                ],
                "ISL202 - Islamic Studies": [
                    {"name": "Islamic_Jurisprudence_and_Core_Values.pdf", "status": "Pending"}
                ]
            }
        }
    }

st.title("🎓 VU BBIT Academic Command Center")
st.markdown("Your mobile-friendly cloud curriculum tracker.")

# Cascading Dropdowns
programs = list(st.session_state.hierarchy.keys())
selected_program = st.selectbox("Select Program", programs)

if selected_program:
    semesters = list(st.session_state.hierarchy[selected_program].keys())
    selected_semester = st.selectbox("Select Semester", semesters)
    
    if selected_semester:
        courses = list(st.session_state.hierarchy[selected_program][selected_semester].keys())
        selected_course = st.selectbox("Select Course", courses)
        
        if selected_course:
            st.divider()
            st.subheader(f"📂 Course Materials: {selected_course}")
            files = st.session_state.hierarchy[selected_program][selected_semester][selected_course]
            
            # Display file checklist
            for i, f in enumerate(files):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(f"📄 {f['name']}")
                with col2:
                    completed = st.checkbox("Done", key=f"{selected_course}_{i}")
                    if completed:
                        f['status'] = "Completed"
                    else:
                        f['status'] = "Pending"
            
            st.divider()
            st.subheader("⚡ Auto-Generated Daily Target")
            # Find the first pending file as the active target
            pending_files = [f['name'] for f in files if f['status'] == "Pending"]
            if pending_files:
                st.info(f"**Today's Focus:** Study `{pending_files[0]}` and summarize key concepts for {selected_course.split('-')[0].strip()}.")
            else:
                st.success(f"🎉 All materials for {selected_course} are completed!")
