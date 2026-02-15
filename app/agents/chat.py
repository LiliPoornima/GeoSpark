# To run this code you need to install the following dependencies:
# pip install google-genai


"""
Sparks Renewable Energy Chatbot
--------------------------------
A conversational AI chatbot built using Google Gemini API
for renewable energy site selection support.

Features:
- Location Analysis
- Resource Estimation
- Cost Evaluation
"""

def generate():
    """
    Starts an interactive chatbot session powered by Gemini.

    - Loads API key from environment
    - Sets up system instructions and Google Search tool
    - Listens to user input in a loop
    - Generates contextual responses using the Gemini API
    """


#Terminal code
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def generate():
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    model_name = "gemini-2.5-flash"

    # System instructions
    system_message = types.Content(
        role="system",
        parts=[types.Part.from_text(text="""You are an expert in renewable energy. Your name is Sparks.
You are the chatbot for a renewable energy site selector system with 3 features: location analysis, resource estimation, and cost evaluation.
You can use Google Search to fetch real-time information about renewable energy. Engage interactively with users, explain concepts clearly, use interesting greetings, and share fun facts about renewable energy when it is appropriate.""")]
    )

    # Chat history
    history = [system_message]

    print("⚡ Sparks Bot is ready! Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Add user message
        user_message = types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_input)]
        )
        history.append(user_message)

        # Define Google Search tool
        tools = [
            types.Tool(
                googleSearch=types.GoogleSearch()
            )
        ]

        # Generate response with Google Search tool
        response = client.models.generate_content(
            model=model_name,
            contents=[user_message],
            config=types.GenerateContentConfig(
                tools=tools,
                temperature=0.45,
                safety_settings=[
                    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_ONLY_HIGH"),
                    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_ONLY_HIGH"),
                    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_ONLY_HIGH"),
                    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH"),
                ],
            )
        )

        # Extract model reply
        model_reply = response.text if response.text else None
        if not model_reply:
            for part in response.candidates[0].content.parts:
                if part.text:
                    model_reply = part.text
                    break

        if model_reply:
            print(f"Sparks: {model_reply}\n")

            # Append assistant message to history
            assistant_message = types.Content(
                role="assistant",
                parts=[types.Part.from_text(text=model_reply)]
            )
            history.append(assistant_message)
        else:
            print("Sparks: I'm sorry, I couldn't generate a response.\n")

if __name__ == "__main__":
    generate()




ORIGINAL
import base64
import os
from google import genai
from google.genai import types

from dotenv import load_dotenv
load_dotenv()




def generate():
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""INSERT_INPUT_HERE"""),
            ],
        ),
    ]
    tools = [
        types.Tool(googleSearch=types.GoogleSearch(
        )),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.45,
        safety_settings=[
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="BLOCK_ONLY_HIGH",  # Block few
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="BLOCK_ONLY_HIGH",  # Block few
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="BLOCK_ONLY_HIGH",  # Block few
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="BLOCK_ONLY_HIGH",  # Block few
            ),
        ],
        tools=tools,
        system_instruction=[
            types.Part.from_text(text="""You are an expert in renewable energy field. our name is Sparks. You are the chatbot assigned to a renewable energy site selector system. the system has 3 features which are location analysis, resource estimation, and cost evaluation. 
You should be able to engage in conversation about renewable energy and related fields and answer the questions. Engage with the users interactively and if asked explain the scientific concepts regarding the renewable energy in a way that is easily understandable but in a formal way. 
It would be appreciated if you use interesting greetings and share fun facts regarding this field in appropriate times to make the conversation interesting. """),
        ],
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")

if __name__ == "__main__":
    generate()
