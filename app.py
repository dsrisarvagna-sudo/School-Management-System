import streamlit as st
import json
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import date

# ----------------------------------------------------------------------
# Persistence layer (same JSON-file approach as the original script)
# ----------------------------------------------------------------------
DB = "school_data.json"


def load_data():
    if Path(DB).exists():
        with open(DB, "r") as f:
            c = f.read()
            if c:
                return json.loads(c)
    return {"students": [], "teachers": []}


def save_data(data):
    with open(DB, "w") as f:
        json.dump(data, f, indent=4)


if "data" not in st.session_state:
    st.session_state.data = load_data()


# ----------------------------------------------------------------------
# Domain model (kept close to the original OOP structure)
# ----------------------------------------------------------------------
class Person(ABC):
    @abstractmethod
    def get_role(self):
        pass

    @abstractmethod
    def register(self, **kwargs):
        pass

    @staticmethod
    def validate_email(e):
        return "@" in e and "." in e


class Student(Person):
    def get_role(self):
        return "student"

    def register(self, name, age, email, roll):
        data = st.session_state.data
        if not Person.validate_email(email):
            return False, "That email doesn't look right — check for the @ and a domain."
        for s in data["students"]:
            if s["roll_no"] == roll:
                return False, f"Roll number {roll} is already on the register."
        data["students"].append(
            {"name": name, "age": age, "email": email, "roll_no": roll, "grades": {}}
        )
        save_data(data)
        return True, f"{name} added to the student register."

    def add_grade(self, roll_no, subject, marks):
        data = st.session_state.data
        for s in data["students"]:
            if s["roll_no"] == roll_no:
                s["grades"][subject] = marks
                save_data(data)
                return True, f"{subject} grade recorded for roll {roll_no}."
        return False, "No student found with that roll number."


class Teacher(Person):
    def get_role(self):
        return "teacher"

    def register(self, name, age, email, subject, emp_id):
        data = st.session_state.data
        if not Person.validate_email(email):
            return False, "That email doesn't look right — check for the @ and a domain."
        for t in data["teachers"]:
            if t["emp_id"] == emp_id:
                return False, f"Employee ID {emp_id} is already on the register."
        data["teachers"].append(
            {"name": name, "age": age, "email": email, "subject": subject, "emp_id": emp_id}
        )
        save_data(data)
        return True, f"{name} added to the teacher register."


student_handler = Student()
teacher_handler = Teacher()


# ----------------------------------------------------------------------
# Page setup + theme
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="School Management System",
    page_icon="🏫",
    layout="wide"
)

st.markdown("""
<style>
.main {
    background-color: #f8f9fa;
}

h1, h2, h3 {
    color: #1f4e79;
}

[data-testid="stSidebar"] {
    background-color: #1f4e79;
}

[data-testid="stSidebar"] * {
    color: white;
}

.stButton > button {
    background-color: #1f4e79;
    color: white;
    border-radius: 10px;
    border: none;
}

.stButton > button:hover {
    background-color: #2f6fa5;
}
</style>
""", unsafe_allow_html=True)

def ledger_header(title, subtitle):
    st.markdown(
        f"""
        <div class="ledger-head">
            <div class="ledger-title">{title}</div>
            <div class="ledger-stamp">{subtitle} · {date.today().strftime('%d %b %Y')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def feedback(ok, msg):
    if ok:
        st.success(msg)
    else:
        st.error(msg)


# ----------------------------------------------------------------------
# Sidebar navigation
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sb-crest">The Register</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-sub">School Record Book</div>', unsafe_allow_html=True)
    st.write("")
    page = st.radio(
        "Navigate",
        [
            "Register Student",
            "Register Teacher",
            "Student Roll",
            "Teacher Roll",
            "Record a Grade",
        ],
        label_visibility="collapsed",
    )
    st.write("")
    st.markdown(
        f'<div class="sb-sub">On file: {len(st.session_state.data["students"])} students · '
        f'{len(st.session_state.data["teachers"])} teachers</div>',
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------
# Pages
# ----------------------------------------------------------------------
if page == "Register Student":
    ledger_header("New Student Entry", "Register · Students")
    with st.form("student_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full name")
            email = st.text_input("Email")
        with c2:
            age = st.number_input("Age", min_value=4, max_value=100, step=1)
            roll = st.text_input("Roll number")
        submitted = st.form_submit_button("Add to register")
    if submitted:
        if not name or not email or not roll:
            st.error("All fields are required before this entry can be filed.")
        else:
            ok, msg = student_handler.register(name, int(age), email, roll)
            feedback(ok, msg)

elif page == "Register Teacher":
    ledger_header("New Teacher Entry", "Register · Teachers")
    with st.form("teacher_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full name")
            email = st.text_input("Email")
            subject = st.text_input("Subject taught")
        with c2:
            age = st.number_input("Age", min_value=18, max_value=100, step=1)
            emp_id = st.text_input("Employee ID")
        submitted = st.form_submit_button("Add to register")
    if submitted:
        if not name or not email or not subject or not emp_id:
            st.error("All fields are required before this entry can be filed.")
        else:
            ok, msg = teacher_handler.register(name, int(age), email, subject, emp_id)
            feedback(ok, msg)

elif page == "Student Roll":
    ledger_header("Student Roll", f"{len(st.session_state.data['students'])} on file")
    students = st.session_state.data["students"]
    if not students:
        st.markdown('<div class="empty-note">No students have been registered yet.</div>', unsafe_allow_html=True)
    else:
        cols = st.columns(3)
        for i, s in enumerate(students):
            grade_tags = "".join(
                f'<span class="tag">{subj}: {mark}</span>' for subj, mark in s["grades"].items()
            ) or '<span class="tag">no grades yet</span>'
            with cols[i % 3]:
                st.markdown(
                    f"""
                    <div class="card">
                        <div class="card-top">
                            <div class="badge">S</div>
                            <div>
                                <div class="card-name">{s['name']}</div>
                                <div class="card-meta">roll {s['roll_no']} · age {s['age']}</div>
                            </div>
                        </div>
                        <div class="card-meta">{s['email']}</div>
                        <div>{grade_tags}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

elif page == "Teacher Roll":
    ledger_header("Teacher Roll", f"{len(st.session_state.data['teachers'])} on file")
    teachers = st.session_state.data["teachers"]
    if not teachers:
        st.markdown('<div class="empty-note">No teachers have been registered yet.</div>', unsafe_allow_html=True)
    else:
        cols = st.columns(3)
        for i, t in enumerate(teachers):
            with cols[i % 3]:
                st.markdown(
                    f"""
                    <div class="card">
                        <div class="card-top">
                            <div class="badge">T</div>
                            <div>
                                <div class="card-name">{t['name']}</div>
                                <div class="card-meta">id {t['emp_id']} · age {t['age']}</div>
                            </div>
                        </div>
                        <div class="card-meta">{t['email']}</div>
                        <div><span class="tag">{t['subject']}</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

elif page == "Record a Grade":
    ledger_header("Record a Grade", "Student Roll · Grades")
    students = st.session_state.data["students"]
    if not students:
        st.markdown('<div class="empty-note">Register a student first — there\'s no one to grade yet.</div>', unsafe_allow_html=True)
    else:
        roll_options = {f"{s['name']} (roll {s['roll_no']})": s["roll_no"] for s in students}
        with st.form("grade_form", clear_on_submit=True):
            choice = st.selectbox("Student", list(roll_options.keys()))
            c1, c2 = st.columns(2)
            with c1:
                subject = st.text_input("Subject")
            with c2:
                marks = st.number_input("Marks", min_value=0.0, max_value=100.0, step=0.5)
            submitted = st.form_submit_button("Record grade")
        if submitted:
            if not subject:
                st.error("Enter a subject before recording the grade.")
            else:
                ok, msg = student_handler.add_grade(roll_options[choice], subject, marks)
                feedback(ok, msg)