# YouTube Chatbot

A Python application that allows you to ask questions about YouTube videos based on their transcripts. The chatbot uses LangChain and OpenAI's language models to provide accurate answers based on the video content.

## Overview

This project uses Retrieval-Augmented Generation (RAG) to create a chatbot that can answer questions about YouTube videos. The process works as follows:

1. **Transcript Extraction**: The application extracts the transcript from a YouTube video.
2. **Text Processing**: The transcript is split into manageable chunks.
3. **Embedding Generation**: Each chunk is converted into a vector embedding.
4. **Retrieval**: When a question is asked, the most relevant chunks are retrieved.
5. **Answer Generation**: An LLM generates an answer based on the retrieved context.

## Features

- Extract transcripts from YouTube videos
- Process and index video content for efficient retrieval
- Ask questions about the video content
- Get accurate answers based on the video transcript

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone this repository or download the source code.

2. Install the required dependencies:

```bash
pip install -r requirements.txt