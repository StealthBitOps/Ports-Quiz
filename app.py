import streamlit as st
import random
import time
import json
from datetime import datetime
from fpdf import FPDF
import os

# -----------------------------
# Protocol Data
# -----------------------------
protocols = [
    {"name": "TCP", "acronym": "Transmission Control Protocol", "port": "Varies", "layer": "Transport", "reliable": True, "description": "Ensures reliable delivery of data."},
    {"name": "UDP", "acronym": "User Datagram Protocol", "port": "Varies", "layer": "Transport", "reliable": False, "description": "Faster but does not guarantee delivery."},
    {"name": "HTTP", "acronym": "HyperText Transfer Protocol", "port": "80", "layer": "Application", "reliable": True, "description": "Used for web communication."},
    {"name": "FTP", "acronym": "File Transfer Protocol", "port": "21", "layer": "Application", "reliable": True, "description": "Used for file transfers."},
    {"name": "DNS", "acronym": "Domain Name System", "port": "53", "layer": "Application", "reliable": False, "description": "Resolves domain names to IP addresses."},
    {"name": "SMTP", "acronym": "Simple Mail Transfer Protocol", "port": "25", "layer": "Application", "reliable": True, "description": "Used for sending emails."},
    {"name": "DHCP", "acronym": "Dynamic Host Configuration Protocol", "port": "67/68", "layer": "Application", "reliable": False, "description": "Assigns IP addresses dynamically."},
    {"name": "IMAP", "acronym": "Internet Message Access Protocol", "port": "143", "layer": "Application", "reliable": True, "description": "Retrieves email messages from a server."},
    {"name": "POP3", "acronym": "Post Office Protocol 3", "port": "110", "layer": "Application", "reliable": True, "description": "Downloads email messages to a local device."},
    {"name": "SNMP", "acronym": "Simple Network Management Protocol", "port": "161", "layer": "Application", "reliable": False, "description": "Monitors and manages network devices."}
]

# -----------------------------
# Question Generator
# -----------------------------
def generate_questions(difficulty, num_questions):
    used = set()
    questions = []

    while len(questions) < num_questions:
        available = [p for p in protocols if p["name"] not in used]
        if not available:
            break
        proto = random.choice(available)
        used.add(proto["name"])

        if difficulty == "Easy":
            q_type = "mc"
        elif difficulty == "Medium":
            q_type = random.choice(["mc", "fill"])
        else:
            q_type = random.choice(["fill", "tf", "layer", "acronym"])

        if q_type == "mc":
            options = random.sample([p["name"] for p in protocols if p["name"] != proto["name"]], 3)
            options.append(proto["name"])
            random.shuffle(options)
            explanations = {opt: next((p["description"] for p in protocols if p["name"] == opt), "No info") for opt in options}
            questions.append({
                "type": "mc",
                "question": f"Which protocol matches this description: '{proto['description']}'?",
                "options": options,
                "answer": proto["name"],
                "explanations": explanations
            })
        elif q_type == "fill":
            questions.append({
                "type": "fill",
                "question": f"Which protocol uses port {proto['port']}?",
                "answer": proto["name"],
                "explanation": f"{proto['name']} uses port {proto['port']} for {proto['description']}."
            })
        elif q_type == "layer":
            questions.append({
                "type": "fill",
                "question": f"Which layer does {proto['name']} operate on?",
                "answer": proto["layer"],
                "explanation": f"{proto['name']} operates on the {proto['layer']} layer."
            })
        elif q_type == "acronym":
            questions.append({
                "type": "fill",
                "question": f"What does the acronym {proto['name']} stand for?",
                "answer": proto["acronym"],
                "explanation": f"{proto['name']} stands for {proto['acronym']}."
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
# Leaderboard Functions
# -----------------------------
def load_leaderboard():
    if os.path.exists("leaderboard.json"):
        with open("leaderboard.json", "r") as f:
            return json.load(f)
    return []

def save_leaderboard(data):
    with open("leaderboard.json", "w") as f:
        json.dump(data, f, indent=2)

def update_leaderboard(name, score, time_taken):
    board = load_leaderboard()
    board.append({"name": name, "score": score, "time": round(time_taken, 2)})
    board.sort(key=lambda x: (-x["score"], x["time"]))
    save_leaderboard(board)
    return board

# -----------------------------
# PDF Generator
# -----------------------------
def generate_pdf(results, score, total, difficulty, name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    pdf.cell(200, 10, txt=f"{name}'s Quiz Results", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Score: {score}/{total} | Difficulty: {difficulty} | {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
    pdf.ln(10)
    for i, r in enumerate(results):
        pdf.multi_cell(0, 10, txt=f"Q{i+1}: {r['question']}")
        pdf.multi_cell(0, 10, txt=f"Your answer: {r['user_answer']}")
        pdf.multi_cell(0, 10, txt=f"Correct answer: {r['answer']}")
        if r["type"] == "mc":
            for opt, exp in r["explanations"].items():
                pdf.multi_cell(0, 10, txt=f"- {opt}: {exp}")
        else:
            pdf.multi_cell(0, 10, txt=f"Explanation: {r['explanation']}")
        pdf.ln(5)
    pdf.output("quiz_results.pdf")

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🧠 TCP/UDP Protocol Quiz")

name = st.text_input("Enter your name to begin:")
difficulty = st.select_slider("Select difficulty", options=["Easy", "Medium", "Hard"], value="Medium")
num_questions = st.slider("Number of questions", 3, len(protocols), 5)

if st.button("Generate Quiz") and name:
    st.session_state.questions = generate_questions(difficulty, num_questions)
    st.session_state.answers = {}
    st.session_state.submitted = False
    st.session_state.start_time = time.time()

if "questions" in st.session_state and not st.session_state.submitted:
    st.subheader("Answer the questions:")
    for i, q in enumerate(st.session_state.questions):
        st.markdown(f"**Q{i+1}: {q['question']}**")
        key = f"q_{i}"
        placeholder = st.empty()
        for sec in range(10, 0, -1):
            placeholder.markdown(f"⏳ Time left: {sec} seconds")
            time.sleep(1)
        placeholder.empty()
        if q["type"] == "mc":
            st.session_state.answers[key] = st.radio("Choose one:", q["options"], key=key)
        elif q["type"] == "tf":
            st.session_state.answers[key] = st.radio("True or False:", ["True", "False"], key=key)
        else:
            st.session_state.answers[key] = st.text_input("Your answer:", key=key)

    if st.button("Submit Quiz"):
        score = 0
        results = []
        end_time = time.time()
        total_time = end_time - st.session_state.start_time

        for i, q in enumerate(st.session_state.questions):
            user_answer = st.session_state.answers.get(f"q_{i}", "")
            correct = user_answer.strip().lower() == q["answer"].strip().lower()
            if correct:
                score += 1
            result = {
                "question": q["question"],
                "user_answer": user_answer,
                "answer": q["answer"],
                "type": q["type"]
            }
            if q["type"] == "mc":
                result["explanations"] = q["explanations"]
            else:
                result["explanation"] = q["explanation"]
            results.append(result)

        st.session_state.submitted = True
        st.success(f"✅ {name}, you scored {score} out of {len(st.session_state.questions)} in {round(total_time, 2)} seconds")

        for r in results:
            st.markdown(f"**Q:** {r['question']}")
            st.markdown(f"- Your answer: `{r['user_answer']}`")
            st.markdown(f"- Correct answer: `{r['answer']}`")
            if r["type"] == "mc":
                st.markdown("**Option explanations:**")
                for opt, exp in r["explanations"].items():
                    st.markdown(f"- `{opt}`: {exp}")
            else:
                st.markdown(f"- Explanation: {r['explanation']}")
            st.markdown("---")

        generate_pdf(results, score, len(st.session_state.questions), difficulty, name)
        with open("quiz_results.pdf", "rb") as f:
            st.download_button("📄 Download PDF Results", f, file_name="quiz_results.pdf")

        leaderboard = update_leaderboard(name, score, total_time)
        st.subheader("🏆 Leaderboard")
        for i, entry in enumerate(leaderboard[:10], start=1):
            st.markdown(f"{i}. **{entry['name']}** — {entry['score']} pts in {entry['time']}s")

if st.button("Start Over"):
    st.session_state.clear()
    st.experimental_rerun()
