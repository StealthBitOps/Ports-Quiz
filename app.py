import streamlit as st
import time
import random

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
        qtype = "mc"
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
            "osi_layer": p["osi_layer"]
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

    # Timer logic
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
# │ SECTION 5: Review Screen                                   │
# └────────────────────────────────────────────────────────────┘

if st.session_state.get("quiz_complete"):
    st.title("🔍 Quiz Review")
    correct = 0
    for i, q in enumerate(st.session_state.questions):
        user_answer = st.session_state.answers.get(i, "")
        is_correct = user_answer == q["answer"]
        if is_correct:
            correct += 1
        st.markdown(f"**Q{i+1}: {q['question']}**")
        st.markdown(f"- Your answer: `{user_answer}`")
        st.markdown(f"- Correct answer: `{q['answer']}`")
        st.markdown(f"- Result: {'✅ Correct' if is_correct else '❌ Incorrect'}")
        st.markdown("---")

    st.success(f"Final Score: {correct} / {len(st.session_state.questions)}")

    if st.button("🔁 Restart Quiz"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

