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
    # මම මෙතනට ලස්සන කක්කෙක්ගේ (Bird) පින්තූරයක් දැම්මා
    st.image("https://cdn-icons-png.flaticon.com/512/12222/12222560.png", width=120)
    st.markdown("<h2 style='text-align:center; color:white;'>Kaputa AI Pro</h2>", unsafe_allow_html=True)
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
