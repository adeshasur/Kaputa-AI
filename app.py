import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
from gtts import gTTS
import tempfile
from duckduckgo_search import DDGS
import PyPDF2
from PIL import Image

# 1. Configuration
load_dotenv()
api_key = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")

# 404 Error Fix
genai.configure(api_key=api_key, transport='rest')

# 2. Page Styling (Cleaner, Premium Dark)
st.set_page_config(page_title="Kaputa AI Pro", page_icon="🐦", layout="wide")

# Subtle, high-quality CSS
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        /* Font & Background */
        html, body, [class*="css"] { 
            font-family: 'Inter', sans-serif; 
        }
        
        /* Sidebar: Cleaner, less blurred */
        [data-testid="stSidebar"] { 
            background-color: #0E1117; 
            border-right: 1px solid #1E1E1E;
        }
        
        /* Chat Messages: distinguishable but clean */
        .stChatMessage {
            background-color: transparent;
            border-bottom: 1px solid #1E1E1E;
        }

        /* Input Box */
        .stTextInput input {
            border-radius: 12px;
            border: 1px solid #333;
        }
        
        /* Hide Header/Footer */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
    </style>
""", unsafe_allow_html=True)

# 3. Model Setup
try:
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception as e:
    st.error(f"System Error: {e}")

# 4. SIDEBAR - NEW LOGO
with st.sidebar:
    try:
        # Load local logo
        logo = Image.open("assets/logo.png")
        st.image(logo, width=150)
    except:
        st.markdown("## 🦅 Kaputa AI")
    
    st.markdown("<h3 style='text-align: left; color: #aaa; margin-top: -10px;'>Professional AI</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    mode = st.radio("Mode", ["Chat", "Quiz", "Research"])
    
    st.markdown("---")
    if st.button("New Chat", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.rerun()

# 5. CHAT LOGIC
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "model", "content": "Hello! I am Kaputa AI. How can I help you today?"}]

for msg in st.session_state.messages:
    role = "assistant" if msg["role"] == "model" else "user"
    avatar = "assets/logo.png" if role == "assistant" else None
    
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg["content"])

if prompt := st.chat_input("Message Kaputa AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="assets/logo.png"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            # Stream response for better UX
            response = model.generate_content(prompt, stream=True)
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "model", "content": full_response})
        except Exception as e:
            st.error(f"Error: {e}")
