import streamlit as st
import time
import random

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 1: Setup and Sample Questions                      │
# └────────────────────────────────────────────────────────────┘

questions = [
    {"question": "Which protocol uses port 22?", "options": ["FTP", "SSH", "DNS", "HTTP"], "answer": "SSH"},
    {"question": "Which protocol resolves domain names?", "options": ["SNMP", "FTP", "DNS", "ICMP"], "answer": "DNS"},
    {"question": "Which protocol transfers files?", "options": ["FTP", "RIP", "SSH", "SNMP"], "answer": "FTP"},
]

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 2: Initialize State                                │
# └────────────────────────────────────────────────────────────┘

if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.index = 0
    st.session_state.answers = {}
    st.session_state.timer_start = None

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 3: Start Quiz                                      │
# └────────────────────────────────────────────────────────────┘

if not st.session_state.started:
    st.title("🧠 Simple Protocol Quiz")
    st.markdown("Click below to begin.")
    if st.button("Start Quiz"):
        st.session_state.started = True
        st.session_state.timer_start = time.time()
        st.rerun()

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 4: Quiz Flow                                       │
# └────────────────────────────────────────────────────────────┘

if st.session_state.started and st.session_state.index < len(questions):
    q = questions[st.session_state.index]
    st.subheader(f"Question {st.session_state.index + 1}")
    st.markdown(q["question"])
    selected = st.radio("Choose one:", q["options"], key=f"q_{st.session_state.index}")

    # Timer
    elapsed = int(time.time() - st.session_state.timer_start)
    remaining = max(0, 15 - elapsed)
    st.markdown(f"⏳ Time left: `{remaining}` seconds")

    if remaining == 0:
        st.session_state.answers[st.session_state.index] = selected
        st.session_state.index += 1
        st.session_state.timer_start = time.time()
        st.rerun()

    if st.button("Submit", disabled=selected == ""):
        st.session_state.answers[st.session_state.index] = selected
        st.session_state.index += 1
        st.session_state.timer_start = time.time()
        st.rerun()

# ┌────────────────────────────────────────────────────────────┐
# │ SECTION 5: Review                                          │
# └────────────────────────────────────────────────────────────┘

if st.session_state.started and st.session_state.index >= len(questions):
    st.title("✅ Quiz Complete")
    score = 0
    for i, q in enumerate(questions):
        user = st.session_state.answers.get(i, "")
        correct = q["answer"]
        st.markdown(f"**Q{i+1}: {q['question']}**")
        st.markdown(f"- Your answer: `{user}`")
        st.markdown(f"- Correct answer: `{correct}`")
        if user == correct:
            score += 1
    st.success(f"Final Score: {score} / {len(questions)}")

    if st.button("Restart Quiz"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
