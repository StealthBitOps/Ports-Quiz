# ┌───────────────────────────────────────────────┐
# │ SECTION 1: Quiz Setup                         │
# └───────────────────────────────────────────────┘

difficulty = st.select_slider("Choose difficulty", options=["Easy", "Medium", "Hard"])
st.session_state["difficulty"] = difficulty

num_questions = st.slider("How many questions?", min_value=1, max_value=20, value=5)

# ┌───────────────────────────────────────────────┐
# │ SECTION 2: Protocol Dataset                   │
# └───────────────────────────────────────────────┘

protocols = [
    {"name": "SSH", "acronym": "SSH", "port": "22", "description": "Secure remote login service", "osi_layer": 7, "difficulty": "Easy"},
    {"name": "DNS", "acronym": "DNS", "port": "53", "description": "Resolves domain names to IP addresses", "osi_layer": 7, "difficulty": "Easy"},
    {"name": "FTP", "acronym": "FTP", "port": "20-21", "description": "Transfers files between systems", "osi_layer": 7, "difficulty": "Medium"},
    {"name": "SNMP", "acronym": "SNMP", "port": "161-162", "description": "Manages network devices remotely", "osi_layer": 7, "difficulty": "Medium"},
    {"name": "DHCP", "acronym": "DHCP", "port": "67, 68", "description": "Assigns IP addresses dynamically", "osi_layer": 7, "difficulty": "Medium"},
    {"name": "SMTP", "acronym": "SMTP", "port": "25", "description": "Transfers email", "osi_layer": 7, "difficulty": "Easy"},
    {"name": "HTTP", "acronym": "HTTP", "port": "80", "description": "Transfers webpages", "osi_layer": 7, "difficulty": "Easy"},
    {"name": "HTTPS", "acronym": "HTTPS", "port": "443", "description": "Transfers secure webpages", "osi_layer": 7, "difficulty": "Easy"},
    {"name": "RIP", "acronym": "RIP", "port": "520", "description": "Exchanges routing info between routers", "osi_layer": 3, "difficulty": "Hard"},
    {"name": "ICMP", "acronym": "ICMP", "port": "0-255", "description": "Troubleshoots network issues", "osi_layer": 3, "difficulty": "Hard"},
    # Add more entries as needed...
]

# ┌───────────────────────────────────────────────┐
# │ SECTION 3: Generate Questions                 │
# └───────────────────────────────────────────────┘

import random

def generate_questions(protocols, difficulty, count):
    pool = [p for p in protocols if p["difficulty"] == difficulty]
    selected = random.sample(pool, min(count, len(pool)))
    questions = []

    for p in selected:
        qtype = "mc" if difficulty == "Easy" else random.choice(["mc", "tf", "fill"])
        if qtype == "mc":
            distractors = random.sample([x["acronym"] for x in protocols if x["acronym"] != p["acronym"]], 3)
            questions.append({
                "question": f"Which protocol uses port {p['port']}?",
                "answer": p["acronym"],
                "type": "mc",
                "options": distractors + [p["acronym"]],
                "topic": "Protocol",
                "explanation": {
                    "correct": f"{p['acronym']} uses port {p['port']} — {p['description']}.",
                    "wrong": {d: f"{d} is not correct for port {p['port']}." for d in distractors}
                }
            })
        elif qtype == "tf":
            is_true = random.choice([True, False])
            answer = "True" if is_true else "False"
            fact = f"{p['acronym']} uses port {p['port']}" if is_true else f"{p['acronym']} uses port 9999"
            questions.append({
                "question": f"True or False: {fact}",
                "answer": answer,
                "type": "tf",
                "topic": "Protocol",
                "explanation": {
                    "correct": f"{'Correct' if is_true else 'Incorrect'} — {p['description']}."
                }
            })
        else:
            questions.append({
                "question": f"Fill in: Which protocol uses port {p['port']}?",
                "answer": p["acronym"],
                "type": "fill",
                "topic": "Protocol",
                "explanation": {
                    "correct": f"{p['acronym']} uses port {p['port']} — {p['description']}."
                }
            })

    return questions

# ┌───────────────────────────────────────────────┐
# │ SECTION 4: Review Logic                       │
# └───────────────────────────────────────────────┘

for i, q in enumerate(st.session_state.questions):
    key = f"q_{i}"
    user_answer = st.session_state.answers.get(key, "No answer")
    correct_answer = q["answer"]
    is_correct = user_answer.strip().lower() == correct_answer.strip().lower()

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
