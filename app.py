import streamlit as st
import pandas as pd
import random
from datetime import datetime
from fpdf import FPDF
import os

# Define protocol data
protocols = [
    ("SSH", "SSH", "22", "TCP", "Secure remote login service", "Remote Access"),
    ("Telnet", "Telnet", "23", "TCP", "Remote login service", "Remote Access"),
    ("REXEC", "REXEC", "512", "TCP", "Execute commands remotely", "Remote Access"),
    ("RLOGIN", "RLOGIN", "513", "TCP", "Interactive shell session", "Remote Access"),
    ("RDP", "RDP", "3389", "TCP", "Remote desktop access", "Remote Access"),
    ("X11", "X11", "6000", "TCP", "GUI for networked computers", "Remote Access"),
    ("FTP", "FTP", "20-21", "TCP", "Transfer files", "File Transfer"),
    ("SCP", "SCP", "22", "TCP", "Securely copy files", "File Transfer"),
    ("TFTP", "TFTP", "69", "UDP", "Transfer files between systems", "File Transfer"),
    ("SMB", "SMB", "445", "TCP", "Transfer files", "File Transfer"),
    ("NFS", "NFS", "2049", "TCP", "Mount remote systems", "File Transfer"),
    ("SMTP", "SMTP", "25", "TCP", "Email transfer", "Messaging"),
    ("POP3", "POP3", "110", "TCP", "Retrieve emails", "Messaging"),
    ("IMAP", "IMAP", "143", "TCP", "Access emails", "Messaging"),
    ("NNTP", "NNTP", "119", "TCP", "Access newsgroups", "Messaging"),
    ("IRC", "IRC", "194", "UDP", "Real-time chat", "Messaging"),
    ("Kerberos", "Kerberos", "88", "TCP", "Authentication and authorization", "Authentication"),
    ("LDAP", "LDAP", "389", "TCP", "Directory services", "Authentication"),
    ("RADIUS", "RADIUS", "1812", "TCP", "Authentication and authorization", "Authentication"),
    ("KINK", "KINK", "892", "TCP", "Authentication and authorization", "Authentication"),
]

# Convert to DataFrame
df = pd.DataFrame(protocols, columns=["Protocol", "Acronym", "Port(s)", "Transport Layer", "Description", "Functionality Group"])

# Streamlit app
st.set_page_config(page_title="TCP/UDP Protocol Quiz", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-family: 'Calibri', sans-serif;
        font-size: 11pt;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 TCP/UDP Protocol Quiz")

# Difficulty slider
difficulty = st.slider("Select difficulty level", 1, 3, 2, format="Level %d")
difficulty_map = {1: 0.25, 2: 0.5, 3: 1.0}
subset_size = int(len(df) * difficulty_map[difficulty])
subset_df = df.sample(n=subset_size, random_state=42).reset_index(drop=True)

# Number of questions slider
max_questions = len(subset_df)
num_questions = st.slider("Number of questions", 1, max_questions, min(10, max_questions))
quiz_df = subset_df.sample(n=num_questions, random_state=1).reset_index(drop=True)

st.subheader("Answer the following questions:")

user_answers = []
questions = []

for i, row in quiz_df.iterrows():
    qtype = random.choice(["mc", "tf", "fill"])
    question_text = ""
    correct_answer = ""
    explanation = ""
    options = []

    if qtype == "mc":
        question_text = f"What is the port number for {row['Protocol']}?"
        correct_answer = row['Port(s)']
        options = [row['Port(s)']]
        while len(options) < 4:
            opt = random.choice(df['Port(s)'].tolist())
            if opt not in options:
                options.append(opt)
        random.shuffle(options)
        user_choice = st.radio(f"Q{i+1}: {question_text}", options, key=f"q{i}")
        user_answers.append(user_choice)
        explanation = f"{row['Protocol']} uses port {row['Port(s)']} for {row['Description']}."

    elif qtype == "tf":
        question_text = f"True or False: {row['Protocol']} uses UDP."
        correct_answer = "True" if row['Transport Layer'] == "UDP" else "False"
        user_choice = st.radio(f"Q{i+1}: {question_text}", ["True", "False"], key=f"q{i}")
        user_answers.append(user_choice)
        explanation = f"{row['Protocol']} uses {row['Transport Layer']}."

    elif qtype == "fill":
        question_text = f"Fill in the acronym for this protocol: {row['Description']}"
        correct_answer = row['Acronym']
        user_choice = st.text_input(f"Q{i+1}: {question_text}", key=f"q{i}")
        user_answers.append(user_choice)
        explanation = f"The correct acronym is {row['Acronym']} for {row['Protocol']}."

    questions.append({
        "question": question_text,
        "correct": correct_answer,
        "user": user_choice,
        "explanation": explanation
    })

# Submit button
if st.button("Submit Quiz"):
    st.subheader("📊 Quiz Results")
    score = 0
    for i, q in enumerate(questions):
        st.markdown(f"**Q{i+1}:** {q['question']}")
        st.markdown(f"- Your answer: `{q['user']}`")
        st.markdown(f"- Correct answer: `{q['correct']}`")
        st.markdown(f"- Explanation: {q['explanation']}")
        if str(q['user']).strip().lower() == str(q['correct']).strip().lower():
            score += 1
        st.markdown("---")

    st.markdown(f"### ✅ Score: {score} / {num_questions}")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"**Completed on:** {timestamp}")
    st.markdown(f"**Difficulty Level:** Level {difficulty}")

    # Generate PDF
    pdf = FPDF()
    pdf.add_font('Calibri', '', '/usr/share/fonts/truetype/msttcorefonts/Calibri.ttf', uni=True)
    pdf.set_font("Calibri", size=11)
    pdf.add_page()
    pdf.cell(200, 10, txt="TCP/UDP Protocol Quiz Results", ln=True, align='C')
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Completed on: {timestamp}", ln=True)
    pdf.cell(200, 10, txt=f"Difficulty Level: Level {difficulty}", ln=True)
    pdf.cell(200, 10, txt=f"Score: {score} / {num_questions}", ln=True)
    pdf.ln(5)

    for i, q in enumerate(questions):
        pdf.multi_cell(0, 10, txt=f"Q{i+1}: {q['question']}\nYour answer: {q['user']}\nCorrect answer: {q['correct']}\nExplanation: {q['explanation']}\n---")

    if not os.path.exists("/mnt/data"):
        os.makedirs("/mnt/data")
    pdf_path = "/mnt/data/quiz_results.pdf"
    pdf.output(pdf_path)
    st.success("✅ PDF generated successfully!")
    st.markdown(f"[📥 Download Results PDF](quiz_results.pdf)")
