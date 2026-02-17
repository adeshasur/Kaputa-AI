import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
from gtts import gTTS
import tempfile
from duckduckgo_search import DDGS
from fpdf import FPDF
import PyPDF2
import json
from youtube_transcript_api import YouTubeTranscriptApi

# 1. Environment Setup
load_dotenv()

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("API Key not found!")
    st.stop()

genai.configure(api_key=api_key, transport='rest')

# Initialize theme state (default to Light mode for Apple aesthetic)
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

# 2. Page Config
st.set_page_config(
    page_title="Kaputa AI Pro",
    page_icon="⚡", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# Dynamic CSS Function
def get_theme_css(theme):
    if theme == "Dark":
        return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        :root {
            --apple-blue: #007AFF;
            --bg-main: #000000;
            --bg-card: #1C1C1E;
            --text-primary: #F2F2F7;
            --text-secondary: #8E8E93;
            --text-tertiary: #6E6E73;
        }

        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Display', sans-serif;
            color: var(--text-primary) !important;
            background-color: var(--bg-main) !important;
        }

        /* iOS Large Title */
        .main-title {
            font-size: 3.5rem;
            font-weight: 700;
            background: linear-gradient(180deg, #FFFFFF 0%, #888888 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
            text-align: center;
            letter-spacing: -1.5px;
        }
        
        .badge {
            color: #007AFF;
            font-size: 1rem;
            vertical-align: top;
            font-weight: 600;
            background: rgba(0, 122, 255, 0.15);
            padding: 4px 10px;
            border-radius: 20px;
        }

        /* Sidebar: Dark Glassmorphism */
        [data-testid="stSidebar"] {
            background: rgba(28, 28, 30, 0.85) !important;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            position: relative;
            padding-bottom: 80px;
            min-width: 280px !important;
            max-width: 280px !important;
        }
        [data-testid="stSidebar"] > div:first-child {
            width: 280px !important;
            background: transparent;
        }

        /* Dark Cards */
        .result-card {
            background-color: var(--bg-card);
            border-radius: 20px;
            padding: 24px;
            margin-top: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* Inputs: Dark Style */
        .stTextInput input, .stTextArea textarea {
            background-color: #2C2C2E !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            border-radius: 18px !important;
            padding: 16px !important;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: var(--apple-blue) !important;
            box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.3);
        }
        
        /* Buttons: Premium */
        .stButton button {
            background-color: #007AFF !important;
            color: white !important;
            border-radius: 9999px !important;
            padding: 10px 24px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(0, 122, 255, 0.4);
            border: none !important;
            transition: all 0.2s ease;
        }
        .stButton button:hover {
            background-color: #0051D5 !important;
            box-shadow: 0 6px 16px rgba(0, 122, 255, 0.5);
        }
        .stButton button:active {
            transform: scale(0.97);
        }

        /* Tabs: Dark Segmented */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: rgba(255, 255, 255, 0.05);
            padding: 5px;
            border-radius: 16px;
            display: inline-flex;
            justify-content: center;
            margin: 0 auto;
            width: fit-content;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            border: none;
            color: var(--text-secondary);
            font-size: 0.9rem;
            padding: 8px 20px;
            border-radius: 12px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #3A3A3C !important;
            color: var(--text-primary) !important;
            font-weight: 600;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
        }

        /* Footer: Dark */
        .footer {
            position: fixed;
            bottom: 10px;
            left: 10px;
            width: 260px;
            background: rgba(28, 28, 30, 0.95);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            color: var(--text-tertiary);
            padding: 8px 10px;
            border-radius: 14px;
            font-size: 0.65rem;
            text-align: center;
            z-index: 10000;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
            line-height: 1.4;
        }

        /* Crow Logo */
        .crow-logo {
            text-align: center;
            font-size: 3.5rem;
            padding: 20px 0 10px 0;
            filter: grayscale(0%);
        }

        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
    </style>
"""
    else:  # Light Mode
        return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        :root {
            --apple-blue: #007AFF;
            --bg-main: #F9F9F9;
            --bg-card: #FFFFFF;
            --text-primary: #1D1D1F;
            --text-secondary: #424245;
            --text-tertiary: #86868B;
        }

        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Display', sans-serif;
            color: var(--text-primary) !important;
            background-color: var(--bg-main) !important;
        }

        /* iOS Large Title */
        .main-title {
            font-size: 3.5rem;
            font-weight: 700;
            background: linear-gradient(180deg, #1D1D1F 0%, #424245 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
            text-align: center;
            letter-spacing: -1.5px;
        }
        
        .badge {
            color: #007AFF;
            font-size: 1rem;
            vertical-align: top;
            font-weight: 600;
            background: rgba(0, 122, 255, 0.12);
            padding: 4px 10px;
            border-radius: 20px;
        }

        /* Sidebar: Glassmorphism */
        [data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.7) !important;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-right: 1px solid rgba(0, 0, 0, 0.08);
            position: relative;
            padding-bottom: 80px;
            min-width: 280px !important;
            max-width: 280px !important;
        }
        [data-testid="stSidebar"] > div:first-child {
            width: 280px !important;
            background: transparent;
        }

        /* White Cards */
        .result-card {
            background-color: var(--bg-card);
            border-radius: 20px;
            padding: 24px;
            margin-top: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
            border: 1px solid rgba(0, 0, 0, 0.06);
        }

        /* Inputs: Light iMessage Style */
        .stTextInput input, .stTextArea textarea {
            background-color: var(--bg-card) !important;
            border: 1px solid rgba(0, 0, 0, 0.1) !important;
            color: var(--text-primary) !important;
            border-radius: 18px !important;
            padding: 16px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: var(--apple-blue) !important;
            box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.15);
        }
        
        /* Buttons: Premium */
        .stButton button {
            background-color: #007AFF !important;
            color: white !important;
            border-radius: 9999px !important;
            padding: 10px 24px !important;
            font-weight: 600 !important;
            box-shadow: 0 2px 8px rgba(0, 122, 255, 0.25);
            border: none !important;
            transition: all 0.2s ease;
        }
        .stButton button:hover {
            background-color: #0051D5 !important;
            box-shadow: 0 4px 12px rgba(0, 122, 255, 0.35);
        }
        .stButton button:active {
            transform: scale(0.97);
        }

        /* Tabs: Light Segmented */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: rgba(0, 0, 0, 0.05);
            padding: 5px;
            border-radius: 16px;
            display: inline-flex;
            justify-content: center;
            margin: 0 auto;
            width: fit-content;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            border: none;
            color: var(--text-tertiary);
            font-size: 0.9rem;
            padding: 8px 20px;
            border-radius: 12px;
        }
        .stTabs [aria-selected="true"] {
            background-color: var(--bg-card) !important;
            color: var(--text-primary) !important;
            font-weight: 600;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        /* Footer: Light */
        .footer {
            position: fixed;
            bottom: 10px;
            left: 10px;
            width: 260px;
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            color: var(--text-tertiary);
            padding: 8px 10px;
            border-radius: 14px;
            font-size: 0.65rem;
            text-align: center;
            z-index: 10000;
            border: 1px solid rgba(0, 0, 0, 0.08);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            line-height: 1.4;
        }

        /* Crow Logo */
        .crow-logo {
            text-align: center;
            font-size: 3.5rem;
            padding: 20px 0 10px 0;
            filter: grayscale(20%);
        }

        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
    </style>
"""

# Apply current theme CSS
st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)

# Crow Logo in Sidebar
with st.sidebar:
    st.markdown('''
        <div style="text-align: center; padding: 20px 0 15px 0;">
            <img src="https://cdn-icons-png.flaticon.com/512/12222/12222560.png" alt="Kaputa Logo" style="width: 80px; height: 80px; border-radius: 20px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
        </div>
    ''', unsafe_allow_html=True)
    st.markdown("---")


# --- HEADER SECTION ---
st.markdown('<div class="main-title">Kaputa AI <span class="badge">PRO</span></div>', unsafe_allow_html=True)
st.caption("Advanced AI Workspace")

# --- HELPER FUNCTIONS ---
def search_web(query):
    try:
        results = DDGS().text(query, max_results=3)
        return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
    except:
        return None

def create_pdf(messages):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Kaputa AI - Session Export", ln=True, align='C')
    pdf.ln(10)
    for msg in messages:
        role = "User" if msg['role'] == "user" else "AI"
        content = msg['content'].encode('latin-1', 'replace').decode('latin-1') 
        pdf.multi_cell(0, 10, txt=f"{role}: {content}")
        pdf.ln(5)
    return pdf.output(dest='S').encode('latin-1')

def get_video_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be" in url:
        return url.split("/")[-1]
    return None

# --- MODEL (Gemini 2.0 Flash) ---
try:
    # Using models/ prefix to avoid 404 errors
    model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
except:
    st.error("System Error: Model connection failed.")

# ==========================================
# 🚀 MAIN WORKSPACE (Tabs)
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["Chat", "Quiz", "Research", "Dev"])

# ------------------------------------------
# TAB 1: CHAT WORKSPACE
# ------------------------------------------
with tab1:
    with st.sidebar:
        st.caption("SETTINGS")
        enable_search = st.toggle("Web Access", value=True)
        
        st.caption("CONTEXT")
        uploaded_pdf = st.file_uploader("References (PDF)", type="pdf", label_visibility="collapsed")
        pdf_text = ""
        if uploaded_pdf:
            try:
                reader = PyPDF2.PdfReader(uploaded_pdf)
                for page in reader.pages:
                    pdf_text += page.extract_text()
                st.success("Context Loaded")
            except:
                st.error("File Error")

        st.divider()
        st.download_button(
            label="Download Session",
            data=create_pdf(st.session_state.messages if "messages" in st.session_state else []),
            file_name="session_log.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        # Footer at bottom of sidebar
        st.markdown('<div class="footer">Kaputa AI Pro v2.0<br>Engineered by Adheesha Sooriyaarachchi</div>', unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "model", "content": "Kaputa AI Pro (1.5) online. Connectivity optimized. How can I assist?"})

    for message in st.session_state.messages:
        role = message["role"]
        # Professional Icons (No Cartoons)
        avatar = "⚡" if role == "model" else "👤"
        with st.chat_message("assistant" if role == "model" else "user", avatar=avatar):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter command or query..."):
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant", avatar="⚡"):
            with st.spinner("Processing..."):
                response_text = ""
                try:
                    if enable_search:
                        search_results = search_web(prompt)
                        final_prompt = f"Web Data:\n{search_results}\n\nQuery: {prompt}" if search_results else prompt
                        response = model.generate_content(final_prompt)
                    elif uploaded_pdf and pdf_text:
                        response = model.generate_content(f"Context:\n{pdf_text}\n\nQuery: {prompt}")
                    else:
                        response = model.generate_content(prompt)
                    
                    response_text = response.text
                    st.markdown(response_text)
                    
                    # Optional: TTS (Hidden unless needed for 'pro' feel, usually annoying in office tools)
                    # We keep it minimal or remove if 'Professional' means silent.
                    # Keeping it for feature parity but maybe cleaner.

                    st.session_state.messages.append({"role": "model", "content": response_text})
                except Exception as e:
                    st.error(f"Error: {e}")

# ------------------------------------------
# TAB 2: EXAM QUIZ MODE
# ------------------------------------------
with tab2:
    st.subheader("Assessment Generator")
    col1, col2 = st.columns([2, 1])
    with col1:
        quiz_context = st.text_area("Source Material", height=200, label_visibility="collapsed", placeholder="Paste lecture notes or text here...")
    with col2:
        num_questions = st.number_input("Question Count", min_value=1, max_value=20, value=5)
        if st.button("Generate Assessment", type="primary", use_container_width=True):
            if quiz_context:
                with st.spinner("Analyzing text & generating logic..."):
                    try:
                        quiz_prompt = f"""
                        Create {num_questions} professional multiple choice questions based on the text.
                        Output JSON only: [{{ "question": "...", "options": ["A", "B"], "answer": "A" }}]
                        """
                        response = model.generate_content(quiz_prompt)
                        clean_text = response.text.strip().replace("```json", "").replace("```", "")
                        st.session_state.quiz_data = json.loads(clean_text)
                    except:
                        st.error("Parsing Error")
    
    if "quiz_data" in st.session_state:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        for i, q in enumerate(st.session_state.quiz_data):
            st.markdown(f"**{i+1}. {q['question']}**")
            st.radio("Options", q['options'], key=f"q_{i}", label_visibility="collapsed")
            with st.expander("Reveal Answer"):
                st.info(f"Correct Answer: {q['answer']}")
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------
# TAB 3: VIDEO INTELLIGENCE (YouTube)
# ------------------------------------------
with tab3:
    st.subheader("Video Intelligence")
    col_u, col_b = st.columns([5, 1])
    with col_u:
        video_url = st.text_input("YouTube URL", placeholder="https://youtube.com/...", label_visibility="collapsed")
    with col_b:
        summ_btn = st.button("Analyze", type="primary", use_container_width=True)

    if summ_btn and video_url:
        vid = get_video_id(video_url)
        if vid:
            with st.spinner("Extracting transcript..."):
                try:
                    transcript = YouTubeTranscriptApi.get_transcript(vid)
                    text = " ".join([x['text'] for x in transcript])
                    response = model.generate_content(f"Summarize professionally:\n{text[:30000]}")
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.markdown("### Executive Summary")
                    st.markdown(response.text)
                    st.markdown('</div>', unsafe_allow_html=True)
                except:
                    st.error("Transcript unavailable")

# ------------------------------------------
# TAB 4: DEVELOPER STUDIO
# ------------------------------------------
with tab4:
    st.subheader("Code Studio")
    col_c, col_opt = st.columns([3, 1])
    with col_c:
        code = st.text_area("Code Input", height=300, label_visibility="collapsed")
    with col_opt:
        action = st.radio("Operation", ["Debug Analysis", "Code Explanation", "Performance Opt."], label_visibility="collapsed")
        if st.button("Execute", type="primary", use_container_width=True):
            if code:
                with st.spinner("Processing AST..."):
                    prompt = f"Perform {action} on:\n{code}"
                    res = model.generate_content(prompt)
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.markdown(res.text)
                    st.markdown('</div>', unsafe_allow_html=True)

