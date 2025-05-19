from agents import Agent, Runner, function_tool
from agents.extensions.models.litellm_model import LitellmModel
from dotenv import load_dotenv
import os
import re
import sys
import json

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ Error: GEMINI_API_KEY not found in environment variables.")
    sys.exit(1)

# Store application information
application_info = {
    "name": None,
    "email": None,
    "skills": None
}

# Function to save application info to JSON file in project root
def save_to_json(data: dict, filename: str = "application_info.json"):
    try:
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Assume project root is the parent directory of the script
        project_root = os.path.dirname(script_dir)
        # Construct full path to save the JSON file in project root
        file_path = os.path.join(project_root, filename)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        return f"✅ Application info saved to {file_path}"
    except Exception as e:
        return f"❌ Error saving to JSON: {e}"

# Tool to extract name, email, and skills from text
@function_tool
def extract_application_info(text: str) -> str:
    name_match = re.search(r"(?:my name is|i am)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", text, re.IGNORECASE)
    email_match = re.search(r"\b[\w.-]+@[\w.-]+\.\w+\b", text)
    skills_match = re.search(r"(?:skills are|i know|i can use)\s+(.+)", text, re.IGNORECASE)

    response = []
    if name_match:
        name = name_match.group(1)
        if name:
            application_info["name"] = name.title()
            response.append("✅ Name saved.")

    if email_match:
        application_info["email"] = email_match.group(0)
        response.append("✅ Email saved.")
    if skills_match:
        skills = skills_match.group(1)
        if skills:
            application_info["skills"] = skills.strip()
            response.append("✅ Skills saved.")

    if not any([name_match, email_match, skills_match]):
        return "❓ I couldn't extract any info. Could you please provide your name, email, or skills?"

    return " ".join(response) + " Let me check what else I need."

# Tool to check if all required information is collected
@function_tool
def check_application_goal(dummy: str) -> str:
    if all(application_info.values()):
        # Save to JSON when all info is collected
        save_result = save_to_json(application_info)
        return (f"✅ You're ready! Name: {application_info['name']}, Email: {application_info['email']}, "
                f"Skills: {application_info['skills']}. {save_result}")
    else:
        missing = [k for k, v in application_info.items() if not v]
        return f"⏳ Still need: {', '.join(missing)}. Please ask the user to provide this."

# Initialize the agent
try:
    agent = Agent(
        name="Helpful job application assistant",
        instructions="""You are a helpful job application assistant.
Your goal is to collect the user's name, email, and skills.
Use the tools provided to extract this information and check whether all required data is collected.
Once everything is collected, save the info to a JSON file in the project root and inform the user that the application info is complete and stop.
""",
        model=LitellmModel(model="gemini/gemini-1.5-flash", api_key=GEMINI_API_KEY),
        tools=[extract_application_info, check_application_goal]
    )
    print("✅ Agent initialized successfully.")
except Exception as e:
    print(f"❌ Error initializing agent: {e}")
    sys.exit(1)

# Maintain conversation history for logging (not passed to Runner)
conversation_history = []

def run(message: str) -> str:
    try:
        # Add user message to history for logging
        conversation_history.append({"role": "user", "content": message})
        
        # Run the agent with the current message only
        result = Runner.run_sync(
            agent,
            message
        )
        
        # Add agent response to history for logging
        output = result.final_output
        conversation_history.append({"role": "assistant", "content": output})
        
        return output
    except Exception as e:
        return f"❌ Error running agent: {e}"

# Main interaction loop
print("📝 Hi! I'm your job application assistant. Please tell me your name, email, and skills.")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("👋 Bye! Good luck.")
        break

    response = run(user_input)
    print("Bot:", response)

    # Check if goal is achieved
    if "you're ready" in response.lower():
        print("🎉 Application info complete!")
        break