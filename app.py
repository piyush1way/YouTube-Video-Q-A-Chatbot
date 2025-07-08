import os
import streamlit as st
from openai import AuthenticationError, RateLimitError

from chatbot import YouTubeChatbot
from youtube_utils import extract_video_id, TranscriptsDisabled, NoTranscriptFound

st.set_page_config(
    page_title="YouTube Chatbot",
    page_icon="🎬",
    layout="centered"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .subheader {
        font-size: 1.2rem;
        color: #888888;
        margin-bottom: 2rem;
    }
    .stButton button {
        width: 100%;
        background-color: #FF0000;
        color: white;
    }
    .response-container {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Main title and description
st.markdown('<p class="main-header">YouTube Chatbot</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Ask questions about any YouTube video using AI</p>', unsafe_allow_html=True)

# Create sidebar for API key input
with st.sidebar:
    st.markdown("### Configuration")
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
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown(
        "This app uses LangChain and OpenAI to process YouTube video transcripts "
        "and answer questions about the content."
    )

# Main content area
st.markdown("### 📹 Enter YouTube Video")
video_url = st.text_input(
    "YouTube URL",
    placeholder="https://www.youtube.com/watch?v=...",
    help="Enter a YouTube video URL or ID"
)

# Initialize session state for storing the chatbot instance
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
    
if 'video_processed' not in st.session_state:
    st.session_state.video_processed = False
    
if 'current_video_id' not in st.session_state:
    st.session_state.current_video_id = None

# Process video button
if st.button("Process Video"):
    # Validate inputs
    if not video_url:
        st.error("Please enter a YouTube video URL")
    elif not api_key:
        st.error("Please enter your OpenAI API key")
    else:
        # Set the API key in environment
        os.environ["OPENAI_API_KEY"] = api_key
        
        # Show processing message
        with st.spinner("Processing video transcript..."):
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
                        st.success("Video processed successfully! You can now ask questions.")
                    else:
                        st.error("Failed to process video. Please check the URL and try again.")
                else:
                    st.info("Video already processed. You can ask questions below.")
                    
            except AuthenticationError:
                st.error("Invalid OpenAI API key. Please check your API key and try again.")
            except RateLimitError:
                st.error("OpenAI API rate limit exceeded. Please try again later.")
            except TranscriptsDisabled:
                st.error("This video does not have captions available. Please try a different video.")
            except NoTranscriptFound:
                st.error("No transcript found in the supported languages. Please try a different video.")
            except ValueError as e:
                st.error(f"Invalid input: {str(e)}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Question input and answer section (only show if video is processed)
if st.session_state.video_processed and st.session_state.chatbot is not None:
    st.markdown("---")
    st.markdown("### 🤔 Ask a Question")
    
    question = st.text_area(
        "Your question about the video",
        placeholder="What is the main topic of this video?",
        height=100
    )
    
    if st.button("Get Answer"):
        if not question:
            st.warning("Please enter a question")
        else:
            with st.spinner("Thinking..."):
                try:
                    # Get answer from chatbot
                    answer = st.session_state.chatbot.ask(question)
                    
                    # Display answer
                    st.markdown("### 💬 Answer")
                    st.markdown(f"<div class='response-container'>{answer}</div>", unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# Instructions if no video is processed yet
if not st.session_state.video_processed:
    st.info("👆 Enter a YouTube URL above and click 'Process Video' to get started!")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888888;'>"
    "Powered by LangChain and OpenAI"
    "</div>",
    unsafe_allow_html=True
)
