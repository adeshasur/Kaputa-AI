import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
from duckduckgo_search import DDGS

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
st.caption("Gemini 2.5 Flash | Context Aware Chat 🧠")

# 3. Helper Functions
def search_web(query):
    try:
        results = DDGS().text(query, max_results=3)
        return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
    except:
        return None

# --- SESSION STATE SETUP (History & Memory) ---

# Chat History එක තියාගන්න තැන (List of Chats)
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {
        "Chat 1": [] # මුලින්ම Chat 1 කියලා එකක් හදනවා
    }

# දැනට Active වෙලා තියෙන Chat එකේ නම
if "active_chat" not in st.session_state:
    st.session_state.active_chat = "Chat 1"

# Chat ගණන (නම් හදන්න)
if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 1

# 4. SIDEBAR (History Panel)
with st.sidebar:
    # A. New Chat Button (උඩින්ම)
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        st.session_state.chat_counter += 1
        new_chat_name = f"Chat {st.session_state.chat_counter}"
        st.session_state.chat_sessions[new_chat_name] = [] # අලුත් ලිස්ට් එකක්
        st.session_state.active_chat = new_chat_name # අලුත් එකට මාරු වෙනවා
        st.rerun()
    
    st.markdown("---")
    st.subheader("� History")
    
    # B. Chat History List (පරණ Chats ටික පෙන්වීම)
    # අපි Reverse කරනවා අලුත් ඒව උඩින් පෙන්නන්න
    chat_names = list(st.session_state.chat_sessions.keys())[::-1]
    
    selected_chat = st.radio(
        "Go to chat:",
        chat_names,
        index=chat_names.index(st.session_state.active_chat) if st.session_state.active_chat in chat_names else 0,
        label_visibility="collapsed",
        key="history_radio"
    )
    
    # Radio Button එකෙන් Chat එක මාරු වුනොත්
    if selected_chat != st.session_state.active_chat:
        st.session_state.active_chat = selected_chat
        st.rerun()

    st.markdown("---")
    
    # C. Tools
    enable_search = st.toggle("🌍 Web Search")
    
    # Clear Current Chat
    if st.button("�️ Clear This Chat"):
        st.session_state.chat_sessions[st.session_state.active_chat] = []
        st.rerun()

# 5. Model Setup
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
except:
    st.error("Model Error")

# 6. MAIN CHAT INTERFACE
st.subheader(f"💬 {st.session_state.active_chat}")

# Active Chat එකේ මැසේජ් ටික ගන්න
current_messages = st.session_state.chat_sessions[st.session_state.active_chat]

# මැසේජ් ටික පෙන්නන්න
for message in current_messages:
    role = "assistant" if message["role"] == "model" else "user"
    with st.chat_message(role):
        st.markdown(message["content"])

# 7. INPUT & LOGIC
prompt = st.chat_input("අහන්න...")

if prompt:
    # 1. User Message Save & Display
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_sessions[st.session_state.active_chat].append({"role": "user", "content": prompt})

    # 2. AI Response Generation
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # --- CONTEXT AWARENESS LOGIC ---
                # මෙතනදී අපි 'current_messages' (පරණ කතාව) ඔක්කොම මොඩල් එකට යවනවා.
                # එතකොට Kaputa දන්නවා අපි කලින් කතා කරේ මොනවද කියලා.
                
                history_for_gemini = [
                    {"role": "user", "parts": [m["content"]]} if m["role"] == "user"
                    else {"role": "model", "parts": [m["content"]]}
                    for m in st.session_state.chat_sessions[st.session_state.active_chat]
                ]
                
                # Chat Object එක හදනවා (History එක්ක)
                chat = model.start_chat(history=history_for_gemini)
                
                # Search Logic
                if enable_search:
                    search_results = search_web(prompt)
                    if search_results:
                        final_prompt = f"Web Info:\n{search_results}\n\nUser Question: {prompt}"
                        response = chat.send_message(final_prompt)
                    else:
                        response = chat.send_message(prompt)
                else:
                    response = chat.send_message(prompt)
                
                st.markdown(response.text)
                
                # 3. AI Reply Save
                st.session_state.chat_sessions[st.session_state.active_chat].append({"role": "model", "content": response.text})

            except Exception as e:
                st.error(f"Error: {e}")