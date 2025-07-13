#!/usr/bin/env python3
"""
Improved RAG Configuration for Better Retrieval
This script provides better default settings for document retrieval.
"""

import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(str(Path(__file__).parent))

from config import RAGConfig

def apply_better_retrieval_settings():
    """Apply better settings for document retrieval"""
    print("🔧 Applying improved RAG settings for better retrieval...")
    
    # Lower similarity threshold for better recall
    RAGConfig.SIMILARITY_THRESHOLD = 0.2  # Lower threshold
    
    # Increase number of documents to retrieve
    RAGConfig.TOP_K_DOCUMENTS = 5  # More documents
    
    # Smaller chunks for better granularity
    RAGConfig.CHUNK_SIZE = 256  # Smaller chunks
    RAGConfig.CHUNK_OVERLAP = 50  # Good overlap
    
    # Longer generation for more detailed answers
    RAGConfig.MAX_GENERATION_LENGTH = 512  # Longer answers
    
    print("✅ Applied improved settings:")
    print(f"  - Similarity threshold: {RAGConfig.SIMILARITY_THRESHOLD}")
    print(f"  - Top K documents: {RAGConfig.TOP_K_DOCUMENTS}")
    print(f"  - Chunk size: {RAGConfig.CHUNK_SIZE}")
    print(f"  - Chunk overlap: {RAGConfig.CHUNK_OVERLAP}")
    print(f"  - Max generation length: {RAGConfig.MAX_GENERATION_LENGTH}")

def create_resume_specific_rag():
    """Create a RAG pipeline optimized for resume queries"""
    from rag_pipeline import RAGPipeline
    
    print("🎯 Creating resume-optimized RAG pipeline...")
    
    # Apply better settings
    apply_better_retrieval_settings()
    
    # Create pipeline
    rag = RAGPipeline()
    
    return rag

def test_resume_queries(rag_pipeline, document_path):
    """Test common resume queries"""
    print("🧪 Testing common resume queries...")
    
    from document_loader import DocumentProcessor
    
    # Load and process document
    processor = DocumentProcessor()
    content = processor.load_document(document_path)
    metadata = {'source': document_path, 'type': 'resume'}
    chunks = processor.chunk_document(content, metadata)
    
    # Add to pipeline
    rag_pipeline.vector_store.add_documents(chunks)
    
    # Test queries
    test_queries = [
        "How many years of experience do I have?",
        "What is my work experience?",
        "What companies have I worked for?",
        "What skills do I have?",
        "What is my educational background?",
        "What positions have I held?",
        "What is my career history?",
        "List my professional experience",
        "What jobs have I worked at?",
        "What is my work background?"
    ]
    
    results = []
    
    for query in test_queries:
        print(f"\n❓ Testing: '{query}'")
        
        response = rag_pipeline.query(query, top_k=3)
        
        print(f"📋 Retrieved {response['num_documents_retrieved']} documents")
        print(f"🤖 Answer: {response['answer'][:100]}...")
        
        if response['retrieved_documents']:
            best_score = max(doc['similarity_score'] for doc in response['retrieved_documents'])
            print(f"🎯 Best similarity score: {best_score:.4f}")
        
        results.append({
            'query': query,
            'answer': response['answer'],
            'num_docs': response['num_documents_retrieved'],
            'best_score': best_score if response['retrieved_documents'] else 0.0
        })
    
    return results

def main():
    """Main function"""
    print("🎯 Resume RAG Optimizer")
    print("=" * 25)
    
    # Get resume file path
    if len(sys.argv) > 1:
        resume_path = sys.argv[1]
    else:
        resume_path = input("📁 Enter the path to your resume: ").strip()
    
    if not Path(resume_path).exists():
        print(f"❌ Resume file not found: {resume_path}")
        return
    
    try:
        # Create optimized RAG pipeline
        rag = create_resume_specific_rag()
        
        # Test queries
        results = test_resume_queries(rag, resume_path)
        
        # Show summary
        print("\n📊 Test Results Summary:")
        print("=" * 30)
        
        successful_queries = [r for r in results if r['num_docs'] > 0]
        
        print(f"✅ Successful queries: {len(successful_queries)}/{len(results)}")
        print(f"📈 Average similarity score: {sum(r['best_score'] for r in results) / len(results):.4f}")
        
        if successful_queries:
            print(f"🎯 Best performing queries:")
            best_queries = sorted(successful_queries, key=lambda x: x['best_score'], reverse=True)[:3]
            for i, query in enumerate(best_queries, 1):
                print(f"  {i}. {query['query']} (Score: {query['best_score']:.4f})")
        
        # Provide recommendations
        print(f"\n💡 Recommendations:")
        if len(successful_queries) < len(results) * 0.7:  # Less than 70% success
            print("  - Consider lowering similarity threshold further")
            print("  - Check if resume contains the information you're looking for")
            print("  - Try more specific questions about resume content")
        else:
            print("  - RAG pipeline is working well for your resume!")
            print("  - Try the optimized settings in the main app")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
