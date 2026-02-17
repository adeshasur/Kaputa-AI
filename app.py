import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="Kaputa Doctor", page_icon="🩺")
st.title("Kaputa Doctor 🩺")

# 1. API Key Check
api_key = os.getenv("GEMINI_API_KEY")
if not api_key and "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

if not api_key:
    st.error("API Key එක සොයාගත නොහැක! .env හෝ Secrets පරීක්ෂා කරන්න.")
    st.stop()

# 2. Configure & Check Version
try:
    genai.configure(api_key=api_key)
    st.success(f"✅ Library Version: {genai.__version__}")
    
    st.write("### Available Models (ඔයාට පාවිච්චි කරන්න පුළුවන් මොළ):")
    
    # 3. List all models
    count = 0
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            st.code(m.name) # මොඩල් එකේ නම පෙන්වන්න
            count += 1
            
    if count == 0:
        st.warning("කිසිම මොඩල් එකක් සොයාගත නොහැක. API Key එකේ ප්රශ්නයක් විය හැක.")
        
except Exception as e:
    st.error(f"Critical Error: {e}")
    st.write("Try updating requirements.txt to: google-generativeai>=0.8.3")