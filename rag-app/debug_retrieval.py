#!/usr/bin/env python3
"""
Debug RAG Retrieval - Help diagnose retrieval issues
This script helps debug why certain queries aren't finding relevant documents.
"""

import sys
from pathlib import Path
import json

# Add the current directory to the Python path
sys.path.append(str(Path(__file__).parent))

from rag_pipeline import RAGPipeline
from document_loader import DocumentProcessor
from vector_store import VectorStore
from config import RAGConfig

def debug_document_processing(file_path):
    """Debug how a document is processed and chunked"""
    print(f"🔍 Debugging document processing for: {file_path}")
    print("=" * 60)
    
    try:
        processor = DocumentProcessor()
        
        # Load document
        print("📄 Loading document...")
        content = processor.load_document(file_path)
        print(f"✅ Document loaded. Length: {len(content)} characters")
        print(f"📖 First 200 characters: {content[:200]}...")
        
        # Process chunks
        print("\n🔪 Chunking document...")
        metadata = {'source': file_path, 'type': 'file'}
        chunks = processor.chunk_document(content, metadata)
        
        print(f"✅ Created {len(chunks)} chunks")
        
        # Show chunks
        print("\n📋 Document chunks:")
        for i, chunk in enumerate(chunks):
            print(f"\nChunk {i+1}:")
            print(f"  Length: {chunk['length']} characters")
            print(f"  Content: {chunk['text'][:100]}...")
            
            # Look for experience-related keywords
            experience_keywords = ['experience', 'years', 'work', 'job', 'position', 'role', 'employment', 'career']
            found_keywords = [kw for kw in experience_keywords if kw.lower() in chunk['text'].lower()]
            if found_keywords:
                print(f"  🎯 Experience keywords found: {found_keywords}")
        
        return chunks
        
    except Exception as e:
        print(f"❌ Error processing document: {e}")
        return []

def debug_similarity_search(chunks, query):
    """Debug similarity search for a specific query"""
    print(f"\n🔍 Debugging similarity search for: '{query}'")
    print("=" * 60)
    
    try:
        # Create vector store
        vector_store = VectorStore()
        vector_store.add_documents(chunks)
        
        # Test different similarity thresholds
        thresholds = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
        
        for threshold in thresholds:
            print(f"\n📊 Testing similarity threshold: {threshold}")
            
            # Temporarily change threshold
            original_threshold = RAGConfig.SIMILARITY_THRESHOLD
            RAGConfig.SIMILARITY_THRESHOLD = threshold
            
            results = vector_store.search(query, k=5, threshold=threshold)
            
            print(f"  Found {len(results)} documents above threshold {threshold}")
            
            for i, result in enumerate(results):
                print(f"    {i+1}. Score: {result['similarity_score']:.4f}")
                print(f"       Text: {result['text'][:80]}...")
            
            # Restore threshold
            RAGConfig.SIMILARITY_THRESHOLD = original_threshold
        
        return results
        
    except Exception as e:
        print(f"❌ Error in similarity search: {e}")
        return []

def debug_full_rag_pipeline(file_path, query):
    """Debug the complete RAG pipeline"""
    print(f"\n🔍 Debugging full RAG pipeline")
    print("=" * 40)
    
    try:
        # Initialize RAG pipeline
        rag = RAGPipeline()
        
        # Process document
        processor = DocumentProcessor()
        content = processor.load_document(file_path)
        metadata = {'source': file_path, 'type': 'file'}
        chunks = processor.chunk_document(content, metadata)
        
        # Add to RAG pipeline
        rag.vector_store.add_documents(chunks)
        
        # Test query with different settings
        print(f"🤖 Testing query: '{query}'")
        
        # Test with lower threshold
        original_threshold = RAGConfig.SIMILARITY_THRESHOLD
        RAGConfig.SIMILARITY_THRESHOLD = 0.1  # Lower threshold
        
        response = rag.query(query, top_k=5, explain_process=True)
        
        print(f"\n📋 Results:")
        print(f"  Answer: {response['answer']}")
        print(f"  Documents retrieved: {response['num_documents_retrieved']}")
        print(f"  Retrieval time: {response['retrieval_time']:.3f}s")
        
        if response['retrieved_documents']:
            print(f"\n📄 Retrieved documents:")
            for i, doc in enumerate(response['retrieved_documents']):
                print(f"  {i+1}. Score: {doc['similarity_score']:.4f}")
                print(f"     Text: {doc['text'][:100]}...")
        
        # Restore threshold
        RAGConfig.SIMILARITY_THRESHOLD = original_threshold
        
        return response
        
    except Exception as e:
        print(f"❌ Error in RAG pipeline: {e}")
        return None

def suggest_improvements(query, chunks):
    """Suggest improvements for better retrieval"""
    print(f"\n💡 Suggestions for improving retrieval:")
    print("=" * 40)
    
    # Analyze query
    query_words = query.lower().split()
    print(f"📝 Query words: {query_words}")
    
    # Look for matches in chunks
    matches_found = []
    for i, chunk in enumerate(chunks):
        chunk_text = chunk['text'].lower()
        matches = [word for word in query_words if word in chunk_text]
        if matches:
            matches_found.append((i, matches))
    
    if matches_found:
        print(f"✅ Found query word matches in {len(matches_found)} chunks:")
        for chunk_idx, matches in matches_found:
            print(f"  Chunk {chunk_idx + 1}: {matches}")
    else:
        print("⚠️  No direct word matches found.")
    
    # Suggestions
    print(f"\n🔧 Recommendations:")
    print("1. Try lowering the similarity threshold (current: 0.5)")
    print("2. Try rephrasing your question with different keywords")
    print("3. Check if your resume contains the information you're looking for")
    print("4. Try more specific questions about resume content")
    
    # Alternative question suggestions
    print(f"\n🎯 Try these alternative questions:")
    if 'experience' in query.lower():
        print("  - 'What work experience do I have?'")
        print("  - 'List my professional background'")
        print("  - 'What jobs have I worked at?'")
        print("  - 'What is my career history?'")
    
    print("  - 'What skills do I have?'")
    print("  - 'What is my educational background?'")
    print("  - 'What companies have I worked for?'")

def main():
    """Main debugging function"""
    print("🐛 RAG Retrieval Debugger")
    print("=" * 30)
    
    # Get file path
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("📁 Enter the path to your resume file: ").strip()
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return
    
    # Get query
    if len(sys.argv) > 2:
        query = sys.argv[2]
    else:
        query = input("❓ Enter your question: ").strip()
    
    print(f"\n🔍 Debugging file: {file_path}")
    print(f"🔍 Debugging query: '{query}'")
    
    # Step 1: Debug document processing
    chunks = debug_document_processing(file_path)
    
    if not chunks:
        print("❌ No chunks created. Check document processing.")
        return
    
    # Step 2: Debug similarity search
    debug_similarity_search(chunks, query)
    
    # Step 3: Debug full RAG pipeline
    debug_full_rag_pipeline(file_path, query)
    
    # Step 4: Provide suggestions
    suggest_improvements(query, chunks)

if __name__ == "__main__":
    main()
