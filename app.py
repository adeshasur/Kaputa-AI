import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import PyPDF2
from gtts import gTTS
import tempfile
from duckduckgo_search import DDGS
from fpdf import FPDF
from streamlit_mic_recorder import mic_recorder

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
st.set_page_config(page_title="Kaputa AI", page_icon="🐦", layout="centered")
st.title("Kaputa AI 🐦")
st.caption("Gemini 2.5 Flash | Voice & Vision Enabled")

# 3. Helper Functions
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

# 4. Sidebar (Updated with New Chat Button)
with st.sidebar:
    # ➕ NEW CHAT BUTTON (උඩින්ම දානවා)
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    
    st.header("🛠️ Toolkit")
    enable_search = st.toggle("🌍 Web Search")
    
    st.subheader("📚 Study Buddy")
    uploaded_pdf = st.file_uploader("Upload PDF", type="pdf")
    pdf_text = ""
    if uploaded_pdf:
        try:
            reader = PyPDF2.PdfReader(uploaded_pdf)
            for page in reader.pages:
                pdf_text += page.extract_text()
            st.success("PDF Loaded! ✅")
        except:
            st.error("PDF Error")

    st.markdown("---")
    st.download_button(
        label="💾 Download Chat",
        data=create_pdf(st.session_state.messages if "messages" in st.session_state else []),
        file_name="kaputa_chat.pdf",
        mime="application/pdf"
    )

# 5. Model Setup
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
except:
    st.error("Model Error")

# 6. Chat History Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "model", "content": "ආයුබෝවන්! මම Kaputa. අලුත් දෙයක් පටන් ගමුද?"})

# Display Chat History
for message in st.session_state.messages:
    role = "assistant" if message["role"] == "model" else "user"
    with st.chat_message(role):
        st.markdown(message["content"])

# --- VOICE INPUT SECTION ---
st.write("---") 
c1, c2 = st.columns([1, 5])
with c1:
    audio = mic_recorder(
        start_prompt="🎙️ Record",
        stop_prompt="🛑 Stop",
        just_once=False,
        key='recorder'
    )
with c2:
    st.caption("Click Record to speak.")

# Audio Processing
audio_prompt = None
if audio:
    audio_prompt = audio['bytes']

# 7. Main Input Logic
prompt = st.chat_input("Type something here...")

if prompt or audio_prompt:
    user_content = prompt if prompt else "🎤 [Voice Message]"
    
    with st.chat_message("user"):
        st.markdown(user_content)
    st.session_state.messages.append({"role": "user", "content": user_content})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_text = ""
            try:
                # A. Voice Logic
                if audio_prompt:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                        temp_audio.write(audio_prompt)
                        temp_audio_path = temp_audio.name
                    
                    audio_file = genai.upload_file(temp_audio_path)
                    response = model.generate_content(["Reply to this audio (Sinhala/English):", audio_file])
                    response_text = response.text

                # B. Web Search Logic
                elif enable_search and prompt:
                    search_results = search_web(prompt)
                    if search_results:
                        final_prompt = f"Web Results:\n{search_results}\n\nQuery: {prompt}"
                        response = model.generate_content(final_prompt)
                    else:
                        response = model.generate_content(prompt)
                    response_text = response.text

                # C. PDF Logic
                elif uploaded_pdf and pdf_text and prompt:
                    response = model.generate_content(f"PDF Context:\n{pdf_text}\n\nQuery: {prompt}")
                    response_text = response.text
                
                # D. Normal Chat
                else:
                    response = model.generate_content(prompt)
                    response_text = response.text

                st.markdown(response_text)

                # Voice Output
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