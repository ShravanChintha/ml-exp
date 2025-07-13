"""
Document processing utilities for the RAG application.
This module handles loading, processing, and chunking of various document formats.
"""

import os
import re
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

import PyPDF2
import docx
from bs4 import BeautifulSoup
import requests

from config import RAGConfig

# Set up logging
logging.basicConfig(level=getattr(logging, RAGConfig.LOG_LEVEL))
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles document loading and processing for RAG"""
    
    def __init__(self, chunk_size: int = RAGConfig.CHUNK_SIZE, 
                 chunk_overlap: int = RAGConfig.CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
    def load_document(self, file_path: str) -> str:
        """
        Load document content from various file formats.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            String content of the document
        """
        file_extension = Path(file_path).suffix.lower()
        
        try:
            if file_extension == '.txt' or file_extension == '.md':
                return self._load_text_file(file_path)
            elif file_extension == '.pdf':
                return self._load_pdf_file(file_path)
            elif file_extension == '.docx':
                return self._load_docx_file(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {str(e)}")
            raise
    
    def _load_text_file(self, file_path: str) -> str:
        """Load content from text/markdown files"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _load_pdf_file(self, file_path: str) -> str:
        """Load content from PDF files"""
        content = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
        return content
    
    def _load_docx_file(self, file_path: str) -> str:
        """Load content from Word documents"""
        doc = docx.Document(file_path)
        content = ""
        for paragraph in doc.paragraphs:
            content += paragraph.text + "\n"
        return content
    
    def load_web_page(self, url: str) -> str:
        """
        Load content from a web page.
        
        Args:
            url: URL of the web page
            
        Returns:
            Text content of the web page
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up the text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            logger.error(f"Error loading web page {url}: {str(e)}")
            raise
    
    def chunk_document(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Split document into chunks for embedding.
        
        Args:
            text: Document text to chunk
            metadata: Optional metadata to include with chunks
            
        Returns:
            List of chunks with metadata
        """
        if not text.strip():
            return []
        
        # Clean the text
        text = self._clean_text(text)
        
        # Split into sentences first
        sentences = self._split_into_sentences(text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed chunk size, save current chunk
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                chunks.append({
                    'text': current_chunk.strip(),
                    'metadata': metadata or {},
                    'length': len(current_chunk.strip())
                })
                
                # Start new chunk with overlap
                if self.chunk_overlap > 0:
                    words = current_chunk.split()
                    overlap_words = words[-self.chunk_overlap:]
                    current_chunk = ' '.join(overlap_words) + ' '
                else:
                    current_chunk = ""
            
            current_chunk += sentence + ' '
        
        # Add the last chunk if it has content
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'metadata': metadata or {},
                'length': len(current_chunk.strip())
            })
        
        logger.info(f"Created {len(chunks)} chunks from document")
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        return text.strip()
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting based on punctuation
        sentences = re.split(r'[.!?]+', text)
        
        # Clean up sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def process_multiple_documents(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple documents and return all chunks.
        
        Args:
            file_paths: List of file paths to process
            
        Returns:
            List of all chunks from all documents
        """
        all_chunks = []
        
        for file_path in file_paths:
            try:
                logger.info(f"Processing document: {file_path}")
                
                # Load document
                content = self.load_document(file_path)
                
                # Create metadata
                metadata = {
                    'source': file_path,
                    'filename': os.path.basename(file_path),
                    'file_size': os.path.getsize(file_path),
                    'file_type': Path(file_path).suffix.lower()
                }
                
                # Chunk document
                chunks = self.chunk_document(content, metadata)
                all_chunks.extend(chunks)
                
                logger.info(f"Successfully processed {file_path}: {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {str(e)}")
                continue
        
        return all_chunks

# Example usage and testing
if __name__ == "__main__":
    # Test document processor
    processor = DocumentProcessor()
    
    # Test with sample text
    sample_text = """
    This is a sample document for testing the RAG application.
    It contains multiple sentences and paragraphs to demonstrate
    how the document processor works.
    
    The processor will split this text into chunks that can be
    embedded and stored in a vector database. Each chunk will
    have associated metadata for tracking and retrieval.
    """
    
    chunks = processor.chunk_document(sample_text, {'source': 'sample_text'})
    
    print(f"Created {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1}: {chunk['text'][:100]}...")
        print(f"Length: {chunk['length']}")
        print(f"Metadata: {chunk['metadata']}")
        print("-" * 50)
