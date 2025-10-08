# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 1: Imports and Protocol Dataset                    │
# └────────────────────────────────────────────────────────────┘

import streamlit as st
import random
import time
from io import BytesIO
from fpdf import FPDF

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
# │ SECTION 3: Welcome Screen and Quiz Setup                   │
# └────────────────────────────────────────────────────────────┘

if "questions" not in st.session_state or st.session_state.get("quiz_complete"):
    st.title("🧠 Network Protocol Quiz")
    st.markdown("Test your knowledge of ports, protocols, and OSI layers!")

    difficulty = st.select_slider("Choose difficulty", options=["Easy", "Medium", "Hard"])
    num_questions = st.slider("How many questions?", min_value=1, max_value=20, value=5)

    if st.button("Start Quiz"):
        st.session_state.difficulty = difficulty
        st.session_state.num_questions = num_questions
        st.session_state.current_question = 0
        st.session_state.answers = {}
        st.session_state.start_time = time.time()
        st.session_state.questions = generate_questions(protocols, difficulty, num_questions)
        st.session_state.quiz_complete = False
        st.rerun()

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 4: Quiz Flow with Timer and Conditional Buttons    │
# └────────────────────────────────────────────────────────────┘

if "questions" in st.session_state and not st.session_state.quiz_complete:
    q_index = st.session_state.current_question
    question = st.session_state.questions[q_index]
    key = f"q_{q_index}"

    # Initialize timer and state
    if f"timer_{key}" not in st.session_state:
        st.session_state[f"timer_{key}"] = 10
        st.session_state[f"submitted_{key}"] = False
        st.session_state[f"timeout_{key}"] = False
        st.session_state[f"answer_{key}"] = ""

    # Display question and timer
    st.markdown(f"### Question {q_index + 1} of {st.session_state.num_questions}")
    st.markdown(f"⏳ Time remaining: `{st.session_state[f'timer_{key}']}` seconds")

    # Show question and capture answer
    if question["type"] == "mc":
        selected = st.radio(question["question"], question["options"], key=f"input_{key}")
    elif question["type"] == "tf":
        selected = st.radio(question["question"], ["True", "False"], key=f"input_{key}")
    else:
        selected = st.text_input(question["question"], key=f"input_{key}")

    st.session_state[f"answer_{key}"] = selected

    # Countdown logic
    if st.session_state[f"timer_{key}"] > 0 and not st.session_state[f"submitted_{key}"]:
        time.sleep(1)
        st.session_state[f"timer_{key}"] -= 1
        st.rerun()

    # Timeout reached
    if st.session_state[f"timer_{key}"] == 0 and not st.session_state[f"submitted_{key}"]:
        st.session_state.answers[key] = selected or ""
        st.session_state[f"timeout_{key}"] = True
        st.markdown("⏱️ Time's up! Answer saved. Click **Next** to continue.")

    # Submit button (always visible, disabled until answer is selected, hidden after timeout)
    if not st.session_state[f"timeout_{key}"]:
        submit_disabled = not selected or st.session_state[f"submitted_{key}"]
        if st.button("Submit", disabled=submit_disabled):
            st.session_state.answers[key] = selected
            st.session_state[f"submitted_{key}"] = True
            st.session_state.current_question += 1
            if st.session_state.current_question >= st.session_state.num_questions:
                st.session_state.quiz_complete = True
            st.rerun()

    # Next button (only after timeout)
    if st.session_state[f"timeout_{key}"]:
        if st.button("Next"):
            st.session_state.current_question += 1
            if st.session_state.current_question >= st.session_state.num_questions:
                st.session_state.quiz_complete = True
            st.rerun()

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 5: Review Screen                                   │
# └────────────────────────────────────────────────────────────┘

correct_count = 0

if "questions" in st.session_state and st.session_state.get("quiz_complete"):
    st.markdown("## 🔍 Quiz Review")

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

    st.markdown(f"### 🧮 Final Score: {correct_count} / {len(st.session_state.questions)}")
    st.session_state.correct_count = correct_count

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 6: PDF Export                                      │
# └────────────────────────────────────────────────────────────┘

if st.session_state.get("quiz_complete"):
    st.markdown("## 📄 Export Your Review")
    st.markdown("Click the button below to download a PDF summary of your quiz results.")

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

        pdf.multi_cell(0, 10, txt=f"Q{i+1}: {q['question']}")
        pdf.multi_cell(0, 10, txt=f"Your Answer: {user_answer}")
        pdf.multi_cell(0, 10, txt=f"Correct Answer: {correct_answer}")
        pdf.multi_cell(0, 10, txt=f"Result: {result}")
        pdf.multi_cell(0, 10, txt=f"Explanation: {q['explanation']}")
        pdf.multi_cell(0, 10, txt=f"Port(s): {q['port']}")
        pdf.multi_cell(0, 10, txt=f"Protocol Description: {q['description']}")
        pdf.multi_cell(0, 10, txt=f"OSI Layer: {layer_map.get(q['osi_layer'], 'Unknown')} (Layer {q['osi_layer']})")
        pdf.multi_cell(0, 10, txt=f"Question Type: {q['type'].upper()}")
        pdf.ln(5)

    pdf.ln(10)
    pdf.cell(0, 10, txt=f"Final Score: {st.session_state.correct_count} / {len(st.session_state.questions)}", ln=True)

    buffer = BytesIO()
    pdf.output(buffer)
    st.download_button("📥 Download PDF", data=buffer.getvalue(), file_name="quiz_review.pdf")

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 7: Leaderboard                                     │
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
# │ SECTION 8: Restart Quiz Button                             │
# └────────────────────────────────────────────────────────────┘

if st.session_state.get("quiz_complete"):
    if st.button("🔁 Restart Quiz"):
        for key in list(st.session_state.keys()):
            if key.startswith("q_") or key.startswith("timer_") or key.startswith("submitted_") or key.startswith("timeout_") or key.startswith("answer_"):
                del st.session_state[key]
        st.session_state.pop("questions", None)
        st.session_state.pop("answers", None)
        st.session_state.pop("current_question", None)
        st.session_state.pop("quiz_complete", None)
        st.session_state.pop("correct_count", None)
        st.session_state.pop("start_time", None)
        st.rerun()


