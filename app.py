import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Setup Environment
load_dotenv()

# API Key එක ලබා ගැනීම
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("API Key is missing.")
    st.stop()

# 2. Configure Gemini
genai.configure(api_key=api_key)

# 3. Setup Model - අපි භාවිතා කරන්නේ 'gemini-pro' (මේක ඕනම තැනක වැඩ)
try:
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"Error setting up model: {e}")

# 4. App UI
st.set_page_config(page_title="Kaputa AI", page_icon="🐦")
st.title("Kaputa AI 🐦")
st.caption("Powered by Gemini Pro")

# 5. Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "model", "content": "ආයුබෝවන්! මම Kaputa. මට ඔයාට කොහොමද උදව් කරන්න පුළුවන්?"})

# 6. Display Chat
for message in st.session_state.messages:
    role = "assistant" if message["role"] == "model" else "user"
    with st.chat_message(role):
        st.markdown(message["content"])

# 7. Handle User Input
if prompt := st.chat_input("Ask something..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        # Chat Object එක හදනවා
        chat = model.start_chat(history=[
            {"role": "user", "parts": [m["content"]]} if m["role"] == "user"
            else {"role": "model", "parts": [m["content"]]}
            for m in st.session_state.messages
        ])
        
        response = chat.send_message(prompt)
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        
        st.session_state.messages.append({"role": "model", "content": response.text})
        
    except Exception as e:
        st.error(f"Error: {e}")