import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import subprocess
# Set page config
st.set_page_config(
    page_title="YouTube Video Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Dark mode background */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    .stButton > button {
        background-color: #BF40BF;
        color: white;
        border-radius: 20px;
        padding: 10px 20px;
    }
    
    /* Darker containers with better contrast */
    .video-container, .summary-container {
        background-color: #1E2126;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #2E3440;
        color: #E0E0E0;
    }
    
    /* Style headers */
    h1, h2, h3, h4 {
        color: #FFFFFF !important;
    }
    
    /* Style text input fields */
    .stTextInput input {
        background-color: #262730;
        color: #FFFFFF;
        border: 1px solid #4B4B4B;
    }
    
    /* Style markdown text */
    .stMarkdown {
        color: #E0E0E0;
    }
</style>
""", unsafe_allow_html=True)

# Header section with URL input
st.title("📺 YouTube Video Analyzer")
col1, col2 = st.columns([4, 1])
with col1:
    video_url = st.text_input("", placeholder="Paste YouTube Video URL here")
with col2:
    st.button("🎬 Add Video", type="primary")

# Analyzed Videos section
st.subheader("📊 Analyzed Videos")

# Create three columns for Videos, Summaries, and AI Responses
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📹 Videos")
    with st.container():
        st.markdown("""
        <div class="video-container">
            <h4>iPhone 15 Review: Welcome to the Club!</h4>
            <!-- Add video thumbnail here -->
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("### 📝 Summaries")
    with st.container():
        st.markdown("""
        <div class="summary-container">
            <h4>iPhone 15 Review: Welcome to the Club!</h4>
            <ul>
                <li>Familiar design</li>
                <li>Softer corners, satin back</li>
                <li>Pale light colors</li>
                <li>Dynamic island on non-Pro</li>
                <li>Brighter screen (2,000 knits)</li>
                <li>60Hz display</li>
                <li>A16 Bionic chip</li>
                <li>USB-C charging</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

with col3:
    st.markdown("### 🤖 AI Responses")
    with st.container():
        st.markdown("""
        <div class="summary-container">
            <h4>AI Response</h4>
            <p>The YouTuber gives a detailed review of the new iPhone 15, discussing its design, display, performance, battery life, camera, and software features. They note that while the phone doesn't offer any major new innovations, it does feature a number of subtle improvements that make it a worthwhile upgrade over older models.</p>
        </div>
        """, unsafe_allow_html=True)

# Bottom chat section
st.markdown("---")
chat_col1, chat_col2 = st.columns([5, 1])
with chat_col1:
    user_question = st.text_input("", placeholder="Ask anything about the video...")
with chat_col2:
    st.button("💬 Ask", type="primary") 
    st.button("Talk to the AI 🤖", type="primary") 



with chat_col2:
    if st.button("💬 Ask", type="primary"):
        if user_question:
            
        else:
            st.warning("Please enter a question first!")
    if st.button("Talk to the AI 🤖", type="primary") :
        print("Calling to talk to the AI")
        curl_command = ["curl",
            "-X", "POST", "https://workflows.platform.happyrobot.ai/hooks/l3oos32d6szw",
            "-H", "Content-Type: application/json",
            "-d", '{"user_name": "Sanil", "context": "Slightly Longer Review: The AuraGlow Sleep Mask is a reliable option for minimizing light disruption during sleep. Its contoured design, particularly around the nose bridge, effectively reduces ambient light, even in brighter environments. The adjustable strap ensures a comfortable and secure fit, accommodating various head sizes without slippage. The mask is made from a soft modal blend, which breathes well and prevents overheating—a common complaint with some sleep masks. The stitching appears durable, and after several weeks of use, there are no signs of wear. While it\'t offer noise cancellation, its light-blocking and comfort make it a worthwhile choice for improving sleep quality."}'
        ]
        subprocess.run(curl_command)