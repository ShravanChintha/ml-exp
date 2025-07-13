"""
Vector store implementation for the RAG application.
This module handles embedding generation and similarity search using FAISS.
"""

import os
import pickle
from typing import List, Dict, Any, Optional, Tuple
import logging
import numpy as np

import faiss
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from config import RAGConfig

# Set up logging
logging.basicConfig(level=getattr(logging, RAGConfig.LOG_LEVEL))
logger = logging.getLogger(__name__)

class VectorStore:
    """Vector store for document embeddings using FAISS"""
    
    def __init__(self, embedding_model_name: str = RAGConfig.EMBEDDING_MODEL):
        """
        Initialize vector store with embedding model.
        
        Args:
            embedding_model_name: Name of the Hugging Face embedding model
        """
        self.embedding_model_name = embedding_model_name
        self.embedding_model = None
        self.index = None
        self.documents = []
        self.embeddings = []
        self.dimension = None
        
        # Load embedding model
        self._load_embedding_model()
    
    def _load_embedding_model(self):
        """Load the sentence transformer model for embeddings"""
        try:
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            
            # Get embedding dimension
            sample_embedding = self.embedding_model.encode(["test"])
            self.dimension = sample_embedding.shape[1]
            
            logger.info(f"Embedding model loaded successfully. Dimension: {self.dimension}")
            
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document dictionaries with 'text' and 'metadata' keys
        """
        if not documents:
            logger.warning("No documents to add")
            return
        
        logger.info(f"Adding {len(documents)} documents to vector store")
        
        # Extract text content
        texts = [doc['text'] for doc in documents]
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        embeddings = self.embedding_model.encode(
            texts, 
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # Initialize or update FAISS index
        if self.index is None:
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings)
        
        # Store documents and embeddings
        self.documents.extend(documents)
        self.embeddings.extend(embeddings.tolist())
        
        logger.info(f"Successfully added {len(documents)} documents. Total: {len(self.documents)}")
    
    def search(self, query: str, k: int = RAGConfig.TOP_K_DOCUMENTS, 
               threshold: float = RAGConfig.SIMILARITY_THRESHOLD) -> List[Dict[str, Any]]:
        """
        Search for similar documents using the query.
        
        Args:
            query: Search query
            k: Number of documents to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of similar documents with scores
        """
        if self.index is None or len(self.documents) == 0:
            logger.warning("No documents in vector store")
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)
        
        # Search in FAISS index
        scores, indices = self.index.search(query_embedding, min(k, len(self.documents)))
        
        # Prepare results
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if score >= threshold:  # Filter by threshold
                doc = self.documents[idx].copy()
                doc['similarity_score'] = float(score)
                doc['rank'] = i + 1
                results.append(doc)
        
        logger.info(f"Found {len(results)} similar documents for query: '{query[:50]}...'")
        return results
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        if not self.documents:
            return {
                'total_documents': 0,
                'total_embeddings': 0,
                'embedding_dimension': self.dimension,
                'model_name': self.embedding_model_name
            }
        
        # Calculate document length statistics
        lengths = [len(doc['text']) for doc in self.documents]
        
        return {
            'total_documents': len(self.documents),
            'total_embeddings': len(self.embeddings),
            'embedding_dimension': self.dimension,
            'model_name': self.embedding_model_name,
            'avg_document_length': np.mean(lengths),
            'min_document_length': np.min(lengths),
            'max_document_length': np.max(lengths),
            'total_text_length': sum(lengths)
        }
    
    def save_to_disk(self, path: str) -> None:
        """
        Save vector store to disk.
        
        Args:
            path: Directory path to save the vector store
        """
        try:
            os.makedirs(path, exist_ok=True)
            
            # Save FAISS index
            if self.index is not None:
                faiss.write_index(self.index, os.path.join(path, "faiss_index.bin"))
            
            # Save documents and metadata
            with open(os.path.join(path, "documents.pkl"), "wb") as f:
                pickle.dump(self.documents, f)
            
            with open(os.path.join(path, "embeddings.pkl"), "wb") as f:
                pickle.dump(self.embeddings, f)
            
            # Save configuration
            config = {
                'embedding_model_name': self.embedding_model_name,
                'dimension': self.dimension,
                'total_documents': len(self.documents)
            }
            
            with open(os.path.join(path, "config.pkl"), "wb") as f:
                pickle.dump(config, f)
            
            logger.info(f"Vector store saved to {path}")
            
        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}")
            raise
    
    def load_from_disk(self, path: str) -> None:
        """
        Load vector store from disk.
        
        Args:
            path: Directory path to load the vector store from
        """
        try:
            # Load configuration
            with open(os.path.join(path, "config.pkl"), "rb") as f:
                config = pickle.load(f)
            
            # Verify model compatibility
            if config['embedding_model_name'] != self.embedding_model_name:
                logger.warning(f"Model mismatch: stored={config['embedding_model_name']}, current={self.embedding_model_name}")
            
            # Load FAISS index
            index_path = os.path.join(path, "faiss_index.bin")
            if os.path.exists(index_path):
                self.index = faiss.read_index(index_path)
            
            # Load documents
            with open(os.path.join(path, "documents.pkl"), "rb") as f:
                self.documents = pickle.load(f)
            
            with open(os.path.join(path, "embeddings.pkl"), "rb") as f:
                self.embeddings = pickle.load(f)
            
            self.dimension = config['dimension']
            
            logger.info(f"Vector store loaded from {path}. {len(self.documents)} documents loaded.")
            
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            raise
    
    def clear(self) -> None:
        """Clear all documents and embeddings from the vector store"""
        self.index = None
        self.documents = []
        self.embeddings = []
        logger.info("Vector store cleared")

# Example usage and testing
if __name__ == "__main__":
    # Test vector store
    vector_store = VectorStore()
    
    # Sample documents
    sample_docs = [
        {
            'text': "Machine learning is a subset of artificial intelligence that focuses on algorithms.",
            'metadata': {'source': 'ml_intro.txt', 'topic': 'machine_learning'}
        },
        {
            'text': "Deep learning uses neural networks with multiple layers to learn complex patterns.",
            'metadata': {'source': 'dl_intro.txt', 'topic': 'deep_learning'}
        },
        {
            'text': "Natural language processing enables computers to understand and generate human language.",
            'metadata': {'source': 'nlp_intro.txt', 'topic': 'nlp'}
        },
        {
            'text': "Computer vision allows machines to interpret and analyze visual information from images.",
            'metadata': {'source': 'cv_intro.txt', 'topic': 'computer_vision'}
        }
    ]
    
    # Add documents
    vector_store.add_documents(sample_docs)
    
    # Test search
    results = vector_store.search("What is machine learning?", k=2)
    
    print("Search Results:")
    for result in results:
        print(f"Score: {result['similarity_score']:.3f}")
        print(f"Text: {result['text']}")
        print(f"Metadata: {result['metadata']}")
        print("-" * 50)
    
    # Show stats
    stats = vector_store.get_document_stats()
    print(f"\nVector Store Stats:")
    for key, value in stats.items():
        print(f"{key}: {value}")
