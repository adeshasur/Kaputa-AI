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

# 2. Page Styling: iOS 26 Futuristic
st.set_page_config(page_title="Kaputa AI Pro - iOS 26", page_icon="🐦", layout="wide", initial_sidebar_state="expanded")

# --- iOS 26 FUTURISTIC CSS ---
st.markdown("""
<style>
    /* Global Reset & Fonts */
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600&display=swap'); /* Using SF Pro clone or close match */
    
    :root {
        --ios-bg: #000000;
        --ios-card: #1C1C1E;
        --ios-card-hover: #2C2C2E;
        --ios-blue: #0A84FF;
        --ios-purple: #BF5AF2;
        --ios-glass: rgba(28, 28, 30, 0.65);
        --ios-border: rgba(255, 255, 255, 0.1);
        --ios-text: #F2F2F7;
        --ios-text-secondary: #8E8E93;
    }

    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; /* Fallback to system fonts for max speed */
        background-color: var(--ios-bg) !important;
        color: var(--ios-text) !important;
    }

    /* Sidebar: Frosted Glass / Mesh Gradient Feel */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.8) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: 1px solid var(--ios-border);
    }
    
    /* Hide Default Header/Footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main Content Area */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #1a1a2e 0%, #000000 60%);
    }

    /* iOS 26 Input Fields (Floating Pills) */
    .stTextInput input {
        background-color: var(--ios-card) !important;
        border: 1px solid var(--ios-border) !important;
        color: white !important;
        border-radius: 99px !important; /* Full pill shape */
        padding: 15px 25px !important;
        font-size: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    .stTextInput input:focus {
        border-color: var(--ios-blue) !important;
        background-color: var(--ios-card-hover) !important;
        box-shadow: 0 0 0 2px rgba(10, 132, 255, 0.3), 0 8px 30px rgba(10, 132, 255, 0.1);
    }

    /* Buttons: Neon Glass */
    .stButton button {
        background: linear-gradient(135deg, var(--ios-blue), #0051D5) !important;
        color: white !important;
        border: none !important;
        border-radius: 18px !important; /* iOS squircle-ish */
        padding: 10px 24px !important;
        font-weight: 500 !important;
        box-shadow: 0 4px 15px rgba(10, 132, 255, 0.4);
        transition: transform 0.1s ease, box-shadow 0.2s ease;
    }
    .stButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(10, 132, 255, 0.6);
    }
    .stButton button:active {
        transform: scale(0.96);
    }

    /* Cards / Chat Bubbles */
    .stChatMessage {
        background-color: transparent; /* Clean look */
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding: 20px 0;
    }
    [data-testid="stChatMessageContent"] {
        background-color: transparent !important;
        color: var(--ios-text) !important;
        font-size: 17px; /* iOS body size */
        line-height: 1.5;
    }
    
    /* Avatar Styling */
    .stChatMessageAvatar {
        background-color: var(--ios-card);
        border: 1px solid var(--ios-border);
        border-radius: 50%;
    }

    /* Radios as Segmented Control */
    .stRadio [role="radiogroup"] {
        background-color: var(--ios-card);
        padding: 4px;
        border-radius: 12px;
        display: flex;
        gap: 0;
    }
    .stRadio label {
        flex: 1;
        text-align: center;
        background: transparent;
        border-radius: 8px;
        padding: 8px 16px;
        margin: 0;
        transition: background 0.2s;
        border: none;
    }
    /* Note: Streamlit radio styling is tricky, kept minimal for stability */

    /* Scrollbars (Hidden/Sleek) */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: #333;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }

</style>
""", unsafe_allow_html=True)

# 3. Model Setup
try:
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception as e:
    st.error(f"System Error: {e}")

# 4. SIDEBAR - iOS 26 Look
with st.sidebar:
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True) # Spacer
    
    # Logo Area with Glow
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        try:
            logo = Image.open("assets/logo.png")
            st.image(logo, use_container_width=True)
        except:
            st.markdown("## 🦅")
            
    st.markdown("""
        <div style='text-align: center; margin-bottom: 30px;'>
            <h2 style='font-weight: 700; font-size: 24px; margin: 0; background: linear-gradient(90deg, #fff, #888); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Kaputa AI</h2>
            <p style='color: #666; font-size: 12px; margin-top: 5px; letter-spacing: 1px;'>DESIGNED FOR IOS 26</p>
        </div>
    """, unsafe_allow_html=True)

    # Navigation (Mode Selection)
    st.markdown("<p style='font-size: 12px; color: #666; font-weight: 600; padding-left: 10px;'>WORKSPACE</p>", unsafe_allow_html=True)
    mode = st.radio("Mode", ["💬  Chat", "✨  Create", "🔎  Research"], label_visibility="collapsed")
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("<p style='font-size: 12px; color: #666; font-weight: 600; padding-left: 10px;'>ACTIONS</p>", unsafe_allow_html=True)
    if st.button("New Session", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("<div style='margin-top: auto; padding-top: 50px; text-align: center; color: #444; font-size: 10px;'>v5.0 Ultra</div>", unsafe_allow_html=True)

# 5. MAIN CONTENT
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "model", "content": "Kaputa AI is ready."}]

# Header (Floating Glass)
st.markdown("""
    <div style='
        position: fixed; 
        top: 20px; 
        right: 20px; 
        background: rgba(28, 28, 30, 0.6); 
        backdrop-filter: blur(15px); 
        padding: 8px 16px; 
        border-radius: 20px; 
        border: 1px solid rgba(255,255,255,0.1); 
        z-index: 999; 
        font-size: 12px; 
        font-weight: 600; 
        color: #8E8E93;'>
        Kaputa OS 1.0
    </div>
""", unsafe_allow_html=True)

# Chat Loop
for msg in st.session_state.messages:
    role = "assistant" if msg["role"] == "model" else "user"
    avatar = "assets/logo.png" if role == "assistant" else None # User uses default
    
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg["content"])

# Input Area
if prompt := st.chat_input("Type a message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="assets/logo.png"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            # Add a slight artificial delay for "thinking" feel? No, speed is luxury.
            response = model.generate_content(prompt, stream=True)
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "model", "content": full_response})
        except Exception as e:
            st.error(f"Error: {e}")
