import streamlit as st
from langchain_google_genai import GoogleGenerativeAI
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import os
import re
import fitz  # PyMuPDF

#? 🎯 Load environment variables
load_dotenv()

#? 🤖 Initialize LLM and memory
llm = GoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.environ["GEMINI_API_KEY"]
)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

#? 📋 Global storage for application info
application_info = {"name": None, "email": None, "skills": None}

#? 📝 Extract info from plain text (chat or resume)
def extract_application_info(text: str) -> str:
    """Extract name, email, and skills from user input."""
    name_match = re.search(r"(?:my name is|i am)\s+([A-Za-z]+(?:['-][A-Za-z]+)*(?:\s+[A-Za-z]+(?:['-][A-Za-z]+)*)*)", text, re.IGNORECASE)
    email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text)
    skills_match = re.search(r"(?:skills\s*:?\s*|i know|i can use)\s+(.+)", text, re.IGNORECASE)

    if name_match:
        application_info["name"] = name_match.group(1).title()
    if email_match:
        application_info["email"] = email_match.group(0)
    if skills_match:
        application_info["skills"] = skills_match.group(1).strip()

    return "✅ Got it! Let me check what else I need."

#? 📄 Extract text from uploaded PDF CV
def extract_text_from_pdf(uploaded_file):
    """Extract text from an uploaded PDF file."""
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

#? 🔍 Extract info from CV text
def extract_info_from_cv(text: str):
    """Extract name, email, and skills from CV text."""
    extracted_info = {"name": None, "email": None, "skills": None}
    name_match = re.search(r"(?:Full Name:|Name:|- Name:)\s*([A-Za-z]+(?:['-][A-Za-z]+)*(?:\s+[A-Za-z]+(?:['-][A-Za-z]+)*)*)", text, re.IGNORECASE)
    email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text)
    skills_match = re.search(r"(?:- Skills:|- Skills\s*:|Skills\s*:)\s*(.+)", text, re.IGNORECASE)

    if name_match:
        extracted_info["name"] = name_match.group(1).strip()
    if email_match:
        extracted_info["email"] = email_match.group(0).strip()
    if skills_match:
        skills = skills_match.group(1).replace("\n", ", ").strip()
        extracted_info["skills"] = re.sub(r"\s+", " ", skills)

    return extracted_info

#? 🏁 Goal checker
def check_application_goal(_: str) -> str:
    """Check if all application info is collected."""
    if all(application_info.values()):
        return f"🎉 You're ready! Name: {application_info['name']}, Email: {application_info['email']}, Skills: {application_info['skills']}."
    else:
        missing = [k for k, v in application_info.items() if not v]
        return f"⏳ Still need: {', '.join(missing)}"

#? 🛠️ Define tools for LangChain agent
tools = [
    Tool(
        name="extract_application_info",
        func=extract_application_info,
        description="Extracts name, email, and skills from user input."
    ),
    Tool(
        name="check_application_goal",
        func=check_application_goal,
        description="Checks if all required application info is collected."
    )
]

#? 🤖 Initialize LangChain agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    memory=memory,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=False
)

# ?🎨 Streamlit UI Configuration
st.set_page_config(page_title="🎯 Job Application Assistant", layout="centered")
st.title("🧠 Job Application Assistant")
st.markdown("""
    Welcome to your **Job Application Assistant**! 🚀  
    Provide your **name**, **email**, and **skills** to complete your application.  
    You can also upload a resume for automatic info extraction! 📄
""")

# 📦 Session state initialization
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "goal_complete" not in st.session_state:
    st.session_state.goal_complete = False
if "download_ready" not in st.session_state:
    st.session_state.download_ready = False
if "application_summary" not in st.session_state:
    st.session_state.application_summary = ""

#? 📤 Sidebar: Upload resume
with st.sidebar:
    st.header("📤 Upload Resume (Optional)")
    resume = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

    if resume:
        st.success("✅ Resume uploaded successfully!")
        text = extract_text_from_pdf(resume)
        extracted = extract_info_from_cv(text)
        for key in application_info:
            if extracted[key]:
                application_info[key] = extracted[key]
        st.info("🔍 Extracted Info from Resume:")
        for key, value in extracted.items():
            st.markdown(f"**{key.capitalize()}:** {value or 'Not found'}")
        if any(extracted.values()):
            download_content = (
                f"Extracted Information:\n"
                f"Name: {extracted['name'] or 'Not found'}\n"
                f"Email: {extracted['email'] or 'Not found'}\n"
                f"Skills: {extracted['skills'] or 'Not found'}\n"
            )
            st.download_button(
                label="📥 Download Extracted Info",
                data=download_content,
                file_name="extracted_info.txt",
                mime="text/plain"
            )

    #? 🔄 Reset chat button
    if st.button("🔄 Reset Chat"):
        st.session_state.chat_history.clear()
        st.session_state.goal_complete = False
        st.session_state.download_ready = False
        st.session_state.application_summary = ""
        for key in application_info:
            application_info[key] = None
        st.rerun()

#? 💬 Chat input
user_input = st.chat_input("Type your message here... 💬")

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

# 🖥️ Chat UI with avatars
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

#? 🎉 Final success message
if st.session_state.goal_complete:
    st.success("🎉 All information collected! You're ready to apply!")

# ?📥 Download summary button
if st.session_state.download_ready:
    st.download_button(
        label="📥 Download Application Summary",
        data=st.session_state.application_summary,
        file_name="application_summary.txt",
        mime="text/plain"
    )