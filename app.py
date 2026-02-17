import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Environment variables setup
load_dotenv()

# Streamlit Cloud එකේදී API Key එක ගන්න විදිය
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.getenv("GEMINI_API_KEY")

# API Key Check
if not api_key:
    st.error("API Key එක හමු නොවීය. කරුණාකර Settings වල Secrets පරීක්ෂා කරන්න.")
    st.stop()

genai.configure(api_key=api_key)

# 2. Page Config
st.set_page_config(page_title="Kaputa AI", page_icon="🐦")
st.title("Kaputa AI 🐦")
st.caption("Developed by Adheesha | Powered by Gemini Pro")

# 3. Model Setup (Changed to gemini-pro for stability)
# system_instruction අයින් කළා මොකද gemini-pro එකේ පරණ version එකේ ඒක support කරන්නේ නෑ.
model = genai.GenerativeModel("gemini-pro")

# 4. Chat History Setup
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Kaputa ගේ පළවෙනි මැසේජ් එක මැනුවලි දාමු
    st.session_state.messages.append({"role": "model", "content": "ආයුබෝවන්! මම කපුටා (Kaputa). මම Adheesha හදපු AI සහයකයා. මොනවද දැනගන්න ඕන?"})

# 5. Display History
for message in st.session_state.messages:
    role = "assistant" if message["role"] == "model" else "user"
    with st.chat_message(role):
        st.markdown(message["content"])

# 6. User Input Handling
if prompt := st.chat_input("අහන්න ඕන දෙයක් කියන්න..."):
    # User message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AI Response
    try:
        # Chat Session එක හදමු
        chat = model.start_chat(history=[
            {"role": "user", "parts": [m["content"]]} if m["role"] == "user"
            else {"role": "model", "parts": [m["content"]]}
            for m in st.session_state.messages
        ])
        
        response = chat.send_message(prompt)
        
        # Display response
        with st.chat_message("assistant"):
            st.markdown(response.text)
        
        # Save to history
        st.session_state.messages.append({"role": "model", "content": response.text})
        
    except Exception as e:
        st.error(f"Error එකක් ආවා: {e}")