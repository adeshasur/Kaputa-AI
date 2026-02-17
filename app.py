import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
from gtts import gTTS
import tempfile
from duckduckgo_search import DDGS
from fpdf import FPDF
import PyPDF2

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

# --- 3. ADVANCED CUSTOM CSS (Dark Mode Optimized �) ---
st.markdown("""
    <style>
        /* Import Google Font */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
        
        /* Apply Font */
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }

        /* Gradient Title */
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
            color: #b0b0b0; /* Light Grey for Dark Mode */
            margin-bottom: 30px;
        }

        /* Sidebar Styling - WE REMOVED THE FORCED WHITE BACKGROUND */
        /* Let Streamlit Config handle the dark background */

        /* Footer */
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #0E1117; /* Match Dark Bg */
            color: #666;
            text-align: center;
            font-size: 0.8rem;
            padding: 10px;
            border-top: 1px solid #262730;
            z-index: 1000;
        }

        /* Animations */
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

# 6. SIDEBAR
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/6134/6134346.png", width=80) 
    st.title("Kaputa Control")
    
    with st.expander("🛠️ Core Tools", expanded=True):
        enable_search = st.toggle("🌍 Web Search", help="Connects Kaputa to the internet")
        
        uploaded_pdf = st.file_uploader("📂 Upload PDF", type="pdf")
        pdf_text = ""
        if uploaded_pdf:
            try:
                reader = PyPDF2.PdfReader(uploaded_pdf)
                for page in reader.pages:
                    pdf_text += page.extract_text()
                st.success("Analysis Complete! 🧠", icon="✅")
            except:
                st.error("File Error", icon="❌")

    st.markdown("---")
    
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

# 8. Chat Logic
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "model", "content": "👋 හායි! මම Kaputa. ඔයාගේ ඕනෑම වැඩකට මම ලෑස්තියි. අහන්න..."})

# Display Messages
# Streamlit now handles avatars cleanly, no custom CSS needed for bubbles
for message in st.session_state.messages:
    role = message["role"]
    if role == "model":
        with st.chat_message("assistant", avatar="🐦"):
            st.markdown(message["content"])
    else:
        with st.chat_message("user", avatar="👤"):
            st.markdown(message["content"])

# 9. Input & Processing
prompt = st.chat_input("Message Kaputa AI...")

if prompt:
    # User
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AI
    with st.chat_message("assistant", avatar="🐦"):
        message_placeholder = st.empty()
        with st.spinner("Analyzing..."):
            response_text = ""
            try:
                # Logic
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

# Footer
st.markdown('<div class="footer">🚀 Powered by Gemini 2.5 | 🧠 Built with ❤️ by Adheesha Sooriyaarachchi</div>', unsafe_allow_html=True)