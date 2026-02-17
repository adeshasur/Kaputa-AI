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

# 2. Page Config (Browser Tab එකේ නම සහ Icon එක)
st.set_page_config(
    page_title="Kaputa AI",
    page_icon="🐦",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- 3. CUSTOM CSS & STYLING (මේකෙන් තමයි ලස්සන කරන්නේ) ---
st.markdown("""
    <style>
        /* Google Font Import */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Kaputa Title Gradient Style */
        .title-text {
            font-size: 3rem;
            font-weight: 800;
            background: -webkit-linear-gradient(45deg, #FF4B4B, #FF914D);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 0px;
        }
        
        .subtitle-text {
            text-align: center;
            font-size: 1rem;
            color: #888;
            margin-bottom: 20px;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #f0f2f6;
        }
        
        /* Button Styling */
        .stButton button {
            border-radius: 10px;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# --- 4. HEADER SECTION ---
st.markdown('<p class="title-text">Kaputa AI 🐦</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Your Smart Assistant | Vision 👁️ | Voice 🗣️ | Web 🌍</p>', unsafe_allow_html=True)

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

# 6. SIDEBAR (Enhanced Icons)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80) # Logo එකක් වගේ
    st.title("Settings")
    
    st.markdown("### 🛠️ Features")
    
    # Web Search Toggle with distinct styling
    enable_search = st.toggle("🌍 Web Search Mode")
    if enable_search:
        st.info("Kaputa is now connected to the Internet! 🌐")
    
    st.markdown("---")
    
    # PDF Upload
    st.markdown("### 📚 Knowledge Base")
    uploaded_pdf = st.file_uploader("Drop your PDF Lecture Note", type="pdf")
    pdf_text = ""
    if uploaded_pdf:
        try:
            reader = PyPDF2.PdfReader(uploaded_pdf)
            for page in reader.pages:
                pdf_text += page.extract_text()
            st.success("PDF Analyzed Successfully! ✅")
        except:
            st.error("Error reading PDF ❌")

    st.markdown("---")
    
    # Download Chat
    st.markdown("### 💾 Export")
    st.download_button(
        label="� Download Chat as PDF",
        data=create_pdf(st.session_state.messages if "messages" in st.session_state else []),
        file_name="kaputa_chat.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# 7. Model Setup
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
except:
    st.error("System Error: Model not found.")

# 8. Chat History Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "model", "content": "ආයුබෝවන්! මම Kaputa. මම අලුත් පෙනුමකින් ආවා! 😎 මොනවද කරන්නේ?"})

# 9. Display Chat History (With Custom Avatars) 🧑💻🐦
for message in st.session_state.messages:
    role = message["role"]
    
    # Custom Avatars තෝරා ගැනීම
    if role == "model":
        avatar_icon = "🐦" # Kaputa Icon
        role_name = "assistant"
    else:
        avatar_icon = "🧑💻" # User Icon
        role_name = "user"

    with st.chat_message(role_name, avatar=avatar_icon):
        st.markdown(message["content"])

# 10. Main Input Logic
prompt = st.chat_input("Ask Kaputa anything...")

if prompt:
    # User Message
    with st.chat_message("user", avatar="🧑💻"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AI Response
    with st.chat_message("assistant", avatar="🐦"):
        with st.spinner("Thinking..."):
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

                # Kaputa Speaking (Output Voice Only)
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