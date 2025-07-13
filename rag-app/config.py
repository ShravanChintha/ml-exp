"""
Configuration settings for the RAG application.
This file contains all the configurable parameters for the RAG pipeline.
"""

import os
from typing import Dict, Any

class RAGConfig:
    """Configuration class for RAG application"""
    
    # Model configurations
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    GENERATION_MODEL = "google/flan-t5-base"  # Smaller model for learning
    
    # Document processing
    CHUNK_SIZE = 256  # Size of text chunks for embedding (smaller = more granular)
    CHUNK_OVERLAP = 50  # Overlap between chunks
    
    # Retrieval settings
    TOP_K_DOCUMENTS = 5  # Number of documents to retrieve
    SIMILARITY_THRESHOLD = 0.2  # Minimum similarity score (lower = more permissive)
    
    # Vector store settings
    VECTOR_STORE_PATH = "vector_store"
    FAISS_INDEX_PATH = "faiss_index"
    
    # Generation settings
    MAX_GENERATION_LENGTH = 256
    TEMPERATURE = 0.7
    DO_SAMPLE = True
    
    # UI settings
    APP_TITLE = "RAG Learning Application"
    APP_DESCRIPTION = "Learn how Retrieval-Augmented Generation works!"
    
    # File upload settings
    ALLOWED_EXTENSIONS = ['.txt', '.pdf', '.docx', '.md']
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Logging
    LOG_LEVEL = "INFO"
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get all configuration as a dictionary"""
        return {
            attr: getattr(cls, attr) 
            for attr in dir(cls) 
            if not attr.startswith('_') and not callable(getattr(cls, attr))
        }
    
    @classmethod
    def update_config(cls, **kwargs):
        """Update configuration values"""
        for key, value in kwargs.items():
            if hasattr(cls, key):
                setattr(cls, key, value)
            else:
                raise ValueError(f"Invalid configuration key: {key}")

# Environment variable overrides
if os.getenv("EMBEDDING_MODEL"):
    RAGConfig.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

if os.getenv("GENERATION_MODEL"):
    RAGConfig.GENERATION_MODEL = os.getenv("GENERATION_MODEL")

if os.getenv("CHUNK_SIZE"):
    RAGConfig.CHUNK_SIZE = int(os.getenv("CHUNK_SIZE"))

if os.getenv("TOP_K_DOCUMENTS"):
    RAGConfig.TOP_K_DOCUMENTS = int(os.getenv("TOP_K_DOCUMENTS"))
