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

# 2. Page Config
st.set_page_config(page_title="Kaputa AI", page_icon="🐦", layout="centered")
st.title("Kaputa AI 🐦")
st.caption("Gemini 2.5 Flash | Vision 👁️ | Voice 🗣️ | PDF 📚")

# 3. Sidebar (Settings & PDF Upload)
with st.sidebar:
    st.header("⚙️ Settings")
    
    # PDF Upload
    st.subheader("� Study Buddy (PDF)")
    uploaded_pdf = st.file_uploader("Upload PDF Lecture Note", type="pdf")
    
    pdf_text = ""
    if uploaded_pdf is not None:
        try:
            reader = PyPDF2.PdfReader(uploaded_pdf)
            for page in reader.pages:
                pdf_text += page.extract_text()
            st.success("PDF එක කියෙව්වා! දැන් ඒකෙන් ප්රශ්න අහන්න. ✅")
        except Exception as e:
            st.error(f"PDF Error: {e}")

    st.markdown("---")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# 4. Model Setup
model = genai.GenerativeModel('gemini-1.5-flash')

# 5. Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "model", "content": "ආයුබෝවන්! මම Kaputa. මට පින්තූර බලන්න, PDF කියවන්න වගේම කතා කරන්නත් පුළුවන්. මොනවද කරන්න ඕන?"})

# Display Messages
for message in st.session_state.messages:
    role = "assistant" if message["role"] == "model" else "user"
    with st.chat_message(role):
        st.markdown(message["content"])

# 6. Image Uploader (Chat එක ඇතුලේ)
uploaded_image = st.file_uploader("Upload an Image...", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
if uploaded_image:
    st.image(uploaded_image, caption="Uploaded Image", width=200)

# 7. User Input Handling
if prompt := st.chat_input("අහන්න ඕන දෙයක් කියන්න..."):
    # User Message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        with st.chat_message("assistant"):
            with st.spinner("කල්පනා කරමින්... 🤔"):
                response_text = ""
                
                # Scenario 1: PDF එකක් ගැන අහනවා නම්
                if uploaded_pdf and pdf_text:
                    prompt_with_context = f"Based on this PDF content: \n\n{pdf_text}\n\nUser Question: {prompt}"
                    response = model.generate_content(prompt_with_context)
                    response_text = response.text
                
                # Scenario 2: Image එකක් ගැන අහනවා නම්
                elif uploaded_image:
                    image = Image.open(uploaded_image)
                    response = model.generate_content([prompt, image])
                    response_text = response.text
                
                # Scenario 3: නිකන් Chat කරනවා නම්
                else:
                    chat = model.start_chat(history=[
                        {"role": "user", "parts": [m["content"]]} if m["role"] == "user"
                        else {"role": "model", "parts": [m["content"]]}
                        for m in st.session_state.messages if "parts" not in m
                    ])
                    response = chat.send_message(prompt)
                    response_text = response.text

                # ප්රතිචාරය පෙන්වීම
                st.markdown(response_text)
                
                # Voice Output (උත්තරය කියවීම) 🗣️
                try:
                    tts = gTTS(text=response_text, lang='si' if any(c in response_text for c in 'අආඇ') else 'en')
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                        tts.save(fp.name)
                        st.audio(fp.name, format="audio/mp3")
                except:
                    pass # Voice වැඩ කළේ නැත්නම් අවුලක් නෑ, Text එක විතරක් පෙන්නන්න.

        # Save to History
        st.session_state.messages.append({"role": "model", "content": response_text})

    except Exception as e:
        st.error(f"Error: {e}")