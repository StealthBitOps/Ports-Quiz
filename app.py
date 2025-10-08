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
st.markdown("Welcome! Test your knowledge of network protocols. Select your difficulty and number of questions to begin.")

difficulty = st.select_slider("Select difficulty", options=["Easy", "Medium", "Hard"], value="Medium")
num_questions = st.slider("Number of questions", min_value=3, max_value=len(protocols), value=5)

if st.button("Generate Quiz"):
    # ✅ Clear old session keys to avoid leftover data
    for key in list(st.session_state.keys()):
        if key.startswith("q_") or key.startswith("user_input_") or key.endswith("_start_time") or key == "trigger_rerun":
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
                correct = "True" if proto["reliable"] else "False"
                explanation = f"{proto['name']} is {'reliable' if proto['reliable'] else 'not reliable'} because it {'ensures' if proto['reliable'] else 'does not guarantee'} delivery."
                questions.append({
                    "type": "tf",
                    "question": f"True or False: {proto['name']} is {'reliable' if proto['reliable'] else 'unreliable'}.",
                    "answer": correct,
                    "explanation": explanation
                })

        return questions

    # ✅ Initialize new quiz
    st.session_state.questions = generate_questions(difficulty, num_questions)
    st.session_state.answers = {}
    st.session_state.submitted = False
    st.session_state.current_q = 0
    st.session_state.start_time = time.time()

# ============================================================
# ⏱️ SECTION 3: Quiz Flow with Timer and Answer Input
# ============================================================

if st.session_state.get("trigger_rerun"):
    st.session_state.trigger_rerun = False
    st.stop()

if "questions" in st.session_state and not st.session_state.submitted:
    q_index = st.session_state.current_q
    if q_index < len(st.session_state.questions):
        q = st.session_state.questions[q_index]
        st.markdown(f"**Question {q_index + 1} of {len(st.session_state.questions)}**")
        st.markdown(f"**{q['question']}**")

        key = f"q_{q_index}"
        start_time_key = f"{key}_start_time"

        # ✅ Safe timer initialization
        if start_time_key not in st.session_state:
            st.session_state[start_time_key] = time.time()

        elapsed = time.time() - st.session_state[start_time_key]
        remaining = max(0, 10 - int(elapsed))
        st.markdown(f"⏳ Time left: {remaining} seconds")

        # 🔁 Auto-refresh every second
        st_autorefresh(interval=1000, limit=10, key=f"refresh_{key}")

        submitted = False
        answer = None

        # ✅ Multiple Choice and True/False using radio buttons
        if q["type"] in ["mc", "tf"]:
            options = q["options"] if q["type"] == "mc" else ["True", "False"]
            radio_key = f"radio_{q_index}"
            clear_key = f"clear_{q_index}"

            # Initialize selection
            if radio_key not in st.session_state:
                st.session_state[radio_key] = None

            # Show radio buttons
            selected = st.radio("Choose one:", options, key=radio_key)

            # Clear selection button
            if st.button("Clear selection", key=clear_key):
                st.session_state[radio_key] = None
                st.experimental_rerun()

            # Enable submit only if selected
            if st.session_state[radio_key] is not None:
                answer = st.session_state[radio_key]
                if st.button("Submit"):
                    submitted = True
            else:
                st.button("Submit", disabled=True)

        # ✅ Fill-in-the-blank with Enter key and Submit button
        elif q["type"] == "fill":
            input_key = f"user_input_{q_index}"
            if input_key not in st.session_state:
                st.session_state[input_key] = ""

            with st.form(key=f"form_{q_index}"):
                st.session_state[input_key] = st.text_input("Your answer:", value=st.session_state[input_key])
                submitted = st.form_submit_button("Submit")

            answer = st.session_state[input_key]
            if not submitted and answer.strip():
                if st.button("Submit"):
                    submitted = True
            elif not answer.strip():
                st.button("Submit", disabled=True)

        # ✅ Handle submission
        if submitted and f"{key}_submitted" not in st.session_state:
            st.session_state.answers[key] = answer if answer else "No answer"
            st.session_state[f"{key}_submitted"] = True
            st.session_state.current_q += 1
            st.session_state[start_time_key] = None
            st.session_state.trigger_rerun = True

        # ✅ Show Next button only after timeout
        if remaining == 0 and f"{key}_submitted" not in st.session_state:
            st.markdown("⏱ Time's up! You can still submit your answer.")
            if st.button("Next"):
                st.session_state.answers[key] = answer if answer else "No answer"
                st.session_state[f"{key}_submitted"] = True
                st.session_state.current_q += 1
                st.session_state[start_time_key] = None
                st.session_state.trigger_rerun = True

# ============================================================
# ✅ SECTION 4: Submission, Feedback, Leaderboard, PDF Export
# ============================================================

if "questions" in st.session_state and not st.session_state.submitted and st.session_state.current_q >= len(st.session_state.questions):
    score = 0
    results = []
    end_time = time.time()
    total_time = end_time - st.session_state.get("start_time", end_time)

    # Evaluate answers
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
    st.success(f"✅ You scored {score} out of {len(st.session_state.questions)} in {round(total_time, 2)} seconds")

    # Show detailed feedback
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

    # Leaderboard entry
    name = st.text_input("🏅 Enter your name for the leaderboard (or leave blank for anonymous):")
    if st.button("Submit to Leaderboard"):
        display_name = name.strip() if name.strip() else "Anonymous"
        leaderboard = update_leaderboard(display_name, score, total_time)
        st.success("Your score has been submitted!")

        st.subheader("📊 Leaderboard")
        for i, entry in enumerate(leaderboard[:10], start=1):
            st.markdown(f"{i}. **{entry['name']}** — {entry['score']} pts in {entry['time']}s")

    # PDF export
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

    generate_pdf(results, score, len(st.session_state.questions), difficulty, name or "Anonymous")
    with open("quiz_results.pdf", "rb") as f:
        st.download_button("📄 Download PDF Results", f, file_name="quiz_results.pdf")

# 🔄 Restart button
if "questions" in st.session_state:
    if st.button("🔄 Start Over"):
        st.session_state.clear()
        st.experimental_rerun()








