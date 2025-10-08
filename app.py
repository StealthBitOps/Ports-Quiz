import streamlit as st
import pandas as pd
import random
import time
import os

# Load protocol data
protocols = [
    {
        "name": "FTP",
        "description": "Used for reliable file transfer",
        "port": 21,
        "layer": "Application",
        "reliable": True,
        "acronym": "File Transfer Protocol"
    },
    # Add more protocols here...
]

LEADERBOARD_FILE = "leaderboard.html"
MAX_LEADERBOARD_ENTRIES = 30

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            return pd.read_html(LEADERBOARD_FILE)[0]
        except Exception:
            return pd.DataFrame(columns=["Name", "Score", "Time"])
    return pd.DataFrame(columns=["Name", "Score", "Time"])

def save_leaderboard(df):
    df_sorted = df.sort_values(by=["Score", "Time"], ascending=[False, True]).head(MAX_LEADERBOARD_ENTRIES)
    df_sorted.to_html(LEADERBOARD_FILE, index=False)
    return df_sorted

def generate_questions(difficulty, num_questions):
    used = set()
    questions = []
    while len(questions) < num_questions:
        available = [i for i in range(len(protocols)) if i not in used]
        if not available:
            break
        idx = random.choice(available)
        proto = protocols[idx]
        used.add(idx)

        q_type = "mc" if difficulty == "Easy" else random.choice(["mc", "fill", "tf", "layer", "acronym"])

        if q_type == "mc":
            wrongs = random.sample([p for p in protocols if p["name"] != proto["name"]], 3)
            options = [proto] + wrongs
            random.shuffle(options)
            questions.append({
                "type": "mc",
                "question": f"Which protocol matches this description: '{proto['description']}'?",
                "options": [p["name"] for p in options],
                "answer": proto["name"],
                "explanation": {
                    "correct": f"{proto['name']} is correct because it {proto['description'].lower()}.",
                    "wrong": {
                        p["name"]: f"{p['name']} is incorrect because it {p['description'].lower()}."
                        for p in options if p["name"] != proto["name"]
                    }
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
        else:
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

st.title("🧠 TCP/UDP Protocol Quiz")

if "questions" not in st.session_state:
    st.markdown("### Setup your quiz")
    difficulty = st.select_slider("Select difficulty", options=["Easy", "Medium", "Hard"], value="Medium")
    num_questions = st.slider("Number of questions", min_value=3, max_value=len(protocols), value=5)

    if st.button("Start Quiz"):
        st.session_state.questions = generate_questions(difficulty, num_questions)
        st.session_state.answers = {}
        st.session_state.current_q = 0
        st.session_state.total_time = 0
        st.session_state.quiz_complete = False
        st.session_state.start_time = time.time()
        st.experimental_rerun()

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
            st_autorefresh(interval=1000, limit=10, key=f"refresh_{key}")

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
            st.experimental_rerun()

        if remaining == 0 and submit_key not in st.session_state:
            st.session_state.answers[key] = "No answer"
            st.session_state.total_time += 10
            if st.button("Next"):
                st.session_state[submit_key] = True
                st.session_state.current_q += 1
                st.experimental_rerun()

    else:
        st.session_state.quiz_complete = True
        st.experimental_rerun()

if "questions" in st.session_state and st.session_state.quiz_complete:
    st.markdown("## ✅ Quiz Complete!")
    st.markdown("Click below to review your answers.")
    if st.button("Review Answers"):
        st.session_state.review_ready = True
        st.experimental_rerun()

if "review_ready" in st.session_state and st.session_state.review_ready:
    st.markdown("## 🔍 Review Your Answers")

    correct_count = 0
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

        if is_correct:
            correct_count += 1

    st.session_state.final_score = correct_count
    st.markdown(f"### 🧮 Final Score: {correct_count} / {len(st.session_state.questions)}")

    name = st.text_input("Enter your name for the leaderboard (or leave blank for Anonymous):")
    if st.button("Submit Score"):
        if not name.strip():
            name = "Anonymous"
        leaderboard = load_leaderboard()
        new_entry = pd.DataFrame([{
            "Name": name,
            "Score": st.session_state.final_score,
            "Time": st.session_state.total_time
        }])
        updated = pd.concat([leaderboard, new_entry], ignore_index=True)
        top30 = save_leaderboard(updated)
        st.session_state.leaderboard = top30
        st.session_state.score_submitted = True
        st.experimental_rerun()

if "score_submitted" in st.session_state and st.session_state.score_submitted:
    st.markdown("## 🏆 Leaderboard (Top 30)")
    leaderboard = load_leaderboard()
    st.components.v1.html(leaderboard.to_html(index=False), height=600, scrolling=True)
