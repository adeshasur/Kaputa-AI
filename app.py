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

# --- 3. ADVANCED CUSTOM CSS ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
        html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
        
        .main-title {
            font-size: 3.5rem;
            font-weight: 700;
            background: linear-gradient(120deg, #FF4B4B, #FF914D, #FFC700);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 10px;
            text-shadow: 0px 4px 15px rgba(255, 75, 75, 0.3);
            animation: fadeIn 2s ease-in-out;
        }
        
        .sub-title {
            text-align: center;
            font-size: 1.1rem;
            color: #b0b0b0;
            margin-bottom: 30px;
        }

        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #0E1117;
            color: #666;
            text-align: center;
            font-size: 0.8rem;
            padding: 10px;
            border-top: 1px solid #262730;
            z-index: 1000;
        }

        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(-20px); }
            100% { opacity: 1; transform: translateY(0); }
        }
    </style>
""", unsafe_allow_html=True)

# --- 4. HEADER ---
st.markdown('<div class="main-title">Kaputa AI 🐦</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title"><b>Smart Assistant</b> | Vision 👁️ | Voice 🗣️ | Web 🌍 | Knowledge 📚</div>', unsafe_allow_html=True)

# 5. Helper Functions
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

# 6. SIDEBAR & STATE
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/6134/6134346.png", width=80) 
    st.title("Kaputa Control")
    
    # MODE SELECTION 🔄
    mode = st.radio("Select Mode:", ["💬 Chat Assistant", "📝 Quiz Generator", "📺 Video Summarizer", "💻 Developer Mode"], index=0)
    
    st.markdown("---")

    with st.expander("🛠️ Core Tools", expanded=True):
        if mode == "💬 Chat Assistant":
            enable_search = st.toggle("🌍 Web Search", help="Connects Kaputa to the internet")
        
        uploaded_pdf = st.file_uploader("📂 Upload PDF", type="pdf")
        pdf_text = ""
        if uploaded_pdf:
            try:
                reader = PyPDF2.PdfReader(uploaded_pdf)
                for page in reader.pages:
                    pdf_text += page.extract_text()
                st.success("PDF Analyzed! 🧠", icon="✅")
            except:
                st.error("File Error", icon="❌")

# 7. Model
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
except:
    st.error("System Error 500: Model Unreachable")

# --- MAIN LOGIC BASED ON MODE ---

if mode == "💬 Chat Assistant":
    # 8. Chat Logic
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "model", "content": "👋 හායි! මම Kaputa. ඔයාගේ ඕනෑම වැඩකට මම ලෑස්තියි. අහන්න..."})

    # Display Messages
    for message in st.session_state.messages:
        role = message["role"]
        avatar = "🐦" if role == "model" else "👤"
        with st.chat_message("assistant" if role == "model" else "user", avatar=avatar):
            st.markdown(message["content"])

    # Input & Processing
    prompt = st.chat_input("Message Kaputa AI...")

    if prompt:
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant", avatar="🐦"):
            message_placeholder = st.empty()
            with st.spinner("Analyzing..."):
                response_text = ""
                try:
                    if enable_search:
                        search_results = search_web(prompt)
                        if search_results:
                            final_prompt = f"Web Results:\n{search_results}\n\nUser: {prompt}\n\nAnswer:"
                            response = model.generate_content(final_prompt)
                        else:
                            response = model.generate_content(prompt)
                        response_text = response.text

                    elif uploaded_pdf and pdf_text:
                        response = model.generate_content(f"PDF Context:\n{pdf_text}\n\nUser: {prompt}")
                        response_text = response.text
                    
                    else:
                        response = model.generate_content(prompt)
                        response_text = response.text

                    message_placeholder.markdown(response_text)

                    # TTS
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

elif mode == "📝 Quiz Generator":
    # 9. Quiz Logic
    st.header("📝 Auto Quiz Generator")
    st.caption("Upload a PDF and I will generate 5 MCQ questions for you.")

    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = None

    if uploaded_pdf and pdf_text:
        if st.button("🚀 Generate Quiz from PDF", type="primary"):
            with st.spinner("Generating Questions..."):
                try:
                    prompt = f"""
                    You are a teacher. Create 5 multiple choice questions based on the following text.
                    Return the result strictly as a valid JSON list of objects.
                    Each object must have:
                    "question": The question text.
                    "options": A list of 4 options.
                    "answer": The correct option text (must match one of the options exactly).
                    
                    Text: {pdf_text[:10000]}
                    """
                    response = model.generate_content(prompt)
                    cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
                    st.session_state.quiz_data = json.loads(cleaned_text)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating quiz: {e}")

    if st.session_state.quiz_data:
        score = 0
        with st.form("quiz_form"):
            for i, q in enumerate(st.session_state.quiz_data):
                st.markdown(f"**Q{i+1}: {q['question']}**")
                choice = st.radio(f"Select answer for Q{i+1}", q['options'], key=f"q_{i}")
                if choice == q['answer']:
                    score += 1
            submitted = st.form_submit_button("Submit Answers")
            if submitted:
                st.success(f"You scored: {score} / 5")
                for i, q in enumerate(st.session_state.quiz_data):
                    with st.expander(f"View Answer for Q{i+1}"):
                        st.write(f"Correct Answer: **{q['answer']}**")
                if score == 5:
                    st.balloons()
    elif not uploaded_pdf:
        st.info("👈 Please upload a PDF in the sidebar to start!")

elif mode == "📺 Video Summarizer":
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
                        You are a helpful assistant. Summarize the following YouTube video transcript in detail.
                        Highlight key points and takeaways.
                        
                        Transcript: {full_text[:30000]}
                        """
                        response = model.generate_content(prompt)
                        st.subheader("📝 Summary")
                        st.markdown(response.text)
                        
                    except Exception as e:
                        st.error(f"Could not retrieve transcript. The video might not have captions enabled. Error: {e}")
        else:
            st.error("Invalid YouTube URL")

elif mode == "💻 Developer Mode":
    st.header("💻 Developer Code Assistant")
    st.caption("Paste your code below to debug, explain, or optimize it.")

    code_input = st.text_area("Paste Code Here", height=200)
    
    c1, c2, c3 = st.columns(3)
    
    if code_input:
        with c1:
            if st.button("🐛 Debug Code", type="primary", use_container_width=True):
                with st.spinner("Debugging..."):
                    prompt = f"Identify and fix bugs in this code:\n\n{code_input}"
                    response = model.generate_content(prompt)
                    st.subheader("🐛 Debug Report")
                    st.markdown(response.text)
        
        with c2:
            if st.button("📝 Explain Code", use_container_width=True):
                with st.spinner("Analyzing..."):
                    prompt = f"Explain this code step-by-step:\n\n{code_input}"
                    response = model.generate_content(prompt)
                    st.subheader("📝 Code Explanation")
                    st.markdown(response.text)
        
        with c3:
            if st.button("✨ Optimize Code", use_container_width=True):
                with st.spinner("Optimizing..."):
                    prompt = f"Optimize this code for performance and readability:\n\n{code_input}"
                    response = model.generate_content(prompt)
                    st.subheader("✨ Optimization Suggestions")
                    st.markdown(response.text)

# Footer
st.markdown('<div class="footer">🚀 Powered by Gemini 2.5 | 🧠 Built with ❤️ by Adheesha Sooriyaarachchi</div>', unsafe_allow_html=True)