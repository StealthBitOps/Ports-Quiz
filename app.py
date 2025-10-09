# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 1: Imports and Setup                               │
# └────────────────────────────────────────────────────────────┘

import streamlit as st
import random
import time
from io import BytesIO
from fpdf import FPDF
import unicodedata

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 2: Protocol Dataset                                │
# └────────────────────────────────────────────────────────────┘

protocols = [
    {"name": "SSH", "acronym": "SSH", "port": "22", "description": "Secure remote login", "osi_layer": 7, "difficulty": "Easy"},
    {"name": "DNS", "acronym": "DNS", "port": "53", "description": "Resolves domain names", "osi_layer": 7, "difficulty": "Easy"},
    {"name": "FTP", "acronym": "FTP", "port": "20-21", "description": "Transfers files", "osi_layer": 7, "difficulty": "Medium"},
    {"name": "SNMP", "acronym": "SNMP", "port": "161-162", "description": "Manages devices", "osi_layer": 7, "difficulty": "Medium"},
    {"name": "RIP", "acronym": "RIP", "port": "520", "description": "Routing info exchange", "osi_layer": 3, "difficulty": "Hard"},
    {"name": "ICMP", "acronym": "ICMP", "port": "0-255", "description": "Troubleshoots network issues", "osi_layer": 3, "difficulty": "Hard"},
]

def sanitize(text):
    return unicodedata.normalize("NFKD", text).encode("latin1", "ignore").decode("latin1")

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 3: Question Generator                              │
# └────────────────────────────────────────────────────────────┘

def generate_questions(data, difficulty, count):
    pool = [p for p in data if p["difficulty"] == difficulty]
    selected = random.sample(pool, min(count, len(pool)))
    questions = []

    for p in selected:
        qtype = "mc" if difficulty == "Easy" else random.choice(["mc", "tf", "fill"])
        if qtype == "mc":
            distractors = random.sample(
                [x["acronym"] for x in data if x["acronym"] != p["acronym"]],
                min(3, len(data) - 1)
            )
            questions.append({
                "question": f"Which protocol uses port {p['port']}?",
                "answer": p["acronym"],
                "type": "mc",
                "options": distractors + [p["acronym"]],
                "explanation": f"{p['acronym']} uses port {p['port']} — {p['description']}.",
                "osi_layer": p["osi_layer"],
                "port": p["port"],
                "description": p["description"]
            })
        elif qtype == "tf":
            is_true = random.choice([True, False])
            fact = f"{p['acronym']} uses port {p['port']}" if is_true else f"{p['acronym']} uses port 9999"
            questions.append({
                "question": f"True or False: {fact}",
                "answer": "True" if is_true else "False",
                "type": "tf",
                "explanation": f"{'Correct' if is_true else 'Incorrect'} — {p['description']}.",
                "osi_layer": p["osi_layer"],
                "port": p["port"],
                "description": p["description"]
            })
        else:
            questions.append({
                "question": f"Fill in: Which protocol uses port {p['port']}?",
                "answer": p["acronym"],
                "type": "fill",
                "explanation": f"{p['acronym']} uses port {p['port']} — {p['description']}.",
                "osi_layer": p["osi_layer"],
                "port": p["port"],
                "description": p["description"]
            })

    return questions

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 4: Welcome Screen and Quiz Setup                   │
# └────────────────────────────────────────────────────────────┘

if "quiz_started" not in st.session_state:
    st.title("🧠 Network Protocol Quiz")
    st.markdown("Test your knowledge of ports, protocols, and OSI layers!")

    # Difficulty and question count selectors
    difficulty = st.select_slider("Choose difficulty", options=["Easy", "Medium", "Hard"])
    num_questions = st.slider("How many questions?", min_value=1, max_value=20, value=5)

    # Start Quiz button
    if st.button("Start Quiz"):
        st.session_state.difficulty = difficulty
        st.session_state.num_questions = num_questions
        st.session_state.questions = generate_questions(protocols, difficulty, num_questions)
        st.session_state.current_question = 0
        st.session_state.answers = {}
        st.session_state.quiz_started = True
        st.session_state.quiz_complete = False
        st.session_state.ready_for_review = False
        st.session_state.start_time = time.time()
        st.rerun()
# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 5: Quiz Flow with Countdown Timer and Submit Logic │
# └────────────────────────────────────────────────────────────┘

if st.session_state.get("quiz_started") and not st.session_state.get("quiz_complete"):
    q_index = st.session_state.current_question
    questions = st.session_state.questions

    if q_index >= len(questions):
        st.session_state.ready_for_review = True
        st.rerun()

    question = questions[q_index]
    key = f"q_{q_index}"

    # Initialize per-question state
    if f"submitted_{key}" not in st.session_state:
        st.session_state[f"submitted_{key}"] = False
        st.session_state[f"answer_{key}"] = ""
        st.session_state[f"timer_start_{key}"] = time.time()

    # Display question
    st.markdown(f"### Question {q_index + 1} of {st.session_state.num_questions}")
    if question["type"] == "mc":
        st.radio(question["question"], question["options"], key=f"input_{key}")
    elif question["type"] == "tf":
        st.radio(question["question"], ["True", "False"], key=f"input_{key}")
    else:
        st.text_input(question["question"], key=f"input_{key}")

    selected = st.session_state.get(f"input_{key}", "")
    st.session_state[f"answer_{key}"] = selected

    # Countdown timer
    if not st.session_state[f"submitted_{key}"]:
        elapsed = int(time.time() - st.session_state[f"timer_start_{key}"])
        remaining = max(0, 10 - elapsed)
        st.markdown(f"⏳ Time remaining: `{remaining}` seconds")

        if remaining > 0:
            time.sleep(1)
            st.rerun()
        else:
            # Auto-submit if time runs out
            st.session_state.answers[key] = selected
            st.session_state[f"submitted_{key}"] = True
            st.session_state.current_question += 1
            st.rerun()

    # Submit button
    if not st.session_state[f"submitted_{key}"]:
        submit_disabled = selected is None or selected == ""
        if st.button("Submit", disabled=submit_disabled, key=f"submit_{key}"):
            st.session_state.answers[key] = selected
            st.session_state[f"submitted_{key}"] = True
            st.session_state.current_question += 1
            st.rerun()

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 6: Review Trigger and Review Screen                │
# └────────────────────────────────────────────────────────────┘

if st.session_state.get("ready_for_review") and not st.session_state.get("quiz_complete"):
    st.markdown("## ✅ Quiz Complete")
    st.markdown("You've answered all questions. Click below to review your results.")
    if st.button("Review Quiz"):
        st.session_state.quiz_complete = True
        st.rerun()

if st.session_state.get("quiz_complete"):
    st.markdown("## 🔍 Quiz Review")
    correct_count = 0
    layer_map = {
        1: "Physical", 2: "Data Link", 3: "Network",
        4: "Transport", 5: "Session", 6: "Presentation", 7: "Application"
    }

    for i, q in enumerate(st.session_state.questions):
        key = f"q_{i}"
        user_answer = st.session_state.answers.get(key, "")
        correct_answer = q["answer"]
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()

        st.markdown(f"### Question {i+1}")
        st.markdown(f"**Question:** {q['question']}")
        st.markdown(f"**Your Answer:** `{user_answer}`")
        st.markdown(f"**Correct Answer:** `{correct_answer}`")
        st.markdown(f"**Result:** {'✅ Correct' if is_correct else '❌ Incorrect'}")
        st.markdown(f"**Explanation:** {q['explanation']}")
        st.markdown(f"**Port(s):** {q['port']}")
        st.markdown(f"**Protocol Description:** {q['description']}")
        st.markdown(f"**OSI Layer:** {layer_map.get(q['osi_layer'], 'Unknown')} (Layer {q['osi_layer']})")
        st.markdown(f"**Question Type:** {q['type'].upper()}")
        st.markdown("---")

        if is_correct:
            correct_count += 1

    st.session_state.correct_count = correct_count
    st.markdown(f"### 🧮 Final Score: `{correct_count}` out of `{len(st.session_state.questions)}`")

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 7: PDF Export                                      │
# └────────────────────────────────────────────────────────────┘

if st.session_state.get("quiz_complete"):
    st.markdown("## 📄 Export Your Review")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Network Protocol Quiz Review", ln=True, align="C")
    pdf.ln(10)

    layer_map = {
        1: "Physical", 2: "Data Link", 3: "Network",
        4: "Transport", 5: "Session", 6: "Presentation", 7: "Application"
    }

    for i, q in enumerate(st.session_state.questions):
        key = f"q_{i}"
        user_answer = st.session_state.answers.get(key, "")
        correct_answer = q["answer"]
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
        result = "Correct" if is_correct else "Incorrect"

        pdf.multi_cell(0, 10, txt=sanitize(f"Q{i+1}: {q['question']}"))
        pdf.multi_cell(0, 10, txt=sanitize(f"Your Answer: {user_answer}"))
        pdf.multi_cell(0, 10, txt=sanitize(f"Correct Answer: {correct_answer}"))
        pdf.multi_cell(0, 10, txt=sanitize(f"Result: {result}"))
        pdf.multi_cell(0, 10, txt=sanitize(f"Explanation: {q['explanation']}"))
        pdf.multi_cell(0, 10, txt=sanitize(f"Port(s): {q['port']}"))
        pdf.multi_cell(0, 10, txt=sanitize(f"Protocol Description: {q['description']}"))
        pdf.multi_cell(0, 10, txt=sanitize(f"OSI Layer: {layer_map.get(q['osi_layer'], 'Unknown')} (Layer {q['osi_layer']})"))
        pdf.multi_cell(0, 10, txt=sanitize(f"Question Type: {q['type'].upper()}"))
        pdf.ln(5)

    pdf.ln(10)
    pdf.cell(0, 10, txt=sanitize(f"Final Score: {st.session_state.correct_count} / {len(st.session_state.questions)}"), ln=True)

    buffer = BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin1')
    buffer.write(pdf_output)

    st.download_button("📥 Download PDF", data=buffer.getvalue(), file_name="quiz_review.pdf")

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 8: Leaderboard                                     │
# └────────────────────────────────────────────────────────────┘

if st.session_state.get("quiz_complete"):
    if "leaderboard" not in st.session_state:
        st.session_state.leaderboard = []
    if "attempt_count" not in st.session_state:
        st.session_state.attempt_count = 0

    elapsed = round(time.time() - st.session_state.get("start_time", time.time()), 2)
    difficulty = st.session_state.get("difficulty", "Easy")
    difficulty_weights = {"Easy": 1, "Medium": 2, "Hard": 3}
    score = round((st.session_state.correct_count * difficulty_weights.get(difficulty, 1)) / max(elapsed, 1), 4)

    st.session_state.attempt_count += 1
    attempt_name = f"Attempt {st.session_state.attempt_count}"
    total_questions = len(st.session_state.questions)

    st.session_state.leaderboard.append({
        "name": attempt_name,
        "difficulty": difficulty,
        "correct": st.session_state.correct_count,
        "total": total_questions,
        "time": elapsed,
        "score": score
    })

    st.session_state.leaderboard = sorted(
        st.session_state.leaderboard,
        key=lambda x: x["score"],
        reverse=True
    )[:10]

    st.markdown("## 🏆 Leaderboard (Top 10 Attempts)")
    for entry in st.session_state.leaderboard:
        st.markdown(
            f"- **{entry['name']}** | Difficulty: {entry['difficulty']} | "
            f"Score: `{entry['score']}` | Correct: {entry['correct']}/{entry['total']} | "
            f"Time: {entry['time']}s"
        )

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 9: Restart Quiz Button                             │
# └────────────────────────────────────────────────────────────┘

if st.session_state.get("quiz_complete"):
    if st.button("🔁 Restart Quiz"):
        for key in list(st.session_state.keys()):
            if key.startswith("q_") or key.startswith("input_") or key.startswith("submitted_") or key.startswith("answer_") or key.startswith("timer_") or key.startswith("timer_start_"):
                del st.session_state[key]
        for flag in ["questions", "answers", "current_question", "quiz_complete", "quiz_started", "ready_for_review", "correct_count", "start_time", "difficulty", "num_questions"]:
            st.session_state.pop(flag, None)
        st.rerun()
