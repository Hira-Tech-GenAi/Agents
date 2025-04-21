import streamlit as st  # type: ignore
from langchain_google_genai import GoogleGenerativeAI  # type: ignore
from langchain.agents import initialize_agent, AgentType, Tool  # type: ignore
from langchain.memory import ConversationBufferMemory  # type: ignore
from dotenv import load_dotenv  # type: ignore
import os
import re
import fitz  # type: ignore
from typing import Dict, Optional

# Load environment variables
load_dotenv()

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
images_dir = os.path.join(current_dir, "images")

def load_image(image_name: str, width: int = 250) -> None:
    try:
        image_path = os.path.join(images_dir, image_name)
        if os.path.exists(image_path):
            st.image(image_path, width=width)
        else:
            st.warning(f"Image not found: {image_name}")
    except Exception as e:
        st.warning(f"Error loading image {image_name}: {str(e)}")

# Initialize LLM
llm = GoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.environ["GEMINI_API_KEY"]
)

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

application_info: Dict[str, Optional[str]] = {
    "name": None,
    "email": None,
    "skills": None
}

def extract_application_info(text: str) -> str:
    name_match = re.search(r"(?:my name is|i am)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", text, re.IGNORECASE)
    email_match = re.search(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", text)
    skills_match = re.search(r"(?:skills are|i know|i can use)\s+(.+)", text, re.IGNORECASE)

    if name_match:
        application_info["name"] = name_match.group(1).title()
    if email_match:
        application_info["email"] = email_match.group(0)
    if skills_match:
        application_info["skills"] = skills_match.group(1).strip()

    return "Got it. Let me check what else I need."

def extract_text_from_pdf(uploaded_file) -> str:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def extract_info_from_cv(text: str) -> Dict[str, Optional[str]]:
    info: Dict[str, Optional[str]] = {
        "name": None,
        "email": None,
        "skills": None
    }

    name_match = re.search(r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", text)
    if name_match:
        info["name"] = name_match.group(1).title()

    email_match = re.search(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", text)
    if email_match:
        info["email"] = email_match.group(0)

    skills_section = re.search(r"(?:skills|technical skills|expertise)[:\n](.+?)(?=\n\n|\Z)", text, re.IGNORECASE | re.DOTALL)
    if skills_section:
        info["skills"] = skills_section.group(1).strip()

    return info

def check_application_goal(_: str) -> str:
    if all(application_info.values()):
        return (
            f"✅ You're ready! Name: {application_info['name']}, "
            f"Email: {application_info['email']}, Skills: {application_info['skills']}"
        )
    else:
        missing = [k for k, v in application_info.items() if not v]
        return f"⏳ Still need: {', '.join(missing)}"

tools = [
    Tool(name="extract_application_info", func=extract_application_info, description="Extract name, email, skills"),
    Tool(name="check_application_goal", func=check_application_goal, description="Check completion")
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    memory=memory,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=False
)

st.set_page_config(page_title="🎯 Job Application Assistant", layout="centered")
st.title("Intelligent Job Application Assistant")

load_image("bot-writing.jpg", width=250)

st.markdown("""
Welcome! 👋  
To get started, tell me your:

- **Name**  
- **Email**  
- **Skills**  

Or upload your **resume** and I'll try to extract them for you.
""")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "goal_complete" not in st.session_state:
    st.session_state.goal_complete = False
if "download_ready" not in st.session_state:
    st.session_state.download_ready = False
if "application_summary" not in st.session_state:
    st.session_state.application_summary = ""

st.sidebar.header("📤 Upload Resume (Optional)")
resume = st.sidebar.file_uploader("Upload your resume", type=["pdf", "txt"])

if resume:
    st.sidebar.success("Resume uploaded!")
    text = extract_text_from_pdf(resume)
    extracted = extract_info_from_cv(text)
    for key in application_info:
        if extracted[key]:
            application_info[key] = extracted[key]
    st.sidebar.info("🔍 Extracted info from resume:")
    for key, value in extracted.items():
        st.sidebar.markdown(f"**{key.capitalize()}:** {value}")

if st.sidebar.button("🔄 Reset Chat"):
    st.session_state.chat_history.clear()
    st.session_state.goal_complete = False
    st.session_state.download_ready = False
    st.session_state.application_summary = ""
    for key in application_info:
        application_info[key] = None
    st.rerun()

user_input = st.chat_input("Type here...")

if user_input:
    st.session_state.chat_history.append(("user", user_input))
    extract_application_info(user_input)
    response = agent.invoke({"input": user_input})
    bot_reply = response["output"]
    st.session_state.chat_history.append(("bot", bot_reply))
    goal_status = check_application_goal("check")
    st.session_state.chat_history.append(("status", goal_status))

    if "you're ready" in goal_status.lower():
        st.session_state.goal_complete = True
        summary = (
            f"✅ Name: {application_info['name']}\n"
            f"📧 Email: {application_info['email']}\n"
            f"🛠️ Skills: {application_info['skills']}\n"
        )
        st.session_state.application_summary = summary
        st.session_state.download_ready = True

for sender, message in st.session_state.chat_history:
    if sender == "user":
        with st.chat_message("🧑"):
            st.markdown(message)
    elif sender == "bot":
        with st.chat_message("🤖"):
            st.markdown(message)
    elif sender == "status":
        with st.chat_message("📊"):
            st.info(message)

if st.session_state.goal_complete:
    st.success("🎉 All information collected! You're ready to apply!")

if st.session_state.download_ready:
    st.download_button(
        label="📥 Download Application Summary (TXT)",
        data=st.session_state.application_summary,
        file_name="application_summary.txt",
        mime="text/plain"
    )
