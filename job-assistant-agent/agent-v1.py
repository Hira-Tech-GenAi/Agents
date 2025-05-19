from langchain.agents import initialize_agent, Tool, AgentType
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from typing import Dict, Optional
import os
import re
import json

#? 🌍 Load environment variables
load_dotenv()

#? 🤖 Initialize Gemini LLM
llm = GoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.environ["GEMINI_API_KEY"]
)

#? 🧠 Memory for maintaining chat history
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

#? 📦 Application data dictionary
application_info: Dict[str, Optional[str]] = {
    "name": None,
    "email": None,
    "skills": None
}

# 💾 Save data to JSON
def save_data_to_json(data: Dict[str, Optional[str]], filename: str = "application_info.json") -> None:
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# 🔍 Extract application info using regex
def extract_application_info(text: str) -> str:
    name_match = re.search(r"(?:my name is|i am)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", text, re.IGNORECASE)
    email_match = re.search(r"\b[\w.-]+@[\w.-]+\.\w+\b", text)
    skills_match = re.search(r"(?:skills are|i know|i can use)\s+(.+)", text, re.IGNORECASE)

    response = []
    if name_match:
        name = name_match.group(1)
        if name:
            application_info["name"] = name.title()
            response.append("🧑‍💼 Name saved!")

    if email_match:
        application_info["email"] = email_match.group(0)
        response.append("📧 Email saved!")

    if skills_match:
        skills = skills_match.group(1)
        if skills:
            application_info["skills"] = skills.strip()
            response.append("🛠️ Skills saved!")

    if any([name_match, email_match, skills_match]):
        save_data_to_json(application_info)  # 💾 Save data
        return " ".join(response) + " ✅ Let me check what else I need."
    else:
        return "❓ I couldn't extract any info. Please share your name, email, or skills."

# ✅ Check if all required fields are complete
def check_application_goal(_: str) -> str:
    if all(application_info.values()):
        save_data_to_json(application_info)  # 💾 Final save
        return (
            f"🎯 You're ready to go!\n"
            f"🧑‍💼 Name: {application_info['name']}\n"
            f"📧 Email: {application_info['email']}\n"
            f"🛠️ Skills: {application_info['skills']}"
        )
    else:
        missing = [k for k, v in application_info.items() if not v]
        return f"⏳ Still missing: {', '.join(missing)}. Please provide this info."

# 🛠️ Define tools for the agent
tools = [
    Tool(
        name="extract_application_info",
        func=extract_application_info,
        description="Use this to extract name, email, and skills from the user's message."
    ),
    Tool(
        name="check_application_goal",
        func=check_application_goal,
        description="Check if name, email, and skills are provided. If not, tell the user what is missing.",
        return_direct=True
    )
]

# 📜 System prompt for the agent
SYSTEM_PROMPT = """You are a helpful job application assistant.
Your goal is to collect the user's name, email, and skills.
Use the tools provided to extract this information and check whether all required data is collected.
Once everything is collected, inform the user that the application info is complete and stop.
"""

# 🤖 Initialize the agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    memory=memory,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={"system_message": SYSTEM_PROMPT}
)

# 💬 Conversation loop
print("👋 Hello! I'm your job application assistant. Please share your name, email, and skills to begin. 📝")

while True:
    user_input = input("🗣️ You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("👋 Goodbye! Best of luck with your job hunt. 🚀")
        break

    response = agent.invoke({"input": user_input})
    print("🤖 Bot:", response["output"])

    if "you're ready" in response["output"].lower():
        print("🎉 Application info complete! All the best! 🍀")
        break
