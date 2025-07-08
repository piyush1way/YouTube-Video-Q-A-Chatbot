# -*- coding: utf-8 -*-
"""
YouTube utilities module for the chatbot.

This module provides functions for extracting transcripts and metadata
from YouTube videos.
"""

import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from typing import List, Dict, Optional, Union


def validate_youtube_url(url: str) -> bool:
    """
    Validate if the provided string is a valid YouTube URL or video ID.
    
    Args:
        url: A string containing a YouTube URL or video ID
        
    Returns:
        True if the URL or ID appears to be valid, False otherwise
    """
    # Check if it's a valid YouTube URL
    youtube_regex = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})'
    
    # Check if it's just a video ID (11 characters)
    video_id_regex = r'^[a-zA-Z0-9_-]{11}$'
    
    return bool(re.match(youtube_regex, url) or re.match(video_id_regex, url))


def extract_video_id(url: str) -> str:
    """
    Extract the video ID from a YouTube URL.
    
    Args:
        url: A YouTube video URL or ID
        
    Returns:
        The extracted video ID
        
    Raises:
        ValueError: If the URL is not a valid YouTube URL or ID
    """
    # Validate the URL first
    if not validate_youtube_url(url):
        raise ValueError("Invalid YouTube URL or video ID format")
        
    # If it's already just an ID (no slashes or youtube domain)
    if "/" not in url and "youtube.com" not in url and "youtu.be" not in url:
        return url
        
    # Handle youtu.be format
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
        
    # Handle youtube.com format
    if "v=" in url:
        video_id = url.split("v=")[1]
        ampersand_pos = video_id.find("&")
        if ampersand_pos != -1:
            return video_id[:ampersand_pos]
        return video_id
        
    return url


def get_transcript(video_id: str, languages: List[str] = ["en"]) -> str:
    """
    Get the transcript for a YouTube video.
    
    Args:
        video_id: The YouTube video ID
        languages: List of language codes to try, in order of preference
        
    Returns:
        The transcript text as a single string
        
    Raises:
        TranscriptsDisabled: If transcripts are disabled for the video
        NoTranscriptFound: If no transcript is available in the specified languages
        ValueError: If the video ID is invalid or other issues occur
    """
    try:
        # Get the transcript in the specified languages
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        
        # Flatten it to plain text
        transcript = " ".join(chunk["text"] for chunk in transcript_list)
        
        if not transcript.strip():
            raise ValueError("Empty transcript retrieved")
            
        return transcript
        
    except TranscriptsDisabled:
        raise TranscriptsDisabled(f"No captions available for video ID: {video_id}")
    except NoTranscriptFound:
        raise NoTranscriptFound(f"No transcript found in languages: {', '.join(languages)}")
    except Exception as e:
        raise ValueError(f"Error retrieving transcript: {str(e)}")