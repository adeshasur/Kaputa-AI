import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
from gtts import gTTS
import tempfile
from duckduckgo_search import DDGS
import PyPDF2
from fpdf import FPDF
from youtube_transcript_api import YouTubeTranscriptApi
from PIL import Image

# 1. Configuration
load_dotenv()
api_key = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")

# Fix 404
genai.configure(api_key=api_key, transport='rest')

# 2. Page Setup (Clean & Pro - Like Screenshot)
st.set_page_config(page_title="Kaputa AI Pro", page_icon="🐦", layout="wide", initial_sidebar_state="expanded")

# --- PRO CSS (Updated to match request) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --bg-main: #0E1117;
        --bg-card: #1E1E1E;
        --accent: #3A86FF;
        --text: #E0E0E0;
    }

    /* GLOBAL */
    html, body, .stApp {
        font-family: 'Inter', sans-serif;
        color: var(--text) !important;
        background-color: var(--bg-main) !important;
    }

    /* HEADERS */
    h1, h2, h3 {
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #0E1117;
        border-right: 1px solid #333;
    }
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1E1E1E;
        padding: 6px;
        border-radius: 12px;
        display: inline-flex;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border: none;
        color: #888;
        font-size: 0.9rem;
        padding: 6px 20px;
        border-radius: 8px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #333 !important;
        color: white !important;
        font-weight: 600;
    }

    /* "PRO" Title Style */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
        background: linear-gradient(90deg, #fff, #888);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .badge {
        font-size: 0.8rem;
        vertical-align: top;
        background: #3A86FF;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        margin-left: 5px;
        -webkit-text-fill-color: white; /* Reset gradient */
    }

    /* CARDS */
    .result-card {
        background-color: var(--bg-card);
        border: 1px solid #333;
        border-radius: 16px;
        padding: 20px;
        margin-top: 15px;
    }

    /* INPUTS */
    .stTextInput input, .stTextArea textarea {
        background-color: #1E1E1E !important;
        border: 1px solid #333 !important;
        color: white !important;
        border-radius: 12px !important;
    }
    .stTextInput input:focus {
        border-color: var(--accent) !important;
    }

    /* BUTTONS */
    .stButton button {
        border-radius: 12px !important;
        font-weight: 500 !important;
    }
    
    /* ANIMATED CHAT BUBBLES */
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .stChatMessage {
        animation: slideIn 0.3s ease-out forwards;
        border-radius: 20px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    /* User Message (Blue Gradient) */
    [data-testid="stChatMessage"][data-author="human"] {
        background: linear-gradient(135deg, rgba(58, 134, 255, 0.2), rgba(58, 134, 255, 0.1));
        backdrop-filter: blur(10px);
        border-left: none;
        margin-left: 20%;
        border-bottom-right-radius: 5px;
    }
    
    /* AI Message (Glass Grey) */
    [data-testid="stChatMessage"][data-author="ai"] {
        background: rgba(30, 30, 30, 0.6);
        backdrop-filter: blur(10px);
        margin-right: 20%;
        border-bottom-left-radius: 5px;
    }
    
    /* Hide Avatars for cleaner bubble look (Optional, but user asked for iMessage style) */
    [data-testid="chatAvatarIcon"] {
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
    }
    
    /* SMOOTH PAGE TRANSITIONS */
    .stApp {
        animation: fadeIn 0.6s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 3. Model
try:
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception as e:
    st.error(f"System Error: {e}")

# 4. SIDEBAR LOGIC
with st.sidebar:
    # Logo Area
    # Logo Area (Text Only - Enhanced)
    st.markdown("""
        <div style='text-align: center; padding: 10px 0 20px 0;'>
            <div style='font-size: 3rem; margin-bottom: 5px;'>🦅</div>
            <h1 style='font-size: 1.8rem; font-weight: 800; margin: 0; background: linear-gradient(90deg, #fff, #aaa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Kaputa AI</h1>
            <div style='font-size: 0.7rem; font-weight: 600; color: #3A86FF; letter-spacing: 2px; margin-top: 5px;'>PRO EDITION</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    
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

    st.markdown("---")
    
    # Session Export
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

    if st.button("Download Session", use_container_width=True):
        if "messages" in st.session_state:
            st.download_button(
                label="Confirm Download",
                data=create_pdf(st.session_state.messages),
                file_name="session_log.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    st.markdown("<div style='margin-top: 50px; text-align: center; font-size: 10px; color: #555;'>Kaputa AI Pro v2.0<br>Engineered by Adheesha Sooriyaarachchi</div>", unsafe_allow_html=True)


# 5. MAIN CONTENT
st.markdown('<div class="main-title">Kaputa AI <span class="badge">PRO</span></div>', unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #888; margin-bottom: 30px;'>Advanced AI Workspace</div>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Chat", "Quiz", "Research", "Dev"])

# --- TAB 1: CHAT ---
with tab1:
    # Feature 2: Split View (Side-by-Side)
    if pdf_text:
        col_view, col_chat = st.columns([1, 1.2]) # View 45%, Chat 55%
        with col_view:
            st.markdown("### 📄 Document Context")
            st.markdown(f"""
                <div style='
                    height: 70vh; 
                    overflow-y: auto; 
                    background: rgba(255, 255, 255, 0.05); 
                    padding: 20px; 
                    border-radius: 15px; 
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    font-size: 0.9rem;
                    line-height: 1.6;
                '>{pdf_text}</div>
            """, unsafe_allow_html=True)
        target_container = col_chat
    else:
        target_container = st.container()

    with target_container:
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "model", "content": "Kaputa AI Pro (1.5) online. Connectivity optimized. How can I assist?"}]

        # Chat History
        chat_box = st.container()
        with chat_box:
             for msg in st.session_state.messages:
                role = "assistant" if msg["role"] == "model" else "user"
                avatar = "🐦" if role == "assistant" else None
                with st.chat_message(role, avatar=avatar):
                    st.markdown(msg["content"])

        # Feature 3: Quick Action Cards
        if pdf_text:
            st.write("") # Spacer
            q_col1, q_col2, q_col3 = st.columns(3)
            action_prompt = None
            
            if q_col1.button("📝 Summarize", use_container_width=True):
                action_prompt = "Summarize the document document in detail."
            if q_col2.button("❓ Generate Quiz", use_container_width=True):
                action_prompt = "Generate 5 MCQ questions based on this document."
            if q_col3.button("🐞 Debug/Audit", use_container_width=True):
                action_prompt = "Analyze the document for logic errors or inconsistencies."
            
            if action_prompt:
                st.session_state.messages.append({"role": "user", "content": action_prompt})
                with st.chat_message("user"):
                    st.markdown(action_prompt)
                
                # Trigger generation immediately
                with st.chat_message("assistant", avatar="🐦"):
                    with st.spinner("Analyzing..."):
                        response = model.generate_content(f"Context:\n{pdf_text}\n\nTask: {action_prompt}")
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "model", "content": response.text})
                st.rerun()

        # Chat Input
        if prompt := st.chat_input("Enter command or query..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant", avatar="🐦"):
                with st.spinner("Processing..."):
                    try:
                        full_response = ""
                        # Context Logic
                        if enable_search:
                             try:
                                 results = DDGS().text(prompt, max_results=2)
                                 web_context = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
                                 final_prompt = f"Web Context (Search):\n{web_context}\n\nQuery: {prompt}" if results else prompt
                             except:
                                 final_prompt = prompt
                        elif pdf_text:
                            final_prompt = f"Context (PDF):\n{pdf_text}\n\nQuery: {prompt}"
                        else:
                            final_prompt = prompt
                        
                        # Feature 4: Syntax Highlighting instruction
                        final_prompt += "\n\n(IMPORTANT: Use Code Blocks with language tags for all code)"

                        response = model.generate_content(final_prompt, stream=True)
                        placeholder = st.empty()
                        for chunk in response:
                            full_response += chunk.text
                            placeholder.markdown(full_response + "▌")
                        placeholder.markdown(full_response)
                        st.session_state.messages.append({"role": "model", "content": full_response})
                    except Exception as e:
                        st.error(f"Error: {e}")

# --- TAB 2: QUIZ ---
with tab2:
    st.subheader("Quiz Generator")
    input_text = st.text_area("Paste Content", height=150)
    if st.button("Generate Quiz", type="primary"):
        if input_text:
            with st.spinner("Generating..."):
                try:
                    prompt = f"Generate 3 multiple choice questions based on:\n{input_text}"
                    res = model.generate_content(prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"Error: {e}")

# --- TAB 3: VIDEO (Updated) ---
with tab3:
    st.subheader("Video Intelligence")
    video_url = st.text_input("YouTube URL")
    if st.button("Analyze Video"):
        if video_url:
            with st.spinner("Fetching transcript..."):
                try:
                    video_id = ""
                    if "v=" in video_url: video_id = video_url.split("v=")[1].split("&")[0]
                    elif "youtu.be" in video_url: video_id = video_url.split("/")[-1]
                    
                    if video_id:
                        transcript = YouTubeTranscriptApi.get_transcript(video_id)
                        text = " ".join([x['text'] for x in transcript])
                        res = model.generate_content(f"Summarize:\n{text[:20000]}")
                        st.markdown(res.text)
                    else:
                        st.error("Invalid URL")
                except Exception as e:
                    st.error(f"Transcript Error: {e}")

# --- TAB 4: DEV ---
with tab4:
    st.subheader("Developer Tools")
    code_in = st.text_area("Code Snippet", height=200)
    dev_action = st.radio("Action", ["Explain Code", "Debug", "Convert to Python"])
    if st.button("Execute Dev Task"):
        if code_in:
            with st.spinner("Analyzing..."):
                res = model.generate_content(f"{dev_action} for:\n{code_in}")
                st.markdown(res.text)
