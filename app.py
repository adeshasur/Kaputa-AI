import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
from gtts import gTTS
import tempfile
from duckduckgo_search import DDGS
import PyPDF2

# 1. Configuration
load_dotenv()
api_key = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")

# 404 Error එක වැලැක්වීමට කෙලින්ම API version එක සහ transport එක configure කිරීම
genai.configure(api_key=api_key, transport='rest')

# 2. Page Styling (Apple Dark Look)
st.set_page_config(page_title="Kaputa AI Pro", page_icon="🐦", layout="wide")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
        html, body, [class*="css"] { 
            font-family: 'Inter', sans-serif; 
            background-color: #000 !important; 
            color: #F5F5F7 !important; 
        }
        .stApp { background-color: #000 !important; }
        [data-testid="stSidebar"] { 
            background-color: #1C1C1E !important; 
            border-right: 1px solid #2C2C2E !important; 
        }
        /* Apple-style Blue Pill Buttons */
        .stButton button {
            background-color: #0A84FF !important;
            color: white !important;
            border-radius: 20px !important;
            border: none !important;
        }
        header {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. Model Setup (Stable Fix)
try:
    # 1.5-flash එක models/ path එකත් එක්කම ලබා දීම
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception as e:
    st.error(f"System Error: {e}")

# 4. SIDEBAR - මෙතන තමයි ඔයාගේ CROW LOGO එක තියෙන්නේ
with st.sidebar:
    # Inline SVG Eagle/Crow Logo - no external CDN dependency
    st.markdown('''
        <div style="text-align:center; padding: 20px 0 5px 0;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="100" height="100">
                <defs>
                    <linearGradient id="birdGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#0A84FF;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#5E5CE6;stop-opacity:1" />
                    </linearGradient>
                </defs>
                <circle cx="32" cy="32" r="30" fill="#1C1C1E" stroke="url(#birdGrad)" stroke-width="2"/>
                <!-- Eagle/Bird body -->
                <path d="M18 38 C18 38 22 28 32 24 C36 22 42 22 46 26 C48 28 48 32 46 34 L42 32 L44 28 C44 28 40 24 34 26 C28 28 24 34 22 38 Z" fill="url(#birdGrad)"/>
                <!-- Wing spread -->
                <path d="M26 30 C26 30 20 24 14 22 C14 22 20 26 22 30 Z" fill="url(#birdGrad)" opacity="0.8"/>
                <path d="M38 26 C38 26 44 20 50 18 C50 18 44 22 40 28 Z" fill="url(#birdGrad)" opacity="0.8"/>
                <!-- Head/beak -->
                <circle cx="44" cy="26" r="3" fill="url(#birdGrad)"/>
                <path d="M46 25 L52 23 L47 27 Z" fill="#FF9F0A"/>
                <!-- Eye -->
                <circle cx="44.5" cy="25.5" r="1" fill="white"/>
                <!-- Tail feathers -->
                <path d="M18 38 L12 42 L16 38 L10 40 L16 37 Z" fill="url(#birdGrad)" opacity="0.7"/>
            </svg>
        </div>
    ''', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:white; margin-top:5px;'>Kaputa AI Pro</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    mode = st.radio("SELECT MODE", ["💬 Chat", "📝 Quiz", "🌍 Research"])
    
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("<div style='margin-top:100px; opacity:0.3; font-size:10px; text-align:center;'>Engineered by Adheesha Sooriyaarachchi<br>v4.5 Stable</div>", unsafe_allow_html=True)

# 5. CHAT LOGIC
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "model", "content": "ආයුබෝවන්! මම Kaputa. දැන් මගේ පෙනුම සහ ලෝගෝ එක ඔක්කොම හරි! 🐦"}]

for msg in st.session_state.messages:
    role = "assistant" if msg["role"] == "model" else "user"
    with st.chat_message(role):
        st.markdown(msg["content"])

if prompt := st.chat_input("Enter your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            try:
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "model", "content": response.text})
            except Exception as e:
                st.error(f"API Error (Quota/Model): {e}")
