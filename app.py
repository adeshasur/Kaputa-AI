import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import PyPDF2
from gtts import gTTS
import tempfile

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

# 2. Page Config & Title
st.set_page_config(page_title="Kaputa AI", page_icon="🐦", layout="centered")
st.title("Kaputa AI 🐦")
st.caption("Powered by Gemini 2.5 Flash | Vision 👁️ | PDF 📚 | Voice �️")

# 3. Sidebar (Settings & Uploads)
with st.sidebar:
    st.header("⚙️ Settings")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.session_state.pdf_context = ""
        st.rerun()
    
    st.markdown("---")
    st.header("Uploads 📂")
    
    # Image Uploader
    uploaded_image = st.file_uploader("Upload an Image (Vision)", type=["jpg", "jpeg", "png"])
    
    # PDF Uploader
    uploaded_pdf = st.file_uploader("Upload a PDF (Lecture Note)", type=["pdf"])

    st.markdown("---")
    st.markdown("**Developer:** Adheesha Sooriyaarachchi")

# 4. Model Setup
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Model Error: {e}")

# 5. Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "model", "content": "ආයුබෝවන්! මම Kaputa. මට පින්තූර බලන්න, PDF කියවන්න සහ කතා කරන්න පුළුවන්. කැමති දෙයක් අහන්න!"})

if "pdf_context" not in st.session_state:
    st.session_state.pdf_context = ""

# 6. Process PDF Logic
if uploaded_pdf is not None:
    try:
        # Check if we already processed this PDF to avoid reprocessing on every rerun
        # Simple check: if pdf_context is empty, process it. 
        # (In a real app, we might check file name, but this is simple)
        if st.session_state.pdf_context == "":
            with st.spinner("PDF එක කියවමින්... 📖"):
                pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                st.session_state.pdf_context = text
            st.success("PDF එක කියවා අවසන්! දැන් ඒකෙන් ප්‍රශ්න අහන්න.")
    except Exception as e:
        st.error(f"PDF Error: {e}")

# 7. Display Messages
for message in st.session_state.messages:
    role = "assistant" if message["role"] == "model" else "user"
    with st.chat_message(role):
        st.markdown(message["content"])

# 8. Handling User Input
if prompt := st.chat_input("අහන්න ඕන දෙයක් කියන්න..."):
    # User Message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare Context (PDF Content + Prompt)
    final_prompt = prompt
    if st.session_state.pdf_context:
        final_prompt = f"Background Information (Context from uploaded PDF):\n{st.session_state.pdf_context}\n\nUser Question:\n{prompt}"

    # AI Response
    try:
        with st.chat_message("assistant"):
            with st.spinner("කල්පනා කරමින්... 🤔"):
                response_text = ""
                
                # Image Handling
                if uploaded_image is not None:
                    image = Image.open(uploaded_image)
                    st.image(image, caption="Uploaded Image", use_column_width=True)
                    response = model.generate_content([final_prompt, image])
                    response_text = response.text
                else:
                    # Text / PDF Chat
                    # Note: We send 'final_prompt' which includes PDF context if available.
                    # But for chat history to work, we usually use start_chat.
                    # Sticking PDF context into every message might confuse the history or exceed limits eventually, 
                    # but for 1.5 Flash (1M tokens) it's usually fine for a few turns.
                    # Ideally, we add it to system instruction or just once. 
                    # Here, to keep it simple and robust, we'll use generate_content for single turn with context 
                    # OR start_chat. 
                    # Let's use start_chat but we need to fit the prompt logic.
                    
                    # Simplest approach for RAG with Chat History:
                    # Append the context to the history physically? No, that messes up the UI.
                    # We will send the context invisibly to the model in the current turn.
                    
                    # Construct usage history for the API (excluding current turn which we send now)
                    history_for_api = [
                        {"role": "user", "parts": [m["content"]]} if m["role"] == "user"
                        else {"role": "model", "parts": [m["content"]]}
                        for m in st.session_state.messages[:-1]
                    ]
                    
                    chat = model.start_chat(history=history_for_api)
                    response = chat.send_message(final_prompt)
                    response_text = response.text

                st.markdown(response_text)
                
                # 9. Voice Output (TTS)
                audio_file_path = "response_audio.mp3"
                tts = gTTS(text=response_text, lang='si') # 'si' for Sinhala (or 'en' if English detected, but 'si' often works for mixed)
                # Note: gTTS 'si' might fallback or have specific accents. 
                # If the response is English, 'en' is better. 
                # Let's stick to 'en' as default or 'si' if user prefers? 
                # Kaputa implies Sinhala context. 'si' is safe for mixed usually.
                tts.save(audio_file_path)
                st.audio(audio_file_path)
                os.remove(audio_file_path) # Clean up
        
        # Save Response (Original User Prompt is saved in UI history, but Model sees Enhanced Prompt)
        # We save the PLAIN response to history
        st.session_state.messages.append({"role": "model", "content": response_text})

    except Exception as e:
        st.error(f"Error: {e}")