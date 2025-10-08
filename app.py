# ┌───────────────────────────────────────────────┐
# │ SECTION 1: Imports, Constants, and Dataset    │
# └───────────────────────────────────────────────┘

# 📦 Imports
import streamlit as st
import pandas as pd
import random
import time
import os
from streamlit_autorefresh import st_autorefresh

# ⚙️ Constants
LEADERBOARD_FILE = "leaderboard.html"
MAX_LEADERBOARD_ENTRIES = 30
MAX_QUESTIONS = 20  # One question per protocol

# 📚 Protocol Dataset (20 entries)
protocols = [
    {"name": "FTP", "description": "Used for reliable file transfer", "port": 21, "layer": "Application", "reliable": True, "acronym": "File Transfer Protocol"},
    {"name": "HTTP", "description": "Used for web page delivery", "port": 80, "layer": "Application", "reliable": True, "acronym": "HyperText Transfer Protocol"},
    {"name": "HTTPS", "description": "Secure version of HTTP", "port": 443, "layer": "Application", "reliable": True, "acronym": "HyperText Transfer Protocol Secure"},
    {"name": "SMTP", "description": "Used for sending emails", "port": 25, "layer": "Application", "reliable": True, "acronym": "Simple Mail Transfer Protocol"},
    {"name": "POP3", "description": "Used for retrieving emails", "port": 110, "layer": "Application", "reliable": True, "acronym": "Post Office Protocol v3"},
    {"name": "IMAP", "description": "Used for managing emails on server", "port": 143, "layer": "Application", "reliable": True, "acronym": "Internet Message Access Protocol"},
    {"name": "DNS", "description": "Resolves domain names to IP addresses", "port": 53, "layer": "Application", "reliable": False, "acronym": "Domain Name System"},
    {"name": "DHCP", "description": "Assigns IP addresses to devices", "port": 67, "layer": "Application", "reliable": False, "acronym": "Dynamic Host Configuration Protocol"},
    {"name": "SNMP", "description": "Used for network monitoring", "port": 161, "layer": "Application", "reliable": False, "acronym": "Simple Network Management Protocol"},
    {"name": "Telnet", "description": "Remote login without encryption", "port": 23, "layer": "Application", "reliable": True, "acronym": "Telecommunication Network"},
    {"name": "SSH", "description": "Secure remote login", "port": 22, "layer": "Application", "reliable": True, "acronym": "Secure Shell"},
    {"name": "TCP", "description": "Reliable transport protocol", "port": None, "layer": "Transport", "reliable": True, "acronym": "Transmission Control Protocol"},
    {"name": "UDP", "description": "Unreliable transport protocol", "port": None, "layer": "Transport", "reliable": False, "acronym": "User Datagram Protocol"},
    {"name": "IP", "description": "Routes packets across networks", "port": None, "layer": "Network", "reliable": False, "acronym": "Internet Protocol"},
    {"name": "ICMP", "description": "Used for error reporting and diagnostics", "port": None, "layer": "Network", "reliable": False, "acronym": "Internet Control Message Protocol"},
    {"name": "ARP", "description": "Resolves IP to MAC addresses", "port": None, "layer": "Network", "reliable": False, "acronym": "Address Resolution Protocol"},
    {"name": "RDP", "description": "Remote desktop access", "port": 3389, "layer": "Application", "reliable": True, "acronym": "Remote Desktop Protocol"},
    {"name": "NTP", "description": "Synchronizes clocks over network", "port": 123, "layer": "Application", "reliable": False, "acronym": "Network Time Protocol"},
    {"name": "LDAP", "description": "Directory access protocol", "port": 389, "layer": "Application", "reliable": True, "acronym": "Lightweight Directory Access Protocol"},
    {"name": "TFTP", "description": "Simple file transfer without authentication", "port": 69, "layer": "Application", "reliable": False, "acronym": "Trivial File Transfer Protocol"}
]

# ┌───────────────────────────────────────────────┐
# │ SECTION 2: Leaderboard Utilities              │
# └───────────────────────────────────────────────┘

import datetime

def record_attempt(name, score, time_taken, difficulty):
    attempt = {
        "Name": name,
        "Score": score,
        "Time": time_taken,
        "Difficulty": difficulty,
        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if "session_leaderboard" not in st.session_state:
        st.session_state.session_leaderboard = []
    st.session_state.session_leaderboard.append(attempt)

def get_top_attempts(n=5):
    if "session_leaderboard" not in st.session_state:
        return pd.DataFrame(columns=["Name", "Score", "Time", "Difficulty", "Timestamp"])
    df = pd.DataFrame(st.session_state.session_leaderboard)
    return df.sort_values(by=["Score", "Time"], ascending=[False, True]).head(n)

# ┌───────────────────────────────────────────────┐
# │ SECTION 3: Question Generator                 │
# └───────────────────────────────────────────────┘

def generate_questions(difficulty, num_questions):
    used_indices = set()
    questions = []

    while len(questions) < num_questions:
        available_indices = [i for i in range(len(protocols)) if i not in used_indices]
        if not available_indices:
            break

        idx = random.choice(available_indices)
        proto = protocols[idx]
        used_indices.add(idx)

        q_type = "mc" if difficulty == "Easy" else random.choice(["mc", "fill", "tf", "layer", "acronym"])

        if q_type == "mc":
            wrongs_pool = [p for p in protocols if p["name"] != proto["name"]]
            wrongs = random.sample(wrongs_pool, min(3, len(wrongs_pool)))
            options = [proto] + wrongs
            random.shuffle(options)
            questions.append({
                "type": "mc",
                "question": f"Which protocol matches this description: '{proto['description']}'?",
                "options": [p["name"] for p in options],
                "answer": proto["name"],
                "explanation": {
                    "correct": f"{proto['name']} is correct because it {proto['description'].lower()}.",
                    "wrong": {p["name"]: f"{p['name']} is incorrect because it {p['description'].lower()}." for p in options if p["name"] != proto["name"]}
                }
            })

        elif q_type == "fill":
            questions.append({
                "type": "fill",
                "question": f"Which protocol uses port {proto['port']}?",
                "answer": proto["name"],
                "explanation": {
                    "correct": f"{proto['name']} uses port {proto['port']} for {proto['description'].lower()}."
                }
            })

        elif q_type == "layer":
            questions.append({
                "type": "fill",
                "question": f"Which layer does {proto['name']} operate on?",
                "answer": proto["layer"],
                "explanation": {
                    "correct": f"{proto['name']} operates on the {proto['layer']} layer."
                }
            })

        elif q_type == "acronym":
            questions.append({
                "type": "fill",
                "question": f"What does the acronym {proto['name']} stand for?",
                "answer": proto["acronym"],
                "explanation": {
                    "correct": f"{proto['name']} stands for {proto['acronym']}."
                }
            })

        elif q_type == "tf":
            correct = "True" if proto["reliable"] else "False"
            questions.append({
                "type": "tf",
                "question": f"True or False: {proto['name']} is {'reliable' if proto['reliable'] else 'unreliable'}.",
                "options": ["True", "False"],
                "answer": correct,
                "explanation": {
                    "correct": f"{proto['name']} is {'reliable' if proto['reliable'] else 'unreliable'} because it {'uses' if proto['reliable'] else 'does not use'} connection-oriented delivery."
                }
            })

    return questions

# ┌───────────────────────────────────────────────┐
# │ SECTION 4: Quiz Initialization and State      │
# └───────────────────────────────────────────────┘

st.title("🧠 TCP/UDP Protocol Quiz")

if "questions" not in st.session_state:
    st.markdown("### Setup your quiz")
    difficulty = st.select_slider("Select difficulty", options=["Easy", "Medium", "Hard"], value="Medium")
    num_questions = st.slider("Number of questions", min_value=3, max_value=MAX_QUESTIONS, value=5)

    if st.button("Start Quiz"):
        st.session_state.questions = generate_questions(difficulty, num_questions)
        st.session_state.answers = {}
        st.session_state.current_q = 0
        st.session_state.total_time = 0
        st.session_state.quiz_complete = False
        st.session_state.start_time = time.time()
        st.rerun()

# ┌───────────────────────────────────────────────┐
# │ SECTION 5: Quiz Flow and Timer Logic          │
# └───────────────────────────────────────────────┘

if "questions" in st.session_state and not st.session_state.quiz_complete:
    q_index = st.session_state.current_q
    questions = st.session_state.questions

    if q_index < len(questions):
        q = questions[q_index]
        key = f"q_{q_index}"
        start_key = f"{key}_start"
        submit_key = f"{key}_submitted"

        if start_key not in st.session_state:
            st.session_state[start_key] = time.time()

        elapsed = time.time() - st.session_state[start_key]
        remaining = max(0, 10 - int(elapsed))

        if submit_key not in st.session_state and remaining > 0:
            st.markdown(f"⏳ Time remaining: {remaining} seconds")
            st_autorefresh(interval=1000, limit=11, key=f"refresh_{key}")

        with st.container():
            st.markdown(f"### Question {q_index + 1} of {len(questions)}")
            st.markdown(f"**{q['question']}**")

            answer = None
            submitted = False

            if q["type"] in ["mc", "tf"]:
                options = q["options"]
                selected = st.radio("Choose one:", options, key=f"radio_{q_index}")
                answer = selected
                if remaining > 0 and st.button("Submit"):
                    submitted = True

            elif q["type"] == "fill":
                user_input = st.text_input("Your answer:", key=f"input_{q_index}")
                answer = user_input
                if remaining > 0 and st.button("Submit"):
                    submitted = True

            if submitted and submit_key not in st.session_state:
                st.session_state.answers[key] = answer if answer else "No answer"
                st.session_state.total_time += int(elapsed)
                st.session_state[submit_key] = True
                st.session_state.current_q += 1
                st.rerun()

            if remaining == 0 and submit_key not in st.session_state:
                st.session_state.answers[key] = "No answer"
                st.session_state.total_time += 10
                if st.button("Next"):
                    st.session_state[submit_key] = True
                    st.session_state.current_q += 1
                    st.rerun()

    else:
        st.session_state.quiz_complete = True
        st.rerun()

# ┌───────────────────────────────────────────────┐
# │ SECTION 6: Completion, Review, Restart, Leader│
# └───────────────────────────────────────────────┘

if "questions" in st.session_state and st.session_state.quiz_complete:
    st.markdown("## ✅ Quiz Complete!")

    if "review_ready" not in st.session_state:
        if st.button("Review Answers"):
            st.session_state.review_ready = True
            st.rerun()

if "review_ready" in st.session_state and st.session_state.review_ready:
    st.markdown("## 🔍 Review Your Answers")

    correct_count = 0
    for i, q in enumerate(st.session_state.questions):
        key = f"q_{i}"
        user_answer = st.session_state.answers.get(key, "No answer")
        correct_answer = q["answer"]
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()

        with st.container():
            st.markdown(f"### Q{i+1}: {q['question']}")
            st.markdown(f"- Your answer: `{user_answer}`")
            st.markdown(f"- Correct answer: `{correct_answer}`")
            st.markdown(f"- {'✅ Correct!' if is_correct else '❌ Incorrect.'}")
            st.markdown(f"- Explanation: {q['explanation']['correct']}")

            if q["type"] == "mc":
                for opt in q["options"]:
                    if opt != correct_answer:
                        wrong_expl = q["explanation"]["wrong"].get(opt)
                        if wrong_expl:
                            st.markdown(f"  - ❌ `{opt}`: {wrong_expl}")
            st.markdown("---")

        if is_correct:
            correct_count += 1

    st.session_state.final_score = correct_count
    st.markdown(f"### 🧮 Final Score: {correct_count} / {len(st.session_state.questions)}")

    # 🔁 Restart Quiz Option
    if st.button("🔄 Restart Quiz"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # 📝 Leaderboard Submission (Session-Based)
    if "score_submitted" not in st.session_state:
        with st.form("submit_score_form"):
            name = st.text_input("Enter your name for the leaderboard (or leave blank for Anonymous):")
            submitted = st.form_submit_button("Submit Score")
            if submitted:
                if not name.strip():
                    name = "Anonymous"
                difficulty = st.session_state.difficulty if "difficulty" in st.session_state else "Unknown"
                record_attempt(name, st.session_state.final_score, st.session_state.total_time, difficulty)
                st.session_state.score_submitted = True
                st.rerun()

    # 🏆 Leaderboard Preview (Top 5 from session)
    st.markdown("## 🏆 Leaderboard Preview")
    top5 = get_top_attempts()
    if top5.empty:
        st.info("Leaderboard is currently empty. Be the first to submit your score!")
    else:
        st.dataframe(top5, use_container_width=True)
