# To run this code you need to install the following dependencies:
# pip install google-genai

import os
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Gemini Configuration and Initialization ---

# Initialize the Gemini API client
# The client object is initialized once when the script runs
try:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    model_name = "gemini-2.0-flash"
except Exception as e:
    st.error(f"Error initializing Gemini client: {e}")
    st.stop() # Stop the app if initialization fails

# Define the system instruction and tools
SYSTEM_INSTRUCTION = """You are an expert in renewable energy. Your name is Sparks.
You are the chatbot for a renewable energy site selector system with 3 features: location analysis, resource estimation, and cost evaluation.
You can use Google Search to fetch real-time information about renewable energy. Engage interactively with users, explain concepts clearly, use interesting greetings, and share fun facts where appropriate."""

TOOLS = [
    types.Tool(
        googleSearch=types.GoogleSearch()
    )
]

# --- Streamlit Application Setup ---

# Set the page configuration
st.set_page_config(page_title="Sparks - Renewable Energy Chatbot", page_icon="⚡")

st.title("⚡ Sparks - The Renewable Energy Chatbot")
st.markdown("I'm your expert guide for renewable energy site selection, ready to analyze locations, estimate resources, and evaluate costs!")

# Initialize chat history in Streamlit's session state
# Session state is how Streamlit maintains data across user interactions
if "messages" not in st.session_state:
    # Initialize with the system message and an initial greeting for the user
    st.session_state.messages = [
        types.Content(
            role="system",
            parts=[types.Part.from_text(text=SYSTEM_INSTRUCTION)]
        ),
        {"role": "assistant", "content": "Hello! I'm Sparks. How can I power up your knowledge about renewable energy today?"}
    ]

# --- Function to generate response using Gemini ---

def generate_response(prompt: str):
    """Generates content from the Gemini model using the current history."""
    
    # Construct the contents list from the history, skipping the Streamlit dict format
    # and ensuring the history includes the system instruction (which is always the first item)
    contents = []
    for message in st.session_state.messages:
        if isinstance(message, types.Content):
            contents.append(message)
        elif isinstance(message, dict):
            # Convert previous messages in the display format back to types.Content
            role = "user" if message["role"] == "user" else "assistant"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=message["content"])]))
            
    # Add the new user prompt as a types.Content object
    user_message_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=prompt)]
    )
    contents.append(user_message_content)

    try:
        # Generate response with Google Search tool and safety settings
        response = client.models.generate_content(
            model=model_name,
            contents=contents, # Pass the full history for context
            config=types.GenerateContentConfig(
                tools=TOOLS,
                temperature=0.45,
                safety_settings=[
                    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_ONLY_HIGH"),
                    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_ONLY_HIGH"),
                    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_ONLY_HIGH"),
                    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH"),
                ],
            )
        )
        
        # Extract the model's reply
        model_reply = response.text if response.text else "I couldn't generate a definitive response."
        
        # Return the new user message content (for adding to history) and the reply
        return user_message_content, model_reply

    except Exception as e:
        # Handle API errors gracefully
        return user_message_content, f"An error occurred: I failed to connect to the Gemini service. ({e})"


# --- Display Chat History ---

# Display all messages from the session state, excluding the system instruction (index 0)
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Handle User Input ---

if prompt := st.chat_input("Ask me about renewable energy site selection..."):
    # 1. Display user message
    st.chat_message("user").markdown(prompt)

    # 2. Get response from the model
    # The loading spinner runs while the model is thinking
    with st.spinner("Sparks is consulting the grid..."):
        user_content_obj, model_reply = generate_response(prompt)
    
    # 3. Display assistant message
    with st.chat_message("assistant"):
        st.markdown(model_reply)
        
    # 4. Update session state with the new messages
    # Store messages in the simpler dictionary format for display persistence
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": model_reply})

#Terminal code
# import os
# from google import genai
# from google.genai import types
# from dotenv import load_dotenv

# load_dotenv()

# def generate():
#     client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
#     model_name = "gemini-2.5-flash"

#     # System instructions
#     system_message = types.Content(
#         role="system",
#         parts=[types.Part.from_text(text="""You are an expert in renewable energy. Your name is Sparks.
# You are the chatbot for a renewable energy site selector system with 3 features: location analysis, resource estimation, and cost evaluation.
# You can use Google Search to fetch real-time information about renewable energy. Engage interactively with users, explain concepts clearly, use interesting greetings, and share fun facts about renewable energy when it is appropriate.""")]
#     )

#     # Chat history
#     history = [system_message]

#     print("⚡ Sparks Bot is ready! Type 'exit' to quit.\n")

#     while True:
#         user_input = input("You: ")
#         if user_input.lower() in ["exit", "quit"]:
#             print("Goodbye!")
#             break

#         # Add user message
#         user_message = types.Content(
#             role="user",
#             parts=[types.Part.from_text(text=user_input)]
#         )
#         history.append(user_message)

#         # Define Google Search tool
#         tools = [
#             types.Tool(
#                 googleSearch=types.GoogleSearch()
#             )
#         ]

#         # Generate response with Google Search tool
#         response = client.models.generate_content(
#             model=model_name,
#             contents=[user_message],
#             config=types.GenerateContentConfig(
#                 tools=tools,
#                 temperature=0.45,
#                 safety_settings=[
#                     types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_ONLY_HIGH"),
#                     types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_ONLY_HIGH"),
#                     types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_ONLY_HIGH"),
#                     types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH"),
#                 ],
#             )
#         )

#         # Extract model reply
#         model_reply = response.text if response.text else None
#         if not model_reply:
#             for part in response.candidates[0].content.parts:
#                 if part.text:
#                     model_reply = part.text
#                     break

#         if model_reply:
#             print(f"Sparks: {model_reply}\n")

#             # Append assistant message to history
#             assistant_message = types.Content(
#                 role="assistant",
#                 parts=[types.Part.from_text(text=model_reply)]
#             )
#             history.append(assistant_message)
#         else:
#             print("Sparks: I'm sorry, I couldn't generate a response.\n")

# if __name__ == "__main__":
#     generate()




#ORIGINAL
# import base64
# import os
# from google import genai
# from google.genai import types

# from dotenv import load_dotenv
# load_dotenv()




# def generate():
#     client = genai.Client(
#         api_key=os.getenv("GEMINI_API_KEY"),
#     )

#     model = "gemini-2.0-flash"
#     contents = [
#         types.Content(
#             role="user",
#             parts=[
#                 types.Part.from_text(text="""INSERT_INPUT_HERE"""),
#             ],
#         ),
#     ]
#     tools = [
#         types.Tool(googleSearch=types.GoogleSearch(
#         )),
#     ]
#     generate_content_config = types.GenerateContentConfig(
#         temperature=0.45,
#         safety_settings=[
#             types.SafetySetting(
#                 category="HARM_CATEGORY_HARASSMENT",
#                 threshold="BLOCK_ONLY_HIGH",  # Block few
#             ),
#             types.SafetySetting(
#                 category="HARM_CATEGORY_HATE_SPEECH",
#                 threshold="BLOCK_ONLY_HIGH",  # Block few
#             ),
#             types.SafetySetting(
#                 category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
#                 threshold="BLOCK_ONLY_HIGH",  # Block few
#             ),
#             types.SafetySetting(
#                 category="HARM_CATEGORY_DANGEROUS_CONTENT",
#                 threshold="BLOCK_ONLY_HIGH",  # Block few
#             ),
#         ],
#         tools=tools,
#         system_instruction=[
#             types.Part.from_text(text="""You are an expert in renewable energy field. our name is Sparks. You are the chatbot assigned to a renewable energy site selector system. the system has 3 features which are location analysis, resource estimation, and cost evaluation. 
# You should be able to engage in conversation about renewable energy and related fields and answer the questions. Engage with the users interactively and if asked explain the scientific concepts regarding the renewable energy in a way that is easily understandable but in a formal way. 
# It would be appreciated if you use interesting greetings and share fun facts regarding this field in appropriate times to make the conversation interesting. """),
#         ],
#     )

#     for chunk in client.models.generate_content_stream(
#         model=model,
#         contents=contents,
#         config=generate_content_config,
#     ):
#         print(chunk.text, end="")

# if __name__ == "__main__":
#     generate()
