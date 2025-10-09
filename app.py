import streamlit as st
import random
import time
from fpdf import FPDF
from io import BytesIO

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 1: Protocol Dataset                                │
# └────────────────────────────────────────────────────────────┘

protocols = [
    {"name": "SSH", "acronym": "SSH", "port": "22", "description": "Secure remote login", "osi_layer": 7, "difficulty": "Easy"},
    {"name": "DNS", "acronym": "DNS", "port": "53", "description": "Resolves domain names", "osi_layer": 7, "difficulty": "Easy"},
    {"name": "FTP", "acronym": "FTP", "port": "20-21", "description": "Transfers files", "osi_layer": 7, "difficulty": "Medium"},
    {"name": "SNMP", "acronym": "SNMP", "port": "161-162", "description": "Manages devices", "osi_layer": 7, "difficulty": "Medium"},
    {"name": "RIP", "acronym": "RIP", "port": "520", "description": "Routing info exchange", "osi_layer": 3, "difficulty": "Hard"},
    {"name": "ICMP", "acronym": "ICMP", "port": "0-255", "description": "Troubleshoots network issues", "osi_layer": 3, "difficulty": "Hard"},
]

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 2: Question Generator                              │
# └────────────────────────────────────────────────────────────┘

def generate_questions(data, difficulty, count):
    pool = [p for p in data if p["difficulty"] == difficulty]
    selected = random.sample(pool, min(count, len(pool)))
    questions = []

    for p in selected:
        distractors = random.sample(
            [x["acronym"] for x in data if x["acronym"] != p["acronym"]],
            min(3, len(data) - 1)
        )
        options = distractors + [p["acronym"]]
        random.shuffle(options)
        questions.append({
            "question": f"Which protocol uses port {p['port']}?",
            "answer": p["acronym"],
            "options": options,
            "description": p["description"],
            "osi_layer": p["osi_layer"],
            "port": p["port"],
            "type": "mc"
        })
    return questions

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 3: Welcome Screen                                  │
# └────────────────────────────────────────────────────────────┘

if "quiz_started" not in st.session_state:
    st.title("🧠 Network Protocol Quiz")
    st.markdown("Test your knowledge of ports, protocols, and OSI layers!")

    difficulty = st.selectbox("Choose difficulty", ["Easy", "Medium", "Hard"])
    num_questions = st.slider("Number of questions", 1, 10, 5)

    if st.button("Start Quiz"):
        st.session_state.quiz_started = True
        st.session_state.questions = generate_questions(protocols, difficulty, num_questions)
        st.session_state.current_question = 0
        st.session_state.answers = {}
        st.session_state.timer_start = time.time()
        st.session_state.difficulty = difficulty
        st.session_state.start_time = time.time()
        st.rerun()

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 4: Quiz Flow                                       │
# └────────────────────────────────────────────────────────────┘

if st.session_state.get("quiz_started") and "questions" in st.session_state:
    q_index = st.session_state.current_question
    questions = st.session_state.questions

    if q_index >= len(questions):
        st.session_state.quiz_complete = True
        st.rerun()

    question = questions[q_index]
    st.subheader(f"Question {q_index + 1} of {len(questions)}")
    st.markdown(question["question"])
    selected = st.radio("Choose your answer:", question["options"], key=f"q_{q_index}")

    elapsed = int(time.time() - st.session_state.timer_start)
    remaining = max(0, 15 - elapsed)
    st.markdown(f"⏳ Time left: `{remaining}` seconds")

    if remaining == 0:
        st.session_state.answers[q_index] = selected
        st.session_state.current_question += 1
        st.session_state.timer_start = time.time()
        st.rerun()

    if st.button("Submit", disabled=selected == ""):
        st.session_state.answers[q_index] = selected
        st.session_state.current_question += 1
        st.session_state.timer_start = time.time()
        st.rerun()

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 5: Review and Score                                │
# └────────────────────────────────────────────────────────────┘

if st.session_state.get("quiz_complete"):
    st.title("🔍 Quiz Review")
    correct = 0
    layer_map = {
        1: "Physical", 2: "Data Link", 3: "Network",
        4: "Transport", 5: "Session", 6: "Presentation", 7: "Application"
    }

    for i, q in enumerate(st.session_state.questions):
        user = st.session_state.answers.get(i, "")
        correct_answer = q["answer"]
        is_correct = user == correct_answer
        if is_correct:
            correct += 1
        st.markdown(f"**Q{i+1}: {q['question']}**")
        st.markdown(f"- Your answer: `{user}`")
        st.markdown(f"- Correct answer: `{correct_answer}`")
        st.markdown(f"- Result: {'✅ Correct' if is_correct else '❌ Incorrect'}")
        st.markdown(f"- Explanation: {q['description']}")
        st.markdown(f"- OSI Layer: {layer_map.get(q['osi_layer'], 'Unknown')} (Layer {q['osi_layer']})")
        st.markdown("---")

    st.success(f"Final Score: {correct} / {len(questions)}")
    st.session_state.correct_count = correct

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 6: PDF Export                                      │
# └────────────────────────────────────────────────────────────┘

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Network Protocol Quiz Review", ln=True, align="C")
    pdf.ln(10)

    for i, q in enumerate(st.session_state.questions):
        user = st.session_state.answers.get(i, "")
        correct_answer = q["answer"]
        result = "Correct" if user == correct_answer else "Incorrect"
        pdf.multi_cell(0, 10, txt=f"Q{i+1}: {q['question']}")
        pdf.multi_cell(0, 10, txt=f"Your Answer: {user}")
        pdf.multi_cell(0, 10, txt=f"Correct Answer: {correct_answer}")
        pdf.multi_cell(0, 10, txt=f"Result: {result}")
        pdf.multi_cell(0, 10, txt=f"Explanation: {q['description']}")
        pdf.multi_cell(0, 10, txt=f"OSI Layer: {layer_map.get(q['osi_layer'], 'Unknown')} (Layer {q['osi_layer']})")
        pdf.ln(5)

    pdf.cell(0, 10, txt=f"Final Score: {correct} / {len(questions)}", ln=True)
    buffer = BytesIO()
    buffer.write(pdf.output(dest='S').encode('latin1'))

    st.download_button("📥 Download PDF", data=buffer.getvalue(), file_name="quiz_review.pdf")

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 7: Leaderboard                                     │
# └────────────────────────────────────────────────────────────┘

    if "leaderboard" not in st.session_state:
        st.session_state.leaderboard = []

    elapsed = round(time.time() - st.session_state.start_time, 2)
    difficulty_weights = {"Easy": 1, "Medium": 2, "Hard": 3}
    score = round((correct * difficulty_weights.get(st.session_state.difficulty, 1)) / max(elapsed, 1), 4)

    st.session_state.leaderboard.append({
        "attempt": len(st.session_state.leaderboard) + 1,
        "score": score,
        "correct": correct,
        "total": len(questions),
        "time": elapsed,
        "difficulty": st.session_state.difficulty
    })

    st.session_state.leaderboard = sorted(st.session_state.leaderboard, key=lambda x: x["score"], reverse=True)[:10]

    st.markdown("## 🏆 Leaderboard (Top 10 Attempts)")
    for entry in st.session_state.leaderboard:
        st.markdown(
            f"- Attempt {entry['attempt']} | Difficulty: {entry['difficulty']} | "
            f"Score: `{entry['score']}` | Correct: {entry['correct']}/{entry['total']} | "
            f"Time: {entry['time']}s"
        )

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 8: Restart Quiz                                    │
# └────────────────────────────────────────────────────────────┘

    if st.button("🔁 Restart Quiz"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
