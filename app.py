import streamlit as st
import requests
import os
import json

# Configure page
st.set_page_config(
    page_title="My AI Assistant",
    page_icon="✨",
    layout="centered"
)

# Custom CSS for aesthetics (glassmorphism, clean fonts, minimal design)
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Main container styling */
    .stApp {
        background-color: #fcfcfd;
        color: #121212;
    }
    
    /* Minimalist Sidebar Layout */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #f1f1f3;
        padding-top: 2rem;
    }
    
    /* Ensure chat messages do not get hidden behind inputs */
    .main .block-container {
        padding-bottom: 120px !important;
    }
    
    /* Upload Button Styling */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        background-color: #0f172a;
        color: white;
        font-weight: 500;
        border: none;
        padding: 0.6rem 0;
        transition: all 0.2s ease-in-out;
        margin-top: 0.5rem;
    }
    .stButton > button:hover {
        background-color: #334155;
        color: white;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
    }
    
    /* Chat Message Styling */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
        padding: 0.5rem 0 !important;
    }
    
    /* User message bubble */
    [data-testid="stChatMessage"]:has([data-testid="stIconMaterial"]:contains('person')) {
        background-color: #0f172a !important;
        color: white !important;
        border-radius: 24px 24px 4px 24px;
        margin-left: max(40px, 30%);
        padding: 1.2rem;
        box-shadow: 0 4px 15px -3px rgba(15, 23, 42, 0.1);
        font-weight: 400;
    }
    
    /* Bot message buble */
    [data-testid="stChatMessage"]:has([data-testid="stIconMaterial"]:contains('smart_toy')) {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 24px 24px 24px 4px;
        margin-right: max(40px, 15%);
        padding: 1.2rem;
        box-shadow: 0 4px 15px -3px rgba(0, 0, 0, 0.03);
        line-height: 1.6;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Input area styling - Glassmorphism */
    .stChatInputContainer {
        border-radius: 20px !important;
        border: 1px solid rgba(226, 232, 240, 0.8) !important;
        background-color: rgba(255, 255, 255, 0.75) !important;
        backdrop-filter: blur(16px) !important;
        box-shadow: 0 -10px 40px -10px rgba(0, 0, 0, 0.05) !important;
        padding: 0.5rem 1rem !important;
        margin-bottom: 1rem;
        bottom: 0px !important; /* Keep native bottom placement */
        z-index: 1000 !important;
    }
    
    /* Title sleekness */
    h1 {
        font-weight: 700 !important;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #0f172a, #334155);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# (Sidebar removed for inline chat behavior)

# Title and header
st.title("✨ Lumina AI")
st.markdown("<p style='color: #71717a; font-size: 1.1rem; margin-top: -10px;'>The next generation of customer support.</p>", unsafe_allow_html=True)

# Backend URL
BACKEND_URL = "http://localhost:8000/api/chat"

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your AI assistant. How can I help you today?"}
    ]

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Unified Chat Input with Attachment
prompt_obj = st.chat_input("Ask anything", accept_file="multiple", file_type=["pdf"])

if prompt_obj:
    # Handle the returned ChatInputValue
    text = ""
    files_list = []
    
    if hasattr(prompt_obj, "text"):
        text = prompt_obj.text
        files_list = prompt_obj.files if hasattr(prompt_obj, "files") else []
    elif isinstance(prompt_obj, dict):
        text = prompt_obj.get("text", "")
        files_list = prompt_obj.get("files", [])
    elif isinstance(prompt_obj, str):
        text = prompt_obj
        
    # Process uploaded files if any
    if files_list:
        for uploaded_file in files_list:
            if st.session_state.get("last_uploaded_file") != uploaded_file.name:
                with st.spinner(f"Processing attached document: {uploaded_file.name}..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    try:
                        response = requests.post("http://localhost:8000/api/upload", files=files)
                        if response.status_code == 200:
                            st.session_state.last_uploaded_file = uploaded_file.name
                            st.session_state.messages.append({"role": "assistant", "content": f"📎 I've read the document **{uploaded_file.name}**. Ask me anything about it!"})
                            st.rerun() # Refresh to show system message
                        else:
                            st.error(f"Error: {response.text}")
                    except Exception as e:
                        st.error(f"Connection error: {e}")
                        
    # Process text input if any
    if text:
        # Append user message
        st.session_state.messages.append({"role": "user", "content": text})
        with st.chat_message("user"):
            st.markdown(text)

    # Prepare payload for FastAPI backend
    # The backend expects [{"role": "user" | "bot", "content": "..."}] 
    api_messages = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "bot"
        api_messages.append({"role": role, "content": msg["content"]})
    
    payload = {
        "messages": api_messages,
        "model": "Qwen/Qwen2.5-72B-Instruct"
    }

    # Fetch response from backend
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Lumina is thinking..."):
            try:
                # We use a timeout of 30 seconds
                response = requests.post(BACKEND_URL, json=payload, timeout=30)
                if response.status_code == 200:
                    assistant_response = response.json().get("response", "No response returned.")
                    message_placeholder.markdown(assistant_response)
                    # Add to history
                    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                else:
                    error_msg = f"Error: `{response.status_code}` - {response.text}"
                    message_placeholder.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except requests.exceptions.RequestException as e:
                error_msg = f"Failed to connect to backend: `{e}`. Ensure the FastAPI backend is running on `localhost:8000`."
                message_placeholder.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
