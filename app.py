# ============================================================
# 📦 SECTION 1: Imports, Protocol Table, and Leaderboard Setup
# ============================================================

import streamlit as st
import random
import time
import json
import os
from datetime import datetime
from fpdf import FPDF
from streamlit_autorefresh import st_autorefresh  # ✅ Required for countdown

# -----------------------------
# 📊 Protocol Table (20 Rows)
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
    {"name": "SNMP", "acronym": "Simple Network Management Protocol", "port": "161", "layer": "Application", "reliable": False, "description": "Monitors and manages network devices."},
    {"name": "HTTPS", "acronym": "HyperText Transfer Protocol Secure", "port": "443", "layer": "Application", "reliable": True, "description": "Secure version of HTTP using encryption."},
    {"name": "Telnet", "acronym": "Telecommunication Network", "port": "23", "layer": "Application", "reliable": False, "description": "Used for remote login over networks."},
    {"name": "SFTP", "acronym": "Secure File Transfer Protocol", "port": "22", "layer": "Application", "reliable": True, "description": "Secure file transfer over SSH."},
    {"name": "NTP", "acronym": "Network Time Protocol", "port": "123", "layer": "Application", "reliable": False, "description": "Synchronizes clocks over networks."},
    {"name": "LDAP", "acronym": "Lightweight Directory Access Protocol", "port": "389", "layer": "Application", "reliable": True, "description": "Accesses and maintains distributed directory information."},
    {"name": "RDP", "acronym": "Remote Desktop Protocol", "port": "3389", "layer": "Application", "reliable": True, "description": "Provides remote access to desktops."},
    {"name": "ICMP", "acronym": "Internet Control Message Protocol", "port": "N/A", "layer": "Network", "reliable": False, "description": "Used for error messages and diagnostics."},
    {"name": "SSH", "acronym": "Secure Shell", "port": "22", "layer": "Application", "reliable": True, "description": "Secure remote login and command execution."},
    {"name": "TFTP", "acronym": "Trivial File Transfer Protocol", "port": "69", "layer": "Application", "reliable": False, "description": "Simple file transfer protocol with minimal features."},
    {"name": "BGP", "acronym": "Border Gateway Protocol", "port": "179", "layer": "Network", "reliable": True, "description": "Manages routing between autonomous systems."}
]

# -----------------------------
# 🏆 Leaderboard Functions
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

# ============================================================
# 🧠 SECTION 2: Welcome Screen and Quiz Setup
# ============================================================

st.title("🧠 TCP/UDP Protocol Quiz")
st.markdown("Welcome! Select difficulty and number of questions to begin.")

difficulty = st.select_slider("Select difficulty", options=["Easy", "Medium", "Hard"], value="Medium")
num_questions = st.slider("Number of questions", min_value=3, max_value=len(protocols), value=5)

if st.button("Generate Quiz"):
    # Clear previous state
    for key in list(st.session_state.keys()):
        if key.startswith("q_") or key.startswith("user_input_") or key.endswith("_start_time") or key.startswith("radio_") or key.endswith("_submitted"):
            del st.session_state[key]

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
                questions.append({
                    "type": "mc",
                    "question": f"Which protocol matches this description: '{proto['description']}'?",
                    "options": options,
                    "answer": proto["name"]
                })
            elif q_type == "fill":
                questions.append({
                    "type": "fill",
                    "question": f"Which protocol uses port {proto['port']}?",
                    "answer": proto["name"]
                })
            elif q_type == "layer":
                questions.append({
                    "type": "fill",
                    "question": f"Which layer does {proto['name']} operate on?",
                    "answer": proto["layer"]
                })
            elif q_type == "acronym":
                questions.append({
                    "type": "fill",
                    "question": f"What does the acronym {proto['name']} stand for?",
                    "answer": proto["acronym"]
                })
            else:
                correct = "True" if proto["reliable"] else "False"
                questions.append({
                    "type": "tf",
                    "question": f"True or False: {proto['name']} is {'reliable' if proto['reliable'] else 'unreliable'}.",
                    "options": ["True", "False"],
                    "answer": correct
                })

        return questions

    st.session_state.questions = generate_questions(difficulty, num_questions)
    st.session_state.answers = {}
    st.session_state.submitted = False
    st.session_state.current_q = 0

# ============================================================
# ⏱️ SECTION 3: Quiz Flow with Timer and Answer Input
# ============================================================

if "questions" in st.session_state and not st.session_state.submitted:
    q_index = st.session_state.current_q
    questions = st.session_state.questions

    if q_index < len(questions):
        q = questions[q_index]
        key = f"q_{q_index}"
        start_time_key = f"{key}_start_time"
        submitted_key = f"{key}_submitted"

        # Timer setup
        if start_time_key not in st.session_state:
            st.session_state[start_time_key] = time.time()

        elapsed = time.time() - st.session_state[start_time_key]
        remaining = max(0, 10 - int(elapsed))
        st.markdown(f"**Question {q_index + 1} of {len(questions)}**")
        st.markdown(f"**{q['question']}**")
        st.markdown(f"⏳ Time left: {remaining} seconds")

        # Refresh only if timer is active and not submitted
        if remaining > 0 and submitted_key not in st.session_state:
            st_autorefresh(interval=1000, limit=10, key=f"refresh_{key}")

        answer = None
        submitted = False

        # Multiple Choice and True/False
        if q["type"] in ["mc", "tf"]:
            options = q["options"]
            radio_key = f"radio_{q_index}"
            selected = st.radio("Choose one:", options, key=radio_key)
            answer = selected

            if remaining > 0:
                if selected:
                    if st.button("Submit"):
                        submitted = True
                else:
                    st.button("Submit", disabled=True)

        # Fill-in-the-blank
        elif q["type"] == "fill":
            input_key = f"user_input_{q_index}"
            if input_key not in st.session_state:
                st.session_state[input_key] = ""

            with st.form(key=f"form_{q_index}"):
                st.session_state[input_key] = st.text_input("Your answer:", value=st.session_state[input_key])
                submitted = st.form_submit_button("Submit")

            answer = st.session_state[input_key]

        # Handle submission
        if submitted and submitted_key not in st.session_state:
            st.session_state.answers[key] = answer if answer else "No answer"
            st.session_state[submitted_key] = True
            st.session_state.current_q += 1
            st.session_state[start_time_key] = None
            if st.session_state.current_q < len(st.session_state.questions):
                st.experimental_rerun()

        # Timer expired — show Next button
        if remaining == 0 and submitted_key not in st.session_state:
            st.session_state.answers[key] = answer if answer else "No answer"
            st.markdown("⏱ Time's up! You can still review your answer.")
            st.button("Submit", disabled=True)
            if st.button("Next"):
                st.session_state[submitted_key] = True
                st.session_state.current_q += 1
                st.session_state[start_time_key] = None
                if st.session_state.current_q < len(st.session_state.questions):
                    st.experimental_rerun()

# ============================================================
# 🏁 SECTION 4: Quiz Completion
# ============================================================

if "questions" in st.session_state and not st.session_state.submitted:
    if st.session_state.current_q >= len(st.session_state.questions):
        st.session_state.submitted = True
        st.markdown("🎉 Quiz complete! Here are your answers:")

        for i, q in enumerate(st.session_state.questions):
            key = f"q_{i}"
            user_answer = st.session_state.answers.get(key, "No answer")
            correct_answer = q["answer"]
            st.markdown(f"**Q{i+1}: {q['question']}**")
            st.markdown(f"- Your answer: `{user_answer}`")
            st.markdown(f"- Correct answer: `{correct_answer}`")
            st.markdown("---")
