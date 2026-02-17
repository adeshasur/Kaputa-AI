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
st.caption("Gemini 2.5 Flash | Vision 👁️ | Web Search 🌍 | PDF 📚")

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
        # Sinhala characters cleanup for PDF (basic)
        content = msg['content'].encode('latin-1', 'replace').decode('latin-1') 
        pdf.multi_cell(0, 10, txt=f"{role}: {content}")
        pdf.ln(5)
    return pdf.output(dest='S').encode('latin-1')

# 4. Sidebar Tools
with st.sidebar:
    # ➕ New Chat Button
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.header("🛠️ Tools")
    
    # Web Search Toggle
    enable_search = st.toggle("🌍 Enable Web Search")
    
    # PDF Upload
    st.subheader("📚 Study Buddy")
    uploaded_pdf = st.file_uploader("Upload PDF Note", type="pdf")
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
    
    # Download Chat
    st.download_button(
        label="💾 Download Chat (PDF)",
        data=create_pdf(st.session_state.messages if "messages" in st.session_state else []),
        file_name="kaputa_chat.pdf",
        mime="application/pdf"
    )

# 5. Model Setup
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
except:
    st.error("Model Error")

# 6. Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "model", "content": "ආයුබෝවන්! මම Kaputa. මම දැන් හරිම වේගවත්. මොනවද දැනගන්න ඕන?"})

for message in st.session_state.messages:
    role = "assistant" if message["role"] == "model" else "user"
    with st.chat_message(role):
        st.markdown(message["content"])

# 7. Main Logic (Text Only)
prompt = st.chat_input("මොනවද දැනගන්න ඕන?...")

if prompt:
    # User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AI Response
    with st.chat_message("assistant"):
        with st.spinner("Kaputa is thinking..."):
            response_text = ""
            try:
                # A. Web Search Logic
                if enable_search:
                    search_results = search_web(prompt)
                    if search_results:
                        final_prompt = f"Web Search Results:\n{search_results}\n\nUser Query: {prompt}\n\nAnswer based on results."
                        response = model.generate_content(final_prompt)
                    else:
                        response = model.generate_content(prompt)
                    response_text = response.text

                # B. PDF Logic
                elif uploaded_pdf and pdf_text:
                    response = model.generate_content(f"Context from PDF:\n{pdf_text}\n\nUser Question: {prompt}")
                    response_text = response.text
                
                # C. Normal Chat
                else:
                    response = model.generate_content(prompt)
                    response_text = response.text

                st.markdown(response_text)

                # Kaputa Speaking (Output Voice Only) - මේක තිබුණට UI එක කැත වෙන්නේ නෑ
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