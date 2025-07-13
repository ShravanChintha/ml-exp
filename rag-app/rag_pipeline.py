"""
Core RAG (Retrieval-Augmented Generation) Pipeline Implementation.
This module combines document retrieval with language generation.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import time

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch

from config import RAGConfig
from vector_store import VectorStore
from document_loader import DocumentProcessor

# Set up logging
logging.basicConfig(level=getattr(logging, RAGConfig.LOG_LEVEL))
logger = logging.getLogger(__name__)

class RAGPipeline:
    """Complete RAG pipeline combining retrieval and generation"""
    
    def __init__(self, 
                 embedding_model: str = RAGConfig.EMBEDDING_MODEL,
                 generation_model: str = RAGConfig.GENERATION_MODEL):
        """
        Initialize RAG pipeline.
        
        Args:
            embedding_model: Model for document embeddings
            generation_model: Model for text generation
        """
        self.embedding_model_name = embedding_model
        self.generation_model_name = generation_model
        
        # Initialize components
        self.vector_store = VectorStore(embedding_model)
        self.document_processor = DocumentProcessor()
        self.generator = None
        self.tokenizer = None
        
        # Load generation model
        self._load_generation_model()
        
        # Statistics
        self.query_count = 0
        self.total_retrieval_time = 0
        self.total_generation_time = 0
    
    def _load_generation_model(self):
        """Load the text generation model"""
        try:
            logger.info(f"Loading generation model: {self.generation_model_name}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.generation_model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(self.generation_model_name)
            
            # Create pipeline
            self.generator = pipeline(
                "text2text-generation",
                model=model,
                tokenizer=self.tokenizer,
                device=0 if torch.cuda.is_available() else -1
            )
            
            logger.info("Generation model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading generation model: {str(e)}")
            raise
    
    def add_documents(self, documents: List[str]) -> Dict[str, Any]:
        """
        Add documents to the RAG system.
        
        Args:
            documents: List of document file paths or URLs
            
        Returns:
            Processing statistics
        """
        start_time = time.time()
        
        # Process documents
        all_chunks = []
        for doc_path in documents:
            try:
                if doc_path.startswith('http'):
                    # Web page
                    content = self.document_processor.load_web_page(doc_path)
                    metadata = {'source': doc_path, 'type': 'web_page'}
                else:
                    # File
                    content = self.document_processor.load_document(doc_path)
                    metadata = {'source': doc_path, 'type': 'file'}
                
                # Chunk the document
                chunks = self.document_processor.chunk_document(content, metadata)
                all_chunks.extend(chunks)
                
            except Exception as e:
                logger.error(f"Error processing document {doc_path}: {str(e)}")
                continue
        
        # Add to vector store
        self.vector_store.add_documents(all_chunks)
        
        processing_time = time.time() - start_time
        
        return {
            'total_documents_processed': len(documents),
            'total_chunks_created': len(all_chunks),
            'processing_time_seconds': processing_time,
            'vector_store_stats': self.vector_store.get_document_stats()
        }
    
    def query(self, question: str, 
              top_k: int = RAGConfig.TOP_K_DOCUMENTS,
              include_context: bool = True,
              explain_process: bool = False) -> Dict[str, Any]:
        """
        Execute a RAG query.
        
        Args:
            question: User's question
            top_k: Number of documents to retrieve
            include_context: Whether to include retrieved context in response
            explain_process: Whether to include detailed process information
            
        Returns:
            RAG response with answer and metadata
        """
        start_time = time.time()
        self.query_count += 1
        
        # Step 1: Retrieve relevant documents
        retrieval_start = time.time()
        relevant_docs = self.vector_store.search(question, k=top_k)
        retrieval_time = time.time() - retrieval_start
        self.total_retrieval_time += retrieval_time
        
        if not relevant_docs:
            return {
                'answer': "I don't have relevant information to answer your question. Please add some documents first.",
                'question': question,
                'retrieved_documents': [],
                'context_used': "",
                'processing_time': time.time() - start_time,
                'retrieval_time': retrieval_time,
                'generation_time': 0,
                'num_documents_retrieved': 0,
                'error': "No relevant documents found"
            }
        
        # Step 2: Prepare context
        context_parts = []
        for i, doc in enumerate(relevant_docs):
            context_parts.append(f"Document {i+1} (Score: {doc['similarity_score']:.3f}):\n{doc['text']}")
        
        context = "\n\n".join(context_parts)
        
        # Step 3: Generate answer
        generation_start = time.time()
        answer = self._generate_answer(question, context)
        generation_time = time.time() - generation_start
        self.total_generation_time += generation_time
        
        total_time = time.time() - start_time
        
        # Prepare response
        response = {
            'answer': answer,
            'question': question,
            'retrieved_documents': relevant_docs,
            'context_used': context if include_context else "",
            'processing_time': total_time,
            'retrieval_time': retrieval_time,
            'generation_time': generation_time,
            'num_documents_retrieved': len(relevant_docs)
        }
        
        # Add detailed process explanation if requested
        if explain_process:
            response['process_explanation'] = self._explain_process(question, relevant_docs, answer)
        
        return response
    
    def _generate_answer(self, question: str, context: str) -> str:
        """
        Generate answer using the language model.
        
        Args:
            question: User's question
            context: Retrieved context
            
        Returns:
            Generated answer
        """
        try:
            # Prepare prompt
            prompt = f"""Context: {context}

Question: {question}

Answer based on the context provided:"""
            
            # Generate response
            response = self.generator(
                prompt,
                max_length=RAGConfig.MAX_GENERATION_LENGTH,
                temperature=RAGConfig.TEMPERATURE,
                do_sample=RAGConfig.DO_SAMPLE,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract answer
            answer = response[0]['generated_text']
            
            # Clean up the answer (remove the prompt part)
            if "Answer based on the context provided:" in answer:
                answer = answer.split("Answer based on the context provided:")[-1].strip()
            
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return f"I encountered an error while generating the answer: {str(e)}"
    
    def _explain_process(self, question: str, retrieved_docs: List[Dict], answer: str) -> Dict[str, Any]:
        """
        Explain the RAG process step by step.
        
        Args:
            question: Original question
            retrieved_docs: Retrieved documents
            answer: Generated answer
            
        Returns:
            Process explanation
        """
        return {
            'step_1_query_processing': {
                'description': "Convert the user's question into an embedding vector",
                'question': question,
                'embedding_model': self.embedding_model_name
            },
            'step_2_retrieval': {
                'description': "Search for similar documents using vector similarity",
                'num_documents_found': len(retrieved_docs),
                'similarity_scores': [doc['similarity_score'] for doc in retrieved_docs],
                'retrieval_method': "FAISS cosine similarity search"
            },
            'step_3_context_preparation': {
                'description': "Combine retrieved documents into context",
                'context_length': sum(len(doc['text']) for doc in retrieved_docs),
                'sources': [doc['metadata'].get('source', 'unknown') for doc in retrieved_docs]
            },
            'step_4_generation': {
                'description': "Generate answer using context and question",
                'generation_model': self.generation_model_name,
                'context_used': True,
                'answer_length': len(answer)
            }
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get RAG pipeline statistics"""
        return {
            'total_queries': self.query_count,
            'average_retrieval_time': self.total_retrieval_time / max(self.query_count, 1),
            'average_generation_time': self.total_generation_time / max(self.query_count, 1),
            'vector_store_stats': self.vector_store.get_document_stats(),
            'models': {
                'embedding_model': self.embedding_model_name,
                'generation_model': self.generation_model_name
            }
        }
    
    def clear_knowledge_base(self):
        """Clear all documents from the knowledge base"""
        self.vector_store.clear()
        logger.info("Knowledge base cleared")
    
    def save_knowledge_base(self, path: str):
        """Save the knowledge base to disk"""
        self.vector_store.save_to_disk(path)
        logger.info(f"Knowledge base saved to {path}")
    
    def load_knowledge_base(self, path: str):
        """Load the knowledge base from disk"""
        self.vector_store.load_from_disk(path)
        logger.info(f"Knowledge base loaded from {path}")

# Example usage and testing
if __name__ == "__main__":
    # Initialize RAG pipeline
    rag = RAGPipeline()
    
    # Sample documents (you can replace with real file paths)
    sample_docs = [
        "sample_documents/ml_basics.txt",
        "sample_documents/ai_overview.txt"
    ]
    
    print("RAG Pipeline Example")
    print("=" * 50)
    
    # Add sample text documents (simulate adding docs)
    sample_texts = [
        "Machine learning is a method of data analysis that automates analytical model building. It is a branch of artificial intelligence based on the idea that systems can learn from data, identify patterns and make decisions with minimal human intervention.",
        "Deep learning is part of a broader family of machine learning methods based on artificial neural networks. Learning can be supervised, semi-supervised or unsupervised.",
        "Natural language processing (NLP) is a subfield of linguistics, computer science, and artificial intelligence concerned with the interactions between computers and human language."
    ]
    
    # Simulate document processing
    documents = []
    for i, text in enumerate(sample_texts):
        documents.append({
            'text': text,
            'metadata': {'source': f'sample_doc_{i}.txt', 'topic': 'AI/ML'}
        })
    
    # Add documents to vector store
    rag.vector_store.add_documents(documents)
    
    # Test queries
    test_questions = [
        "What is machine learning?",
        "Tell me about deep learning",
        "What is NLP?",
        "How does AI work?"
    ]
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        print("-" * 30)
        
        response = rag.query(question, explain_process=True)
        
        print(f"Answer: {response['answer']}")
        print(f"Retrieved {response['num_documents_retrieved']} documents")
        print(f"Processing time: {response['processing_time']:.3f} seconds")
        
        if 'process_explanation' in response:
            print("\nProcess Explanation:")
            for step, details in response['process_explanation'].items():
                print(f"  {step}: {details['description']}")
    
    # Show statistics
    print(f"\nRAG Pipeline Statistics:")
    stats = rag.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
