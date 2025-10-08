import streamlit as st
from fpdf import FPDF
from datetime import datetime
import random

# -----------------------------
# Quiz Data
# -----------------------------
protocols = [
    {"name": "TCP", "type": "Connection-oriented", "port": "Varies", "reliable": True, "description": "Ensures reliable delivery of data."},
    {"name": "UDP", "type": "Connectionless", "port": "Varies", "reliable": False, "description": "Faster but does not guarantee delivery."},
    {"name": "HTTP", "type": "Application layer", "port": "80", "reliable": True, "description": "Used for web communication."},
    {"name": "FTP", "type": "Application layer", "port": "21", "reliable": True, "description": "Used for file transfers."},
    {"name": "DNS", "type": "Application layer", "port": "53", "reliable": False, "description": "Resolves domain names to IP addresses."},
    {"name": "SMTP", "type": "Application layer", "port": "25", "reliable": True, "description": "Used for sending emails."},
    {"name": "DHCP", "type": "Application layer", "port": "67/68", "reliable": False, "description": "Assigns IP addresses dynamically."},
]

# -----------------------------
# Question Generator
# -----------------------------
def generate_questions(difficulty, num_questions):
    used_protocols = set()
    questions = []

    while len(questions) < num_questions:
        available = [p for p in protocols if p["name"] not in used_protocols]
        if not available:
            break
        proto = random.choice(available)
        used_protocols.add(proto["name"])

        if difficulty == "Easy":
            q_type = "mc"
        elif difficulty == "Medium":
            q_type = random.choice(["mc", "fill"])
        else:
            q_type = random.choice(["fill", "tf"])

        if q_type == "mc":
            options = random.sample([p["name"] for p in protocols if p["name"] != proto["name"]], 3)
            options.append(proto["name"])
            random.shuffle(options)
            explanation = f"{proto['name']} is correct because: {proto['description']}. Other options do not match this description."
            questions.append({
                "type": "mc",
                "question": f"Which protocol matches this description: '{proto['description']}'?",
                "options": options,
                "answer": proto["name"],
                "explanation": explanation
            })
        elif q_type == "fill":
            explanation = f"{proto['name']} uses port {proto['port']}, which is unique to its function."
            questions.append({
                "type": "fill",
                "question": f"Which protocol uses port {proto['port']}?",
                "answer": proto["name"],
                "explanation": explanation
            })
        else:
            statement = f"{proto['name']} is {'reliable' if proto['reliable'] else 'unreliable'}."
            correct = "True" if proto['reliable'] else "False"
            explanation = f"{proto['name']} is {'reliable' if proto['reliable'] else 'not reliable'} because it {'ensures' if proto['reliable'] else 'does not guarantee'} delivery."
            questions.append({
                "type": "tf",
                "question": f"True or False: {statement}",
                "answer": correct,
                "explanation": explanation
            })

    return questions

# -----------------------------
# PDF Generator
# -----------------------------
def generate_pdf(results, score, total, difficulty):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    pdf.cell(200, 10, txt="Quiz Results", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Score: {score}/{total} | Difficulty: {difficulty} | {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
    pdf.ln(10)
    for i, r in enumerate(results):
        pdf.multi_cell(0, 10, txt=f"Q{i+1}: {r['question']}")
        pdf.multi_cell(0, 10, txt=f"Your answer: {r['user_answer']}")
        pdf.multi_cell(0, 10, txt=f"Correct answer: {r['answer']}")
        pdf.multi_cell(0, 10, txt=f"Explanation: {r['explanation']}")
        pdf.ln(5)
    pdf.output("quiz_results.pdf")

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🧠 TCP/UDP Protocol Quiz")

difficulty = st.select_slider("Select difficulty", options=["Easy", "Medium", "Hard"])
num_questions = st.slider("Number of questions", 3, 7, 5)

if "questions" not in st.session_state:
    st.session_state.questions = generate_questions(difficulty, num_questions)
    st.session_state.answers = {}

questions = st.session_state.questions

st.subheader("Answer the questions:")

for i, q in enumerate(questions):
    st.markdown(f"**Q{i+1}: {q['question']}**")
    key = f"q_{i}"
    if q["type"] == "mc":
        st.session_state.answers[key] = st.radio("Choose one:", q["options"], key=key)
    elif q["type"] == "tf":
        st.session_state.answers[key] = st.radio("True or False:", ["True", "False"], key=key)
    else:
        st.session_state.answers[key] = st.text_input("Your answer:", key=key)

if st.button("Submit Quiz"):
    score = 0
    results = []
    for i, q in enumerate(questions):
        user_answer = st.session_state.answers.get(f"q_{i}", "")
        correct = user_answer.strip().lower() == q["answer"].strip().lower()
        if correct:
            score += 1
        results.append({
            "question": q["question"],
            "user_answer": user_answer,
            "answer": q["answer"],
            "explanation": q["explanation"]
        })
    st.success(f"✅ You scored {score} out of {len(questions)}")
    for r in results:
        st.markdown(f"**Q:** {r['question']}")
        st.markdown(f"- Your answer: `{r['user_answer']}`")


