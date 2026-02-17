import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# API Key එක ගන්න
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("API Key එක දාන්න අමතක වෙලා!")
    st.stop()

genai.configure(api_key=api_key)

# App Title
st.set_page_config(page_title="Kaputa AI", page_icon="🐦")
st.title("Kaputa AI 🐦")

# --- Debugging කොටස (මේකෙන් බලාගන්න පුළුවන් මොන මොඩල් ද වැඩ කියලා) ---
try:
    # Model එක හරියටම Set කරගන්න
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # චැට් එක පටන් ගන්න
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "model", "content": "ආයුබෝවන්! මම Kaputa. කියන්න, මම කොහොමද උදව් කරන්නේ?"})

    for message in st.session_state.messages:
        role = "assistant" if message["role"] == "model" else "user"
        with st.chat_message(role):
            st.markdown(message["content"])

    if prompt := st.chat_input("මොනවද දැනගන්න ඕන?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
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
            st.error(f"Chat Error: {e}")

except Exception as e:
    st.error("Model එක හොයාගන්න බැරි වුනා. කරුණාකර requirements.txt එකේ google-generativeai>=0.8.3 තියෙනවද බලන්න.")
    st.error(f"Error Details: {e}")