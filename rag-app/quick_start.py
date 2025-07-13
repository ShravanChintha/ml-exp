#!/usr/bin/env python3
"""
Quick start script for the RAG Learning Application.
This script demonstrates the core RAG functionality without the web interface.
"""

import os
import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(str(Path(__file__).parent))

from rag_pipeline import RAGPipeline
from document_loader import DocumentProcessor
from config import RAGConfig

def main():
    """Main function to demonstrate RAG functionality"""
    
    print("🤖 RAG Learning Application - Quick Start")
    print("=" * 50)
    
    # Initialize RAG pipeline
    print("Initializing RAG pipeline...")
    try:
        rag = RAGPipeline()
        print("✅ RAG pipeline initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing RAG pipeline: {e}")
        print("Make sure you have installed all dependencies:")
        print("pip install -r requirements.txt")
        return
    
    # Load sample documents
    print("\nLoading sample documents...")
    sample_docs_dir = Path(__file__).parent / "sample_documents"
    
    if sample_docs_dir.exists():
        sample_files = list(sample_docs_dir.glob("*.txt"))
        
        if sample_files:
            try:
                # Process documents
                processor = DocumentProcessor()
                all_chunks = processor.process_multiple_documents([str(f) for f in sample_files])
                
                # Add to RAG pipeline
                rag.vector_store.add_documents(all_chunks)
                
                print(f"✅ Loaded {len(sample_files)} documents with {len(all_chunks)} chunks")
                
                # Show stats
                stats = rag.vector_store.get_document_stats()
                print(f"📊 Vector store contains {stats['total_documents']} document chunks")
                
            except Exception as e:
                print(f"❌ Error loading documents: {e}")
                return
        else:
            print("⚠️  No sample documents found")
    else:
        print("⚠️  Sample documents directory not found")
    
    # Interactive Q&A session
    print("\n🎯 Interactive Q&A Session")
    print("Ask questions about the loaded documents (or 'quit' to exit)")
    print("-" * 50)
    
    # Sample questions to get started
    sample_questions = [
        "What is machine learning?",
        "How do neural networks work?",
        "What are the main NLP tasks?",
        "What is deep learning?",
        "How does sentiment analysis work?"
    ]
    
    print("💡 Sample questions you can try:")
    for i, question in enumerate(sample_questions, 1):
        print(f"{i}. {question}")
    print()
    
    while True:
        try:
            # Get user input
            user_question = input("❓ Your question: ").strip()
            
            if user_question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_question:
                continue
            
            # Process the question
            print(f"\n🔍 Processing: {user_question}")
            print("⏳ Thinking...")
            
            response = rag.query(
                user_question,
                top_k=3,
                include_context=True,
                explain_process=True
            )
            
            # Display results
            print("\n" + "=" * 50)
            print(f"🤖 Answer: {response['answer']}")
            print("=" * 50)
            
            # Show retrieval info
            print(f"\n📋 Retrieved {response['num_documents_retrieved']} relevant documents:")
            for i, doc in enumerate(response['retrieved_documents'], 1):
                print(f"{i}. Score: {doc['similarity_score']:.3f} | Source: {doc['metadata'].get('source', 'Unknown')}")
                print(f"   Preview: {doc['text'][:100]}...")
            
            # Show timing
            print(f"\n⏱️  Processing time: {response['processing_time']:.3f}s")
            print(f"   - Retrieval: {response['retrieval_time']:.3f}s")
            print(f"   - Generation: {response['generation_time']:.3f}s")
            
            # Show process explanation
            if 'process_explanation' in response:
                print("\n🔬 RAG Process Breakdown:")
                for step, details in response['process_explanation'].items():
                    step_name = step.replace('_', ' ').title()
                    print(f"   {step_name}: {details['description']}")
            
            print("\n" + "-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error processing question: {e}")
            continue
    
    # Show final statistics
    print("\n📊 Final Statistics:")
    final_stats = rag.get_statistics()
    print(f"Total queries processed: {final_stats['total_queries']}")
    print(f"Average retrieval time: {final_stats['average_retrieval_time']:.3f}s")
    print(f"Average generation time: {final_stats['average_generation_time']:.3f}s")
    print(f"Documents in knowledge base: {final_stats['vector_store_stats']['total_documents']}")

def test_rag_components():
    """Test individual RAG components"""
    
    print("\n🧪 Testing RAG Components")
    print("=" * 30)
    
    # Test document processor
    print("Testing document processor...")
    processor = DocumentProcessor()
    
    sample_text = """
    This is a sample document for testing the RAG system.
    It demonstrates how text is processed and chunked.
    Each chunk will be embedded and stored for retrieval.
    """
    
    chunks = processor.chunk_document(sample_text, {'source': 'test'})
    print(f"✅ Created {len(chunks)} chunks from sample text")
    
    # Test vector store
    print("\nTesting vector store...")
    from vector_store import VectorStore
    
    vector_store = VectorStore()
    vector_store.add_documents(chunks)
    
    results = vector_store.search("What is this document about?", k=2)
    print(f"✅ Vector store search returned {len(results)} results")
    
    # Test full pipeline
    print("\nTesting full RAG pipeline...")
    rag = RAGPipeline()
    rag.vector_store.add_documents(chunks)
    
    response = rag.query("What is this document about?")
    print(f"✅ RAG pipeline generated answer: {response['answer'][:50]}...")
    
    print("\n🎉 All components working correctly!")

if __name__ == "__main__":
    # Check if we should run tests
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_rag_components()
    else:
        main()
