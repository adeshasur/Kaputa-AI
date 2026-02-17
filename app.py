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
import io

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
st.set_page_config(page_title="Kaputa AI", page_icon="🐦", layout="wide")
st.title("Kaputa AI 🐦 (Ultimate Version)")
st.caption("Gemini 2.5 Flash | Vision 👁️ | Voice 🗣️ | Web Search 🌍 | PDF Export �")

# 3. Helper Function: Web Search
def search_web(query):
    try:
        results = DDGS().text(query, max_results=3)
        return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
    except Exception as e:
        return None

# 4. Helper Function: Export Chat to PDF
def create_pdf(messages):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Kaputa AI - Chat History", ln=True, align='C')
    pdf.ln(10)

    for msg in messages:
        role = "User" if msg['role'] == "user" else "Kaputa"
        # Note: FPDF doesn't support Sinhala perfectly, so we sanitize text
        content = msg['content'].encode('latin-1', 'replace').decode('latin-1') 
        pdf.multi_cell(0, 10, txt=f"{role}: {content}")
        pdf.ln(5)
    
    return pdf.output(dest='S').encode('latin-1')

# 5. Sidebar (Settings & Tools)
with st.sidebar:
    st.header("⚙️ Settings & Tools")
    
    # Toggle Web Search
    enable_search = st.toggle("🌍 Enable Web Search (අන්තර්ජාලය)")
    
    # PDF Upload
    st.subheader("📚 Study Buddy")
    uploaded_pdf = st.file_uploader("Upload Lecture Note (PDF)", type="pdf")
    
    pdf_text = ""
    if uploaded_pdf:
        try:
            reader = PyPDF2.PdfReader(uploaded_pdf)
            for page in reader.pages:
                pdf_text += page.extract_text()
            st.success("PDF Loaded! ✅")
        except:
            st.error("PDF Error")

    # Export Chat Button
    st.markdown("---")
    # Check if messages exist before calling create_pdf
    msgs = st.session_state.messages if "messages" in st.session_state else []
    if msgs:
         pdf_data = create_pdf(msgs)
         st.download_button(
             label="� Download Chat (PDF)",
             data=pdf_data,
             file_name="kaputa_chat.pdf",
             mime="application/pdf"
         )

    # Clear Chat
    if st.button("🗑️ Clear History"):
        st.session_state.messages = []
        st.rerun()

# 6. Model Setup
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
except:
    st.error("Model Error")

# 7. Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "model", "content": "ආයුබෝවන්! මම Kaputa. දැන් මට අන්තර්ජාලයෙන් හොයන්නත්, ඔයා කියන දේ අහන්නත් පුළුවන්."})

# Display Messages
for message in st.session_state.messages:
    role = "assistant" if message["role"] == "model" else "user"
    with st.chat_message(role):
        st.markdown(message["content"])

# 8. VOICE INPUT (Microphone) 🎤
st.markdown("---")
col1, col2 = st.columns([1, 4])
with col1:
    st.write("🎤 **Voice Input:**")
    audio = mic_recorder(start_prompt="⏺️ Record", stop_prompt="⏹️ Stop", key='recorder')

audio_prompt = None
if audio:
    # Voice Input එක කෙලින්ම Gemini ට යවමු (Audio Understanding)
    st.audio(audio['bytes'])
    audio_prompt = audio['bytes']

# 9. Main Logic
prompt = st.chat_input("Type something...")

if prompt or audio_prompt:
    # User Input එක හදාගැනීම
    user_content = prompt if prompt else "🎤 [Audio Message Sent]"
    
    with st.chat_message("user"):
        st.markdown(user_content)
    st.session_state.messages.append({"role": "user", "content": user_content})

    with st.chat_message("assistant"):
        with st.spinner("Kaputa is thinking... 🤔"):
            response_text = ""
            
            try:
                # A. Voice Input නම් (Audio Processing)
                if audio_prompt:
                    # Audio එක File එකක් විදියට Save කරගන්නවා
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                        temp_audio.write(audio_prompt)
                        temp_audio_path = temp_audio.name
                    
                    # Gemini ට Audio File එක යවනවා
                    audio_file = genai.upload_file(temp_audio_path)
                    
                    # Wait for file processing if needed, but for small audio usually fast. 
                    # Ideally we loop check state, but start simple.
                    
                    response = model.generate_content(["Please listen to this audio and reply in Sinhala or English:", audio_file])
                    response_text = response.text
                
                # B. Web Search On නම් 🌍
                elif enable_search and prompt:
                    search_results = search_web(prompt)
                    if search_results:
                        st.info(f"🔎 Searching Web: Found info about '{prompt}'")
                        final_prompt = f"Context from Web Search:\n{search_results}\n\nUser Question: {prompt}\n\nAnswer based on the context."
                        response = model.generate_content(final_prompt)
                    else:
                        response = model.generate_content(prompt)
                    response_text = response.text

                # C. PDF Context 📚
                elif uploaded_pdf and pdf_text and prompt:
                    final_prompt = f"PDF Context:\n{pdf_text}\n\nQuestion: {prompt}"
                    response = model.generate_content(final_prompt)
                    response_text = response.text

                # D. Normal Chat / Image
                else:
                    response = model.generate_content(prompt)
                    response_text = response.text

                st.markdown(response_text)

                # Voice Output (Text-to-Speech) 🗣️
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