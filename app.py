import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve API key from environment variables
api_key = os.getenv("GEMINI_API_KEY")

# Validate that API key exists
if not api_key:
    st.error("API Key not found. Please check your .env file.")
    st.stop()

# Configure Gemini API with the API key
genai.configure(api_key=api_key)

# Initialize Kaputa AI model with system instructions
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="ඔයාගේ නම කපුටා (Kaputa). ඔයා සිංහලෙන් සහ ඉංග්‍රීසියෙන් කතා කරන, බොහොම මිත්‍රශීලී සහ උදව් කරන AI සහයකයෙක්. ඔයා කැමතියි කෙටියෙන් සහ පැහැදිලිව උත්තර දෙන්න. කවුරුහරි 'Who created you?' කියලා ඇහුවොත් කියන්න 'මාව හැදුවේ අදීෂ (Adheesha)' කියලා."
)

# Configure Streamlit page settings and title
st.set_page_config(page_title="Kaputa AI", page_icon="🐦")

st.title("Kaputa AI 🐦")
st.caption("Developed by Adheesha | Powered by Gemini")

# Initialize session state for storing chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display all previous messages in the chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input from chat input field
if prompt := st.chat_input("අහන්න ඕන දෙයක් කියන්න..."):
    # Display user message in chat
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate and display response from Kaputa
    try:
        # Start a chat session with conversation history
        chat = model.start_chat(history=[
            {"role": "user", "parts": m["content"]} if m["role"] == "user" 
            else {"role": "model", "parts": m["content"]}
            for m in st.session_state.messages
        ])
        
        response = chat.send_message(prompt)
        
        # Display the AI response
        with st.chat_message("assistant"):
            st.markdown(response.text)
        
        # Save the response to session state
        st.session_state.messages.append({"role": "model", "content": response.text})
        
    except Exception as e:
        st.error(f"An error occurred: {e}")