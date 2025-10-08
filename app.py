# ┌───────────────────────────────────────────────┐
# │ SECTION 2: Leaderboard Utilities              │
# └───────────────────────────────────────────────┘

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
        st.experimental_rerun()

# ┌───────────────────────────────────────────────┐
# │ SECTION 6: Completion and Review              │
# └───────────────────────────────────────────────┘

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
