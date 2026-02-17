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
        
        /* Quiz Styling */
        .quiz-card {
            background-color: #262730;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border: 1px solid #444;
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

# 6. SIDEBAR & STATE
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/6134/6134346.png", width=80) 
    st.title("Kaputa Control")
    
    # MODE SELECTION 🔄
    mode = st.radio("Select Mode:", ["💬 Chat Assistant", "📝 Quiz Generator"], index=0)
    
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

    st.markdown("---")
    
    if mode == "💬 Chat Assistant":
        with st.expander("💾 Export Options"):
            st.download_button(
                label="📄 Save Conversation",
                data=create_pdf(st.session_state.messages if "messages" in st.session_state else []),
                file_name="kaputa_chat.pdf",
                mime="application/pdf",
                use_container_width=True
            )

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

    # Display Quiz
    if st.session_state.quiz_data:
        score = 0
        with st.form("quiz_form"):
            for i, q in enumerate(st.session_state.quiz_data):
                st.markdown(f"**Q{i+1}: {q['question']}**")
                choice = st.radio(f"Select answer for Q{i+1}", q['options'], key=f"q_{i}")
                
                # Check directly here for simple scoring logic display later
                if choice == q['answer']:
                    score += 1

            submitted = st.form_submit_button("Submit Answers")
            
            if submitted:
                st.success(f"You scored: {score} / 5")
                # Show correct answers
                for i, q in enumerate(st.session_state.quiz_data):
                    with st.expander(f"View Answer for Q{i+1}"):
                        st.write(f"Correct Answer: **{q['answer']}**")
                
                if score == 5:
                    st.balloons()

    elif not uploaded_pdf:
        st.info("👈 Please upload a PDF in the sidebar to start!")

# Footer
st.markdown('<div class="footer">🚀 Powered by Gemini 2.5 | 🧠 Built with ❤️ by Adheesha Sooriyaarachchi</div>', unsafe_allow_html=True)