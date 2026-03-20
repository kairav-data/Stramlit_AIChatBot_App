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

# Custom CSS for aesthetics (glassmorphism, clean fonts)
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container styling */
    .stApp {
        background-color: #fafafa;
        color: #1a1a1a;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
    }
    
    /* User message */
    [data-testid="stChatMessage"]:has([data-testid="stIconMaterial"]:contains('person')) {
        background-color: #18181b !important;
        color: white !important;
        border-radius: 20px 20px 0 20px;
        margin-left: max(50px, 20%);
        padding: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
    }
    
    /* Bot message */
    [data-testid="stChatMessage"]:has([data-testid="stIconMaterial"]:contains('smart_toy')) {
        background-color: white !important;
        color: #1a1a1a !important;
        border: 1px solid #e4e4e7 !important;
        border-radius: 20px 20px 20px 0;
        margin-right: max(50px, 20%);
        padding: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Input area styling */
    .stChatInputContainer {
        border-radius: 12px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1) !important;
        border: 1px solid #e4e4e7 !important;
        background-color: white !important;
    }
</style>
""", unsafe_allow_html=True)

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

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

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
