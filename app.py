import os
import streamlit as st
from openai import AuthenticationError, RateLimitError

from chatbot import YouTubeChatbot
from youtube_utils import extract_video_id, TranscriptsDisabled, NoTranscriptFound

# Page configuration 
st.set_page_config(
    page_title="YouTube Video Q&A Chatbot",
    page_icon="🤖",
    layout="centered"
)

# CSS 
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #FF0000;
    }
    .subheader {
        font-size: 1.3rem;
        color: #666666;
        margin-bottom: 2rem;
    }
    .stButton button {
        width: 100%;
        background-color: #FF0000;
        color: white;
        font-weight: 600;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    .stButton button:hover {
        background-color: #CC0000;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .response-container {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
        background-color: #f8f9fa;
        border-left: 4px solid #FF0000;
    }
    .footer {
        text-align: center;
        color: #888888;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #eeeeee;
    }
    .url-input {
        border-radius: 5px;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        color: #333333;
    }
</style>
""", unsafe_allow_html=True)

# Main title and description
st.markdown('<p class="main-header">🤖 YouTube Video Q&A Chatbot</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">✨ Ask questions about any YouTube video using AI</p>', unsafe_allow_html=True)

#  API key input and About section
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    api_key = st.text_input(
        "OpenAI API Key", 
        type="password",
        placeholder="sk-...",
        help="Your OpenAI API key is required to use the chatbot"
    )
    
    # Load API key from .env if not provided
    if not api_key:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key:
            st.success("API key loaded from .env file")
    
    st.markdown("---")
    st.markdown("### 📖 About")
    st.markdown(
        "This app uses LangChain and OpenAI to process YouTube video transcripts "
        "and answer questions about the content."
    )
    
    st.markdown("### 🔍 How It Works")
    st.markdown("""
    1. Enter a YouTube URL
    2. Click 'Process Video' to extract the transcript
    3. Ask questions about the video content
    4. Get AI-powered answers based on the video
    """)

# Main content area 
st.markdown("<p class='section-header'>📹 Enter YouTube Video</p>", unsafe_allow_html=True)

# two columns for URL input and Process button
col1, col2 = st.columns([3, 1])

with col1:
    video_url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Enter a YouTube video URL or ID",
        key="url_input"
    )

# Initialize session state for storing the chatbot instance
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
    
if 'video_processed' not in st.session_state:
    st.session_state.video_processed = False
    
if 'current_video_id' not in st.session_state:
    st.session_state.current_video_id = None

# Process video button in the second column
with col2:
    st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
    process_button = st.button("🚀 Process")

# Process video logic
if process_button:
    # Validate inputs
    if not video_url:
        st.warning("⚠️ Please enter a YouTube video URL")
    elif not api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar")
    else:
        # Set the API key in environment
        os.environ["OPENAI_API_KEY"] = api_key
        
        # Show processing message with spinner
        with st.spinner("🔄 Processing video transcript... This may take a moment."):
            try:
                # Extract video ID
                video_id = extract_video_id(video_url)
                
                # Check if we need to reprocess the video
                if (st.session_state.chatbot is None or 
                    st.session_state.current_video_id != video_id):
                    
                    # Initialize chatbot
                    st.session_state.chatbot = YouTubeChatbot()
                    
                    # Process the video
                    success = st.session_state.chatbot.process_video(video_url)
                    
                    if success:
                        st.session_state.video_processed = True
                        st.session_state.current_video_id = video_id
                        st.success("✅ Video processed successfully! You can now ask questions.")
                    else:
                        st.error("❌ Failed to process video. Please check the URL and try again.")
                else:
                    st.info("ℹ️ Video already processed. You can ask questions below.")
                    
            except AuthenticationError:
                st.error("🔑 Invalid OpenAI API key. Please check your API key and try again.")
            except RateLimitError:
                st.error("⏱️ OpenAI API rate limit exceeded. Please try again later.")
            except TranscriptsDisabled:
                st.error("📝 This video does not have captions available. Please try a different video.")
            except NoTranscriptFound:
                st.error("🌐 No transcript found in the supported languages. Please try a different video.")
            except ValueError as e:
                st.error(f"⚠️ Invalid input: {str(e)}")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")

# Question input and answer section (only show if video is processed)
if st.session_state.video_processed and st.session_state.chatbot is not None:
    st.markdown("---")
    st.markdown("<p class='section-header'>🤔 Ask a Question</p>", unsafe_allow_html=True)
    
    question = st.text_area(
        "Your question about the video",
        placeholder="What is the main topic of this video?",
        height=100
    )
    
    # Create columns for better button layout
    _, col_btn, _ = st.columns([1, 2, 1])
    
    with col_btn:
        answer_button = st.button("🔍 Get Answer")
    
    if answer_button:
        if not question:
            st.warning("⚠️ Please enter a question")
        else:
            with st.spinner("🧠 Thinking..."):
                try:
                    # Get answer from chatbot
                    answer = st.session_state.chatbot.ask(question)
                    
                    # Display answer 
                    st.markdown("<p class='section-header'>💬 Answer</p>", unsafe_allow_html=True)
                    st.markdown(f"<div class='response-container'>{answer}</div>", unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")

#  if no video is processed yet
if not st.session_state.video_processed:
    st.info("👆 Enter a YouTube URL above and click 'Process' to get started!")

#  footer
st.markdown("---")
st.markdown(
    "<div class='footer'>"
    "Developed by Piyush | Powered by LangChain & OpenAI"
    "</div>",
    unsafe_allow_html=True
)
