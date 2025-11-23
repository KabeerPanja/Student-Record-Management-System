import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Student System",
    page_icon="🎓",
    layout="wide"
)

# --- DATA & CLASS DEFINITIONS ---
DATA_FILE = "students.csv"

def load_students():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, dtype={'student_id': str})
    return pd.DataFrame(columns=[
        "student_id", "first_name", "last_name", "age",
        "grade", "email", "enrollment_date", "score"
    ])

def save_students(df):
    df.to_csv(DATA_FILE, index=False)

class Student:
    def __init__(self, student_id, first_name, last_name, age, grade, email, enrollment_date, score):
        self.student_id = str(student_id)
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.grade = grade
        self.email = email
        self.enrollment_date = enrollment_date
        self.score = score
    
    def to_dict(self):
        return {
            "student_id": self.student_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "grade": self.grade,
            "email": self.email,
            "enrollment_date": self.enrollment_date,
            "score": self.score
        }

class StudentManager:
    def __init__(self):
        self.df = load_students()

    def add_student(self, student):
        if student.student_id in self.df['student_id'].astype(str).values:
            st.error("❌ Student ID already exists!")
            return False
        new_df = pd.DataFrame([student.to_dict()])
        self.df = pd.concat([self.df, new_df], ignore_index=True)
        save_students(self.df)
        st.success("✅ Student added successfully!")
        return True

    def update_student(self, student_id, updated_data):
        if student_id not in self.df['student_id'].astype(str).values:
            st.error("Student ID not found!")
            return False
        mask = self.df['student_id'] == student_id
        for key, value in updated_data.items():
            self.df.loc[mask, key] = value
        save_students(self.df)
        st.success("✅ Student updated successfully!")
        return True

    def delete_student(self, student_id):
        if student_id not in self.df['student_id'].astype(str).values:
            st.error("Student ID not found!")
            return False
        self.df = self.df[self.df['student_id'] != student_id]
        save_students(self.df)
        st.success("🗑️ Student deleted successfully!")
        return True

    def list_students(self, filters=None, sort_by=None, ascending=True, min_score=None):
        df_filtered = self.df.copy()
        if filters:
            for key, value in filters.items():
                if value:
                    df_filtered = df_filtered[df_filtered[key].astype(str).str.contains(str(value), case=False)]
        if min_score is not None:
            df_filtered = df_filtered[df_filtered['score'] >= min_score]
        if sort_by and sort_by in df_filtered.columns:
            df_filtered = df_filtered.sort_values(by=sort_by, ascending=ascending)
        return df_filtered

# --- STREAMLIT INTERFACE ---
manager = StudentManager()

# --- Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.title("School Admin")
    st.write("Manage your student records.")
    st.divider()
    menu = ["Home", "Add Student", "Update Student", "Delete Student", "Filter/Search"]
    choice = st.radio("Navigation", menu)
    st.divider()
    st.caption("© 2025 Student System")

# --- HOME ---
if choice == "Home":
    st.title("🎓 All Students")
    st.markdown("View all registered students.")
    df = manager.list_students()
    if df.empty:
        st.info("No students found. Go to 'Add Student' to get started!")
    else:
        st.dataframe(df, use_container_width=True)

# --- ADD STUDENT ---
elif choice == "Add Student":
    st.title("➕ Add New Student")
    with st.form(key="add_student_form"):
        col1, col2 = st.columns(2)
        with col1:
            student_id = st.text_input("Student ID 🆔")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            age = st.number_input("Age", min_value=1, max_value=150)
        with col2:
            grade = st.text_input("Grade")
            email = st.text_input("Email 📧")
            enrollment_date = st.date_input("Enrollment Date")
            score = st.slider("Score (0-100) 🎯", 0, 100, 50)
        submit = st.form_submit_button("Submit Record")
        if submit:
            if not all([student_id, first_name, last_name, grade, email]):
                st.warning("⚠️ Please fill all required fields!")
            else:
                student = Student(
                    student_id, first_name, last_name, age, grade, email,
                    enrollment_date.strftime("%Y-%m-%d"), score
                )
                manager.add_student(student)

# --- UPDATE STUDENT ---
elif choice == "Update Student":
    st.title("✏️ Update Student")
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False
        st.session_state.student_data = None
        st.session_state.current_id = None

    student_id_input = st.text_input(
        "Enter Student ID to Update",
        key="update_search_input",
        placeholder="Search by Student ID..."
    )
    if st.button("Load Student"):
        student_df = manager.df[manager.df["student_id"].astype(str) == student_id_input]
        if not student_df.empty:
            st.session_state.edit_mode = True
            st.session_state.student_data = student_df.iloc[0].to_dict()
            st.session_state.current_id = student_id_input
        else:
            st.session_state.edit_mode = False
            st.error("Student ID not found!")

    if st.session_state.edit_mode:
        s = st.session_state.student_data
        st.info(f"📝 Editing Record for: **{s['first_name']} {s['last_name']}** (ID: {s['student_id']})")
        with st.form(key="update_student_form"):
            c1, c2 = st.columns(2)
            with c1:
                first_name = st.text_input("First Name", s['first_name'])
                last_name = st.text_input("Last Name", s['last_name'])
                age = st.number_input("Age", value=int(s['age']), min_value=1, max_value=150)
                email = st.text_input("Email", s['email'])
            with c2:
                grade = st.text_input("Grade", s['grade'])
                default_date = datetime.strptime(s['enrollment_date'], "%Y-%m-%d")
                enrollment_date = st.date_input("Enrollment Date", default_date)
                score = st.slider("Score", 0, 100, int(s['score']))
            submit_update = st.form_submit_button("Save Changes")
            if submit_update:
                updated_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "age": age,
                    "grade": grade,
                    "email": email,
                    "enrollment_date": enrollment_date.strftime("%Y-%m-%d"),
                    "score": score
                }
                manager.update_student(st.session_state.current_id, updated_data)
                st.session_state.edit_mode = False
                st.session_state.student_data = None
                st.rerun()

# --- DELETE STUDENT ---
elif choice == "Delete Student":
    st.title("🗑️ Delete Student")
    st.warning("⚠️ This action cannot be undone.")
    student_id = st.text_input("Enter Student ID to Delete")
    if st.button("Delete Record"):
        manager.delete_student(student_id)

# --- FILTER/SEARCH ---
elif choice == "Filter/Search":
    st.title("🔍 Search Students")
    with st.expander("Filter Options", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1: search_id = st.text_input("Search by ID")
        with c2: search_name = st.text_input("Search by Name")
        with c3: search_grade = st.text_input("Search by Grade")
        c4, c5, c6 = st.columns(3)
        with c4: sort_by = st.selectbox("Sort By", ["", "age", "score", "enrollment_date"])
        with c5:
            order = st.radio("Order", ["Ascending", "Descending"], horizontal=True)
            ascending = order == "Ascending"
        with c6: min_score = st.slider("Minimum Score", 0, 100, 0)

    filters = {"student_id": search_id, "grade": search_grade, "first_name": search_name}
    df = manager.list_students(filters=filters, sort_by=sort_by if sort_by else None, ascending=ascending, min_score=min_score)
    st.subheader(f"Results ({len(df)})")
    if df.empty:
        st.info("No matching students found.")
    else:
        st.dataframe(df, use_container_width=True)
