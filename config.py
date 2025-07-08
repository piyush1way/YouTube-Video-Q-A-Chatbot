# -*- coding: utf-8 -*-
"""
Configuration module for YouTube Chatbot.

This module loads environment variables and defines configuration constants
used throughout the application. API keys should be provided at runtime
rather than hardcoded here.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# OpenAI API configuration
# Note: API key should be provided at runtime, not hardcoded here
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# LLM configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))

# Embedding configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# Text splitting configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Retrieval configuration
RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", "4"))

# Default language for transcripts
DEFAULT_TRANSCRIPT_LANGUAGE = os.getenv("DEFAULT_TRANSCRIPT_LANGUAGE", "en")