import os
from dotenv import load_dotenv
from typing import cast
import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig

# Load environment variables from .env file
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# Check if the API key is present; raise an error if not
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

@cl.on_chat_start
async def start():
    # Initialize the external client for Gemini API
    external_client = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=external_client
    )

    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )

    # Define beauty-specific instructions for the agent
    beauty_instructions = """
    You are a Beauty Expert Assistant specializing in natural remedies and beauty tips. 
    Provide only advice related to natural skincare, haircare, and wellness remedies using ingredients like aloe vera, honey, turmeric, coconut oil, etc. 
    If the user asks about non-beauty topics, politely redirect them with: 
    'Sorry, I'm here to help with natural beauty remedies! Try asking about skincare, haircare, or wellness tips.' 
    Use a friendly and engaging tone, and include emojis like 💆‍♀️, 🌿, or ✨ to make responses appealing.
    """

    # Initialize an empty chat history in the session
    cl.user_session.set("chat_history", [])

    cl.user_session.set("config", config)
    agent = Agent(name="BeautyBot", instructions=beauty_instructions, model=model)
    cl.user_session.set("agent", agent)

    # Send a beauty-themed welcome message
    await cl.Message(content="Welcome to BeautyBot! 💖 I'm here to share natural remedies for glowing skin, healthy hair, and wellness. 🌿 Ask me about DIY masks, hair treatments, or beauty tips! ✨").send()

@cl.on_message
async def main(message: cl.Message):
    """Process incoming messages and generate beauty-specific responses."""
    # Send a thinking message with a beauty-themed touch
    msg = cl.Message(content="Mixing up some natural beauty magic... 🌸")
    await msg.send()

    agent = cast(Agent, cl.user_session.get("agent"))
    config = cast(RunConfig, cl.user_session.get("config"))

    # Retrieve the chat history from the session
    history = cl.user_session.get("chat_history") or []
    
    # Append the user's message to the history
    history.append({"role": "user", "content": message.content})

    try:
        print("\n[CALLING_BEAUTY_AGENT_WITH_CONTEXT]\n", history, "\n")
        result = Runner.run_sync(
            starting_agent=agent,
            input=history,
            run_config=config
        )
        
        response_content = result.final_output
        
        # Update the thinking message with the actual response
        msg.content = response_content
        await msg.update()
    
        # Update the session with the new history
        cl.user_session.set("chat_history", result.to_input_list())
        
        # Log the interaction for debugging
        print(f"User: {message.content}")
        print(f"BeautyBot: {response_content}")      
    except Exception as e:
        # Provide a user-friendly error message with a beauty twist
        msg.content = f"Oops, something went wrong while brewing your beauty remedy! 💔 Please try again or ask about a natural beauty tip. Error: {str(e)}"
        await msg.update()
        print(f"Error: {str(e)}")