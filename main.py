# -*- coding: utf-8 -*-
"""\
Main entry point for the YouTube Chatbot application.

This module provides a simple command-line interface to interact with
the YouTube chatbot.\n"""

from chatbot import YouTubeChatbot


def main():
    """
    Main function to run the YouTube chatbot application.
    """
    print("YouTube Chatbot")
    print("==============\n")
    
    chatbot = YouTubeChatbot()
    
    # Get video URL or ID from user
    video_url = input("Enter YouTube video URL or ID: ")
    
    print("\nProcessing video transcript...")
    success = chatbot.process_video(video_url)
    
    if not success:
        print("Failed to process video. Please check the URL and try again.")
        return
    
    print("Video processed successfully!\n")
    
    # Interactive question answering loop
    while True:
        question = input("\nAsk a question about the video (or type 'exit' to quit): ")
        
        if question.lower() in ['exit', 'quit', 'q']:
            break
            
        print("\nThinking...")
        answer = chatbot.ask(question)
        print(f"\nAnswer: {answer}")


if __name__ == "__main__":
    main()