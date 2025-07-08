# -*- coding: utf-8 -*-
"""
Chatbot module for YouTube video Q&A.

This module contains the core functionality for the YouTube chatbot,
including text processing, embedding generation, and question answering.
"""

import os
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from typing import List, Dict, Any, Optional
from openai import AuthenticationError, RateLimitError, APIConnectionError

import config
from youtube_utils import get_transcript, extract_video_id, validate_youtube_url

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class YouTubeChatbot:
    """
    A chatbot that can answer questions about YouTube videos based on their transcripts.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the YouTube chatbot with default settings from config.
        
        Args:
            api_key: Optional OpenAI API key. If not provided, will use the one from config
                    or environment variables.
        """
        # Set API key if provided
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            
        # Use the API key from environment or config
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or config.OPENAI_API_KEY
        
        if not self.api_key:
            logger.error("OpenAI API key is missing")
            raise ValueError("OpenAI API key is missing. Please provide an API key.")
            
        try:
            self.llm = ChatOpenAI(
                model=config.LLM_MODEL,
                temperature=config.LLM_TEMPERATURE
            )
            
            self.embeddings = OpenAIEmbeddings(model=config.EMBEDDING_MODEL)
            
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=config.CHUNK_SIZE,
                chunk_overlap=config.CHUNK_OVERLAP
            )
            
            self.prompt = PromptTemplate(
                template="""
                You are a helpful assistant.
                Answer ONLY from the provided transcript context.
                If the context is insufficient, just say you don't know.

                {context}
                Question: {question}
                """,
                input_variables=['context', 'question']
            )
            
            self.vector_store = None
            self.retriever = None
            self.chain = None
                
        except AuthenticationError as e:
            logger.error(f"Authentication error: {e}")
            raise ValueError(f"Invalid OpenAI API key: {str(e)}")
        except APIConnectionError as e:
            logger.error(f"API connection error: {e}")
            raise ValueError(f"Could not connect to OpenAI API: {str(e)}")
        except Exception as e:
            logger.error(f"Error initializing chatbot: {e}")
            raise ValueError(f"Error initializing chatbot: {str(e)}")
    
    def process_video(self, video_url_or_id: str) -> bool:
        """
        Process a YouTube video by extracting its transcript, splitting it into chunks,
        and creating a vector store for retrieval.
        
        Args:
            video_url_or_id: YouTube video URL or ID
            
        Returns:
            True if processing was successful, False otherwise
            
        Raises:
            ValueError: If the video URL is invalid or transcript cannot be retrieved
        """
        try:
            # Validate and extract video ID
            if not validate_youtube_url(video_url_or_id):
                raise ValueError("Invalid YouTube URL or video ID format")
                
            video_id = extract_video_id(video_url_or_id)
            transcript = get_transcript(video_id)
            
            if not transcript:
                raise ValueError("Could not retrieve transcript for this video")
                
            # Split the transcript into chunks
            chunks = self.text_splitter.create_documents([transcript])
            
            if not chunks:
                raise ValueError("Failed to split transcript into chunks")
            
            # Create vector store
            self.vector_store = FAISS.from_documents(chunks, self.embeddings)
            
            # Create retriever
            self.retriever = self.vector_store.as_retriever(
                search_type="similarity", 
                search_kwargs={"k": config.RETRIEVAL_K}
            )
            
            # Create the chain
            self._create_chain()
            
            return True
            
        except (ValueError, AuthenticationError, RateLimitError) as e:
            # Re-raise these exceptions to be handled by the caller
            raise
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            raise ValueError(f"Error processing video: {str(e)}")
    
    def _create_chain(self) -> None:
        """
        Create the LangChain processing chain for question answering.
        """
        def format_docs(retrieved_docs):
            context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
            return context_text
        
        parallel_chain = RunnableParallel({
            'context': self.retriever | RunnableLambda(format_docs),
            'question': RunnablePassthrough()
        })
        
        parser = StrOutputParser()
        
        self.chain = parallel_chain | self.prompt | self.llm | parser
    
    def ask(self, question: str) -> str:
        """
        Ask a question about the processed YouTube video.
        
        Args:
            question: The question to ask about the video
            
        Returns:
            The answer to the question based on the video transcript
            
        Raises:
            ValueError: If no video has been processed yet or other errors occur
        """
        if not self.chain:
            raise ValueError("Please process a video first using process_video()")
            
        try:
            return self.chain.invoke(question)
        except AuthenticationError as e:
            raise ValueError(f"Authentication error: {str(e)}")
        except RateLimitError as e:
            raise ValueError(f"Rate limit exceeded: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise ValueError(f"Error generating answer: {str(e)}")