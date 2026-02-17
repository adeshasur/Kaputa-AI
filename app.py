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
    st.error("API Key එක සොයාගත නොහැක!")
    st.stop()

genai.configure(api_key=api_key)

# 2. Page Config
st.set_page_config(
    page_title="Kaputa AI",
    page_icon="🐦",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- CSS STYLING ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .title-text {
            font-size: 3rem; font-weight: 800;
            background: -webkit-linear-gradient(45deg, #FF4B4B, #FF914D);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            text-align: center; margin-bottom: 0px;
        }
        .subtitle-text { text-align: center; font-size: 1rem; color: #888; margin-bottom: 20px; }
        .stButton button { border-radius: 10px; font-weight: 600; }
        
        /* Footer Fixed */
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #0E1117;
            color: #FAFAFA;
            text-align: center;
            font-size: 0.8rem;
            padding: 10px;
            border-top: 1px solid #262730;
            z-index: 1000;
        }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<p class="title-text">Kaputa AI 🐦</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Smart Assistant | Vision 👁️ | Voice 🗣️ | Web 🌍 | Quiz 📝</p>', unsafe_allow_html=True)

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
    pdf.cell(200, 10, txt="Kaputa AI - Chat History", ln=True, align='C')
    pdf.ln(10)
    for msg in messages:
        role = "User" if msg['role'] == "user" else "Kaputa"
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

# --- MODEL ---
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
except:
    st.error("System Error: Model not found.")

# ==========================================
# 🚀 MAIN TABS (Chat | Quiz | YouTube | Dev)
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📝 Quiz", "📺 YouTube", "💻 Dev"])

# ------------------------------------------
# TAB 1: CHAT ASSISTANT
# ------------------------------------------
with tab1:
    # Sidebar for Chat
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
        st.title("Kaputa Control")
        
        st.markdown("### 🛠️ Chat Tools")
        enable_search = st.toggle("🌍 Enable Web Search")
        
        st.markdown("---")
        st.markdown("### 📚 Study Buddy")
        uploaded_pdf = st.file_uploader("Upload PDF Note", type="pdf", key="chat_pdf")
        pdf_text = ""
        if uploaded_pdf:
            try:
                reader = PyPDF2.PdfReader(uploaded_pdf)
                for page in reader.pages:
                    pdf_text += page.extract_text()
                st.success("PDF Ready! ✅")
            except:
                st.error("Error reading PDF")

        st.markdown("---")
        st.download_button(
            label="💾 Export Chat (PDF)",
            data=create_pdf(st.session_state.messages if "messages" in st.session_state else []),
            file_name="kaputa_chat.pdf",
            mime="application/pdf"
        )

    # Chat Logic
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "model", "content": "හායි! මම Kaputa. ඔයාගේ ඕනම වැඩකට මම ලෑස්තියි. අහන්න..."})

    for message in st.session_state.messages:
        role = message["role"]
        avatar_icon = "🐦" if role == "model" else "🧑💻"
        role_name = "assistant" if role == "model" else "user"
        with st.chat_message(role_name, avatar=avatar_icon):
            st.markdown(message["content"])

    if prompt := st.chat_input("Message Kaputa AI..."):
        with st.chat_message("user", avatar="🧑💻"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant", avatar="🐦"):
            with st.spinner("Thinking..."):
                response_text = ""
                try:
                    if enable_search:
                        search_results = search_web(prompt)
                        final_prompt = f"Web Results:\n{search_results}\n\nQuery: {prompt}" if search_results else prompt
                        response = model.generate_content(final_prompt)
                    elif uploaded_pdf and pdf_text:
                        response = model.generate_content(f"PDF Context:\n{pdf_text}\n\nUser Question: {prompt}")
                    else:
                        response = model.generate_content(prompt)
                    
                    response_text = response.text
                    st.markdown(response_text)

                    # Voice
                    try:
                        tts = gTTS(text=response_text, lang='si' if any(c in response_text for c in 'අආඇ') else 'en')
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                            tts.save(fp.name)
                            st.audio(fp.name, format="audio/mp3")
                    except:
                        pass
                    
                    st.session_state.messages.append({"role": "model", "content": response_text})
                except Exception as e:
                    st.error(f"Error: {e}")

# ------------------------------------------
# TAB 2: QUIZ GENERATOR 📝
# ------------------------------------------
with tab2:
    st.header("📝 Auto Quiz Generator")
    st.caption("Paste your notes below, and Kaputa will create a quiz for you!")
    
    quiz_context = st.text_area("Paste Text or Notes here:", height=200, placeholder="Enter content...")
    num_questions = st.slider("Number of Questions:", 1, 10, 5)
    
    if st.button("🚀 Generate Quiz", type="primary"):
        if quiz_context:
            with st.spinner("Generating Quiz Questions..."):
                try:
                    quiz_prompt = f"""
                    Create {num_questions} multiple choice questions (MCQ) based on this text:
                    "{quiz_context}"
                    Output ONLY a valid JSON array like this:
                    [{{ "question": "Q1", "options": ["A", "B", "C", "D"], "answer": "Correct Option" }}]
                    """
                    response = model.generate_content(quiz_prompt)
                    clean_text = response.text.strip()
                    if clean_text.startswith("```json"): clean_text = clean_text[7:-3]
                    st.session_state.quiz_data = json.loads(clean_text)
                    st.success("Quiz Generated!")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter text!")

    if "quiz_data" in st.session_state:
        st.markdown("---")
        for i, q in enumerate(st.session_state.quiz_data):
            st.subheader(f"{i+1}. {q['question']}")
            user_answer = st.radio(f"Select answer:", q['options'], key=f"q_{i}")
            if st.checkbox(f"Check Answer {i+1}", key=f"ans_{i}"):
                if user_answer == q['answer']: st.success("Correct! ✅")
                else: st.error(f"Wrong! Answer: {q['answer']}")

# ------------------------------------------
# TAB 3: YOUTUBE SUMMARIZER 📺
# ------------------------------------------
with tab3:
    st.header("📺 YouTube Video Summarizer")
    st.caption("Paste a YouTube link to get a quick summary.")

    video_url = st.text_input("YouTube Video URL")
    
    if video_url:
        video_id = get_video_id(video_url)
        if video_id:
            st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", width=300)
            
            if st.button("🎬 Summarize Video", type="primary"):
                with st.spinner("Watching video..."):
                    try:
                        transcript = YouTubeTranscriptApi.get_transcript(video_id)
                        full_text = " ".join([entry['text'] for entry in transcript])
                        
                        prompt = f"""
                        Summarize this YouTube video transcript. Highlight key points.
                        Transcript: {full_text[:30000]}
                        """
                        response = model.generate_content(prompt)
                        st.subheader("📝 Summary")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.error("Invalid YouTube URL")

# ------------------------------------------
# TAB 4: DEVELOPER MODE 💻
# ------------------------------------------
with tab4:
    st.header("💻 Developer Code Assistant")
    st.caption("Debug, Explain, or Optimize your code.")

    code_input = st.text_area("Paste Code Here", height=200)
    
    col1, col2, col3 = st.columns(3)
    
    if code_input:
        with col1:
            if st.button("🐛 Debug", use_container_width=True):
                with st.spinner("Debugging..."):
                    response = model.generate_content(f"Fix bugs in:\n{code_input}")
                    st.subheader("🐛 Report")
                    st.markdown(response.text)
        with col2:
            if st.button("📝 Explain", use_container_width=True):
                with st.spinner("Explaining..."):
                    response = model.generate_content(f"Explain code:\n{code_input}")
                    st.subheader("📝 Explanation")
                    st.markdown(response.text)
        with col3:
            if st.button("✨ Optimize", use_container_width=True):
                with st.spinner("Optimizing..."):
                    response = model.generate_content(f"Optimize code:\n{code_input}")
                    st.subheader("✨ Suggestions")
                    st.markdown(response.text)

# Footer
st.markdown('<div class="footer">🚀 Powered by Gemini 2.5 | 🧠 Built with ❤️ by Adheesha Sooriyaarachchi</div>', unsafe_allow_html=True)