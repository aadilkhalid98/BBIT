import streamlit as st

# Page configuration for mobile browsers
st.set_page_config(
    page_title="BBIT Study Hub",
    page_icon="📚",
    layout="centered"
)

# Academic Hierarchy for your BBIT Semester 1
if "hierarchy" not in st.session_state:
    st.session_state.hierarchy = {
        "BBIT": {
            "Semester 1": {
                "CS101 - Introduction to Computing": [
                    "Lecture_01_Overview.pdf", 
                    "Lecture_02_Hardware_Basics.pdf", 
                    "CS101_Midterm_Past_Papers.pdf"
                ],
                "ENG101 - English Comprehension": [
                    "Lecture_01_Grammar_Rules.pdf", 
                    "Paragraph_Writing_Guide.docx"
                ],
                "MGT211 - Introduction to Business": [
                    "Business_Forms_Overview.pdf"
                ],
                "MGT503 - Principles of Management": [
                    "Management_Foundations.pdf"
                ],
                "ISL202 - Islamic Studies": [
                    "Islamic_Jurisprudence_Notes.pdf"
                ]
            }
        }
    }

st.title("🎓 VU BBIT Intelligent Study Hub")
st.markdown("Your mobile-friendly cloud academic command center.")

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
            st.subheader(f"📂 Course Files: {selected_course}")
            files = st.session_state.hierarchy[selected_program][selected_semester][selected_course]
            
            for f in files:
                st.text(f"📄 {f}")
            
            st.divider()
            st.subheader("⚡ Auto-Generated Target")
            st.info(f"Today's Target: Read `{files[0]}` and review core summaries for {selected_course}.")
