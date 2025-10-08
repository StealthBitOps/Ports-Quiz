# ┌───────────────────────────────────────────────┐
# │ SECTION 1: Imports and Protocol Dataset       │
# └───────────────────────────────────────────────┘

import streamlit as st
import random
import time

protocols = [
    {"name": "SSH", "acronym": "SSH", "port": "22", "description": "Secure remote login", "osi_layer": 7, "difficulty": "Easy"},
    {"name": "DNS", "acronym": "DNS", "port": "53", "description": "Resolves domain names", "osi_layer": 7, "difficulty": "Easy"},
    {"name": "FTP", "acronym": "FTP", "port": "20-21", "description": "Transfers files", "osi_layer": 7, "difficulty": "Medium"},
    {"name": "SNMP", "acronym": "SNMP", "port": "161-162", "description": "Manages devices", "osi_layer": 7, "difficulty": "Medium"},
    {"name": "RIP", "acronym": "RIP", "port": "520", "description": "Routing info exchange", "osi_layer": 3, "difficulty": "Hard"},
    {"name": "ICMP", "acronym": "ICMP", "port": "0-255", "description": "Troubleshoots network issues", "osi_layer": 3, "difficulty": "Hard"},
]

# ┌───────────────────────────────────────────────┐
# │ SECTION 2: Question Generator                 │
# └───────────────────────────────────────────────┘

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

# ┌───────────────────────────────────────────────┐
# │ SECTION 3: Welcome Screen and Quiz Setup      │
# └───────────────────────────────────────────────┘

if "questions" not in st.session_state or st.session_state.quiz_complete:
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

# ┌───────────────────────────────────────────────┐
# │ SECTION 4: Quiz Flow                          │
# └───────────────────────────────────────────────┘

if "questions" in st.session_state and not st.session_state.quiz_complete:
    q_index = st.session_state.current_question
    question = st.session_state.questions[q_index]
    st.markdown(f"### Question {q_index + 1} of {st.session_state.num_questions}")
    st.markdown(f"⏱️ Time elapsed: {round(time.time() - st.session_state.start_time, 2)} seconds")

    key = f"q_{q_index}"
    if question["type"] == "mc":
        answer = st.radio(question["question"], question["options"], key=key)
    elif question["type"] == "tf":
        answer = st.radio(question["question"], ["True", "False"], key=key)
    else:
        answer = st.text_input(question["question"], key=key)

    if st.button("Next"):
        st.session_state.answers[key] = answer
        st.session_state.current_question += 1
        if st.session_state.current_question >= st.session_state.num_questions:
            st.session_state.quiz_complete = True
        st.rerun()

# ┌───────────────────────────────────────────────┐
# │ SECTION 5: Review Screen                      │
# └───────────────────────────────────────────────┘

correct_count = 0

if "questions" in st.session_state and st.session_state.get("quiz_complete"):
    st.markdown("## 🔍 Quiz Review")

    layer_map = {
        1: "Physical", 2: "Data Link", 3: "Network",
        4: "Transport", 5: "Session", 6: "Presentation", 7: "Application"
    }

    for i, q in enumerate(st.session_state.questions):
        key = f"q_{i}"
        user_answer = st.session_state.answers.get(key, "No answer")
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

# ┌───────────────────────────────────────────────┐
# │ SECTION 6: Leaderboard Tracking               │
# └───────────────────────────────────────────────┘

if "leaderboard" not in st.session_state:
    st.session_state.leaderboard = []
if "attempt_count" not in st.session_state:
    st.session_state.attempt_count = 0

# Safely calculate elapsed time
start_time = st.session_state.get("start_time", time.time())
elapsed = round(time.time() - start_time, 2)

# Safely get difficulty and score
difficulty = st.session_state.get("difficulty", "Easy")
difficulty_weights = {"Easy": 1, "Medium": 2, "Hard": 3}
score = round((correct_count * difficulty_weights.get(difficulty, 1)) / max(elapsed, 1), 4)

# Save attempt
st.session_state.attempt_count += 1
attempt_name = f"Attempt {st.session_state.attempt_count}"
total_questions = len(st.session_state.questions) if "questions" in st.session_state else 0

st.session_state.leaderboard.append({
    "name": attempt_name,
    "difficulty": difficulty,
    "correct": correct_count,
    "total": total_questions,
    "time": elapsed,
    "score": score
})

# Keep only top 10 attempts
st.session_state.leaderboard = sorted(
    st.session_state.leaderboard,
    key=lambda x: x["score"],
    reverse=True
)[:10]

# Display leaderboard
st.markdown("## 🏆 Leaderboard (Top 10 Attempts)")
for entry in st.session_state.leaderboard:
    st.markdown(
        f"- **{entry['name']}** | Difficulty: {entry['difficulty']} | "
        f"Score: `{entry['score']}` | Correct: {entry['correct']}/{entry['total']} | "
        f"Time: {entry['time']}s"
    )

