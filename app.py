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

genai.configure(api_key=api_key)

# 2. Page Config
st.set_page_config(
    page_title="Kaputa AI Pro",
    page_icon="⚡", # Cleaner icon
    layout="wide", # Wide layout for Dashboard feel
    initial_sidebar_state="expanded"
)

# --- PROFESSIONAL CSS SYSTEM ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
        
        :root {
            --primary: #4F46E5;
            --background: #0E1117;
            --surface: #1F2937;
            --text: #F3F4F6;
        }

        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
            color: var(--text);
        }

        /* Cleaner Sidebar */
        [data-testid="stSidebar"] {
            background-color: var(--background);
            border-right: 1px solid #374151;
        }

        /* Modern Title (No Gradients, Just Clean) */
        .main-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: -1px;
            margin-bottom: 5px;
        }
        
        .badge {
            background: #4F46E5;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
            vertical-align: middle;
            margin-left: 10px;
        }

        /* Card Style for Results */
        .result-card {
            background-color: #1F2937;
            border: 1px solid #374151;
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        /* Input Fields */
        .stTextInput input, .stTextArea textarea {
            background-color: #111827 !important;
            border: 1px solid #374151 !important;
            color: #fff !important;
            border-radius: 8px !important;
        }

        /* Buttons */
        .stButton button {
            background-color: #4F46E5 !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            font-weight: 500 !important;
            transition: all 0.2s;
        }
        .stButton button:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: transparent;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            border: 1px solid #374151;
            border-radius: 6px;
            color: #9CA3AF;
            padding: 8px 16px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #4F46E5 !important;
            color: white !important;
            border-color: #4F46E5 !important;
        }

        /* Footer */
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #0E1117;
            color: #6B7280;
            padding: 12px;
            font-size: 0.75rem;
            text-align: center;
            border-top: 1px solid #374151;
            z-index: 999;
        }
    </style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
col_logo, col_title = st.columns([1, 10])
with col_title:
    st.markdown('<div class="main-title">Kaputa AI <span class="badge">PRO</span></div>', unsafe_allow_html=True)
    st.caption("Advanced AI Workspace for Research, Coding & Education")

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
    model = genai.GenerativeModel('gemini-2.0-flash')
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

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "model", "content": "Kaputa AI Pro online. Connectivity established. How can I assist?"})

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

# Footer
st.markdown('<div class="footer">Kaputa AI Pro v2.0 | Engineered by Adheesha Sooriyaarachchi</div>', unsafe_allow_html=True)