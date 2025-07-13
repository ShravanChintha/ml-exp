"""
Streamlit Web Application for RAG Learning.
This is the main user interface for the RAG application.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any
import time
import json

from config import RAGConfig
from rag_pipeline import RAGPipeline
from document_loader import DocumentProcessor

# Page configuration
st.set_page_config(
    page_title=RAGConfig.APP_TITLE,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #2E86AB;
    text-align: center;
    margin-bottom: 1rem;
}
.sub-header {
    font-size: 1.5rem;
    color: #A23B72;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
}
.info-box {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}
.success-box {
    background-color: #d4edda;
    color: #155724;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}
.error-box {
    background-color: #f8d7da;
    color: #721c24;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}
.metric-container {
    background-color: #e8f4f8;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'rag_pipeline' not in st.session_state:
    st.session_state.rag_pipeline = None
    st.session_state.documents_added = False
    st.session_state.query_history = []
    st.session_state.processing_stats = {}

def initialize_rag_pipeline():
    """Initialize the RAG pipeline"""
    if st.session_state.rag_pipeline is None:
        with st.spinner("Initializing RAG pipeline... This may take a moment."):
            try:
                st.session_state.rag_pipeline = RAGPipeline()
                st.success("RAG pipeline initialized successfully!")
            except Exception as e:
                st.error(f"Error initializing RAG pipeline: {str(e)}")
                return False
    return True

def main():
    """Main application function"""
    
    # Header
    st.markdown('<div class="main-header">🤖 RAG Learning Application</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; margin-bottom: 2rem;">Learn how Retrieval-Augmented Generation works!</div>', unsafe_allow_html=True)
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Home", "📚 Add Documents", "❓ Ask Questions", "📊 Analytics", "ℹ️ How RAG Works"]
    )
    
    # Initialize RAG pipeline
    if not initialize_rag_pipeline():
        st.stop()
    
    # Route to different pages
    if page == "🏠 Home":
        show_home_page()
    elif page == "📚 Add Documents":
        show_document_upload_page()
    elif page == "❓ Ask Questions":
        show_question_page()
    elif page == "📊 Analytics":
        show_analytics_page()
    elif page == "ℹ️ How RAG Works":
        show_how_rag_works_page()

def show_home_page():
    """Show the home page with overview"""
    
    st.markdown('<div class="sub-header">Welcome to RAG Learning!</div>', unsafe_allow_html=True)
    
    # Overview
    st.markdown("""
    <div class="info-box">
    <h3>What is RAG?</h3>
    <p><strong>Retrieval-Augmented Generation (RAG)</strong> is a powerful AI technique that combines:</p>
    <ul>
        <li>🔍 <strong>Information Retrieval</strong>: Finding relevant documents from a knowledge base</li>
        <li>🤖 <strong>Text Generation</strong>: Using an AI model to generate answers based on retrieved context</li>
    </ul>
    <p>This application helps you understand how RAG works by letting you:</p>
    <ul>
        <li>📚 Upload your own documents</li>
        <li>❓ Ask questions about those documents</li>
        <li>📊 See how the system retrieves and uses information</li>
        <li>🔬 Analyze the entire process step by step</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Current status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        if st.session_state.rag_pipeline:
            stats = st.session_state.rag_pipeline.get_statistics()
            st.metric("Documents", stats['vector_store_stats']['total_documents'])
        else:
            st.metric("Documents", 0)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        if st.session_state.rag_pipeline:
            stats = st.session_state.rag_pipeline.get_statistics()
            st.metric("Queries", stats['total_queries'])
        else:
            st.metric("Queries", 0)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Status", "Ready" if st.session_state.rag_pipeline else "Initializing")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick start guide
    st.markdown('<div class="sub-header">Quick Start Guide</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <h4>🚀 Get Started in 3 Steps:</h4>
    <ol>
        <li><strong>Add Documents</strong> - Upload text files, PDFs, or enter text manually</li>
        <li><strong>Ask Questions</strong> - Query your documents using natural language</li>
        <li><strong>Explore Results</strong> - See how RAG retrieves relevant information and generates answers</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # Model information
    st.markdown('<div class="sub-header">Model Information</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🔤 Embedding Model**
        - Model: `sentence-transformers/all-MiniLM-L6-v2`
        - Purpose: Convert text to numerical vectors
        - Used for: Document similarity search
        """)
    
    with col2:
        st.markdown("""
        **🤖 Generation Model**
        - Model: `google/flan-t5-base`
        - Purpose: Generate human-like text
        - Used for: Answering questions based on context
        """)

def show_document_upload_page():
    """Show the document upload page"""
    
    st.markdown('<div class="sub-header">📚 Add Documents to Knowledge Base</div>', unsafe_allow_html=True)
    
    # Upload method selection
    upload_method = st.selectbox(
        "Choose how to add documents:",
        ["📁 Upload Files", "✏️ Enter Text Manually", "🌐 Add from URL"]
    )
    
    if upload_method == "📁 Upload Files":
        show_file_upload_section()
    elif upload_method == "✏️ Enter Text Manually":
        show_text_input_section()
    elif upload_method == "🌐 Add from URL":
        show_url_input_section()

def show_file_upload_section():
    """Show file upload section"""
    
    st.markdown("### Upload Documents")
    st.markdown("Supported formats: TXT, PDF, DOCX, MD")
    
    uploaded_files = st.file_uploader(
        "Choose files",
        type=['txt', 'pdf', 'docx', 'md'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.write(f"Selected {len(uploaded_files)} files:")
        for file in uploaded_files:
            st.write(f"- {file.name} ({file.size} bytes)")
        
        if st.button("Process Documents", type="primary"):
            process_uploaded_files(uploaded_files)

def show_text_input_section():
    """Show text input section"""
    
    st.markdown("### Enter Text Manually")
    
    text_input = st.text_area(
        "Enter your text:",
        height=200,
        placeholder="Paste your text here..."
    )
    
    title = st.text_input("Document Title (optional)", placeholder="My Document")
    
    if text_input and st.button("Add Text", type="primary"):
        process_text_input(text_input, title)

def show_url_input_section():
    """Show URL input section"""
    
    st.markdown("### Add Document from URL")
    
    url = st.text_input("Enter URL:", placeholder="https://example.com/article")
    
    if url and st.button("Fetch and Process", type="primary"):
        process_url_input(url)

def process_uploaded_files(uploaded_files):
    """Process uploaded files"""
    
    with st.spinner("Processing documents..."):
        try:
            # Save uploaded files temporarily and process
            import tempfile
            import os
            
            temp_files = []
            for uploaded_file in uploaded_files:
                # Create temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    temp_files.append(tmp_file.name)
            
            # Process documents
            processor = DocumentProcessor()
            all_chunks = processor.process_multiple_documents(temp_files)
            
            # Add to RAG pipeline
            st.session_state.rag_pipeline.vector_store.add_documents(all_chunks)
            
            # Clean up temp files
            for temp_file in temp_files:
                os.unlink(temp_file)
            
            st.success(f"Successfully processed {len(uploaded_files)} documents!")
            st.session_state.documents_added = True
            
            # Show processing stats
            stats = st.session_state.rag_pipeline.vector_store.get_document_stats()
            st.info(f"Total documents in knowledge base: {stats['total_documents']}")
            
        except Exception as e:
            st.error(f"Error processing documents: {str(e)}")

def process_text_input(text_input, title):
    """Process manually entered text"""
    
    with st.spinner("Processing text..."):
        try:
            processor = DocumentProcessor()
            
            # Create document
            metadata = {'source': title or 'Manual Input', 'type': 'manual'}
            chunks = processor.chunk_document(text_input, metadata)
            
            # Add to RAG pipeline
            st.session_state.rag_pipeline.vector_store.add_documents(chunks)
            
            st.success(f"Successfully added text! Created {len(chunks)} chunks.")
            st.session_state.documents_added = True
            
        except Exception as e:
            st.error(f"Error processing text: {str(e)}")

def process_url_input(url):
    """Process URL input"""
    
    with st.spinner("Fetching and processing URL..."):
        try:
            processor = DocumentProcessor()
            
            # Load web page
            content = processor.load_web_page(url)
            
            # Create document
            metadata = {'source': url, 'type': 'web_page'}
            chunks = processor.chunk_document(content, metadata)
            
            # Add to RAG pipeline
            st.session_state.rag_pipeline.vector_store.add_documents(chunks)
            
            st.success(f"Successfully processed URL! Created {len(chunks)} chunks.")
            st.session_state.documents_added = True
            
        except Exception as e:
            st.error(f"Error processing URL: {str(e)}")

def show_question_page():
    """Show the question asking page"""
    
    st.markdown('<div class="sub-header">❓ Ask Questions</div>', unsafe_allow_html=True)
    
    # Check if documents are added
    if not st.session_state.documents_added:
        stats = st.session_state.rag_pipeline.vector_store.get_document_stats()
        if stats['total_documents'] == 0:
            st.warning("Please add some documents first in the 'Add Documents' section.")
            return
    
    # Question input
    question = st.text_input(
        "Enter your question:",
        placeholder="What would you like to know about your documents?"
    )
    
    # Advanced options
    with st.expander("Advanced Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            top_k = st.slider("Number of documents to retrieve", 1, 10, RAGConfig.TOP_K_DOCUMENTS)
            show_context = st.checkbox("Show retrieved context", value=True)
        
        with col2:
            explain_process = st.checkbox("Explain RAG process", value=False)
            similarity_threshold = st.slider("Similarity threshold", 0.0, 1.0, RAGConfig.SIMILARITY_THRESHOLD)
    
    if question and st.button("Ask Question", type="primary"):
        ask_question(question, top_k, show_context, explain_process, similarity_threshold)
    
    # Show query history
    if st.session_state.query_history:
        st.markdown('<div class="sub-header">Query History</div>', unsafe_allow_html=True)
        
        for i, query in enumerate(reversed(st.session_state.query_history[-5:])):  # Show last 5 queries
            with st.expander(f"Q: {query['question'][:50]}..."):
                st.write(f"**Answer:** {query['answer']}")
                st.write(f"**Processing Time:** {query['processing_time']:.3f} seconds")
                st.write(f"**Retrieved Documents:** {query['num_documents_retrieved']}")

def ask_question(question, top_k, show_context, explain_process, similarity_threshold):
    """Process a question through RAG"""
    
    with st.spinner("Thinking..."):
        try:
            # Update config temporarily
            original_top_k = RAGConfig.TOP_K_DOCUMENTS
            original_threshold = RAGConfig.SIMILARITY_THRESHOLD
            
            RAGConfig.TOP_K_DOCUMENTS = top_k
            RAGConfig.SIMILARITY_THRESHOLD = similarity_threshold
            
            # Ask question
            response = st.session_state.rag_pipeline.query(
                question,
                top_k=top_k,
                include_context=show_context,
                explain_process=explain_process
            )
            
            # Restore config
            RAGConfig.TOP_K_DOCUMENTS = original_top_k
            RAGConfig.SIMILARITY_THRESHOLD = original_threshold
            
            # Display answer
            st.markdown('<div class="sub-header">Answer</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="success-box">{response["answer"]}</div>', unsafe_allow_html=True)
            
            # Show metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Documents Retrieved", response['num_documents_retrieved'])
            
            with col2:
                st.metric("Retrieval Time", f"{response['retrieval_time']:.3f}s")
            
            with col3:
                st.metric("Generation Time", f"{response['generation_time']:.3f}s")
            
            # Show retrieved documents
            if response['retrieved_documents']:
                st.markdown('<div class="sub-header">Retrieved Documents</div>', unsafe_allow_html=True)
                
                for i, doc in enumerate(response['retrieved_documents']):
                    with st.expander(f"Document {i+1} (Score: {doc['similarity_score']:.3f})"):
                        st.write(doc['text'])
                        st.json(doc['metadata'])
            
            # Show context if requested
            if show_context and response['context_used']:
                st.markdown('<div class="sub-header">Context Used</div>', unsafe_allow_html=True)
                st.text_area("Context", response['context_used'], height=200)
            
            # Show process explanation if requested
            if explain_process and 'process_explanation' in response:
                st.markdown('<div class="sub-header">RAG Process Explanation</div>', unsafe_allow_html=True)
                
                for step, details in response['process_explanation'].items():
                    st.write(f"**{step.replace('_', ' ').title()}**: {details['description']}")
            
            # Add to history
            st.session_state.query_history.append(response)
            
        except Exception as e:
            st.error(f"Error processing question: {str(e)}")

def show_analytics_page():
    """Show analytics and statistics"""
    
    st.markdown('<div class="sub-header">📊 Analytics Dashboard</div>', unsafe_allow_html=True)
    
    if not st.session_state.rag_pipeline:
        st.warning("RAG pipeline not initialized.")
        return
    
    # Get statistics
    stats = st.session_state.rag_pipeline.get_statistics()
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Documents", stats['vector_store_stats']['total_documents'])
    
    with col2:
        st.metric("Total Queries", stats['total_queries'])
    
    with col3:
        st.metric("Avg Retrieval Time", f"{stats['average_retrieval_time']:.3f}s")
    
    with col4:
        st.metric("Avg Generation Time", f"{stats['average_generation_time']:.3f}s")
    
    # Vector store statistics
    if stats['vector_store_stats']['total_documents'] > 0:
        st.markdown('<div class="sub-header">Document Statistics</div>', unsafe_allow_html=True)
        
        vs_stats = stats['vector_store_stats']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Average Document Length", f"{vs_stats['avg_document_length']:.0f} chars")
            st.metric("Min Document Length", f"{vs_stats['min_document_length']} chars")
        
        with col2:
            st.metric("Max Document Length", f"{vs_stats['max_document_length']} chars")
            st.metric("Total Text Length", f"{vs_stats['total_text_length']} chars")
    
    # Query performance over time
    if st.session_state.query_history:
        st.markdown('<div class="sub-header">Query Performance</div>', unsafe_allow_html=True)
        
        # Create performance chart
        df = pd.DataFrame([
            {
                'Query': i + 1,
                'Retrieval Time': query['retrieval_time'],
                'Generation Time': query['generation_time'],
                'Total Time': query['processing_time'],
                'Documents Retrieved': query['num_documents_retrieved']
            }
            for i, query in enumerate(st.session_state.query_history)
        ])
        
        # Time chart
        fig = px.line(df, x='Query', y=['Retrieval Time', 'Generation Time', 'Total Time'],
                      title='Query Performance Over Time')
        st.plotly_chart(fig, use_container_width=True)
        
        # Documents retrieved chart
        fig2 = px.bar(df, x='Query', y='Documents Retrieved',
                      title='Documents Retrieved per Query')
        st.plotly_chart(fig2, use_container_width=True)
    
    # Model information
    st.markdown('<div class="sub-header">Model Configuration</div>', unsafe_allow_html=True)
    
    model_info = {
        'Embedding Model': stats['models']['embedding_model'],
        'Generation Model': stats['models']['generation_model'],
        'Embedding Dimension': stats['vector_store_stats']['embedding_dimension'],
        'Chunk Size': RAGConfig.CHUNK_SIZE,
        'Top K Documents': RAGConfig.TOP_K_DOCUMENTS,
        'Similarity Threshold': RAGConfig.SIMILARITY_THRESHOLD
    }
    
    st.json(model_info)

def show_how_rag_works_page():
    """Show detailed explanation of how RAG works"""
    
    st.markdown('<div class="sub-header">ℹ️ How RAG Works</div>', unsafe_allow_html=True)
    
    # RAG overview
    st.markdown("""
    <div class="info-box">
    <h3>RAG Overview</h3>
    <p><strong>Retrieval-Augmented Generation (RAG)</strong> is a technique that enhances large language models by providing them with relevant external knowledge.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Step-by-step process
    st.markdown("## The RAG Process")
    
    # Step 1
    st.markdown("### 1. Document Ingestion")
    st.markdown("""
    - Documents are loaded from various sources (files, URLs, etc.)
    - Text is cleaned and preprocessed
    - Documents are split into smaller chunks (typically 256-512 tokens)
    - Each chunk is converted to a numerical vector (embedding) using a specialized model
    """)
    
    # Step 2
    st.markdown("### 2. Vector Storage")
    st.markdown("""
    - Embeddings are stored in a vector database (we use FAISS)
    - The database allows for fast similarity search
    - Each embedding is associated with its original text and metadata
    """)
    
    # Step 3
    st.markdown("### 3. Query Processing")
    st.markdown("""
    - User's question is converted to an embedding using the same model
    - The system searches for similar embeddings in the database
    - Top-k most similar documents are retrieved based on cosine similarity
    """)
    
    # Step 4
    st.markdown("### 4. Answer Generation")
    st.markdown("""
    - Retrieved documents are combined into a context
    - The question and context are fed to a language model
    - The model generates an answer based on the provided context
    """)
    
    # Visual representation
    st.markdown("## RAG Architecture")
    
    # Create a simple flow diagram
    st.markdown("""
    ```
    Documents → Chunking → Embedding → Vector DB
                                          ↓
    User Query → Embedding → Similarity Search → Top-K Documents
                                          ↓
    Question + Context → Language Model → Answer
    ```
    """)
    
    # Benefits
    st.markdown("## Benefits of RAG")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Advantages:**
        - ✅ Provides up-to-date information
        - ✅ Reduces hallucinations
        - ✅ Allows domain-specific knowledge
        - ✅ Transparent and explainable
        """)
    
    with col2:
        st.markdown("""
        **Use Cases:**
        - 📚 Document Q&A
        - 🏢 Corporate knowledge bases
        - 🔬 Research assistance
        - 📖 Educational content
        """)
    
    # Technical details
    st.markdown("## Technical Implementation")
    
    with st.expander("Embedding Models"):
        st.markdown("""
        - **sentence-transformers/all-MiniLM-L6-v2**: Fast and efficient embedding model
        - Converts text to 384-dimensional vectors
        - Trained on large corpus for general-purpose similarity
        """)
    
    with st.expander("Vector Search"):
        st.markdown("""
        - **FAISS (Facebook AI Similarity Search)**: High-performance vector database
        - Uses inner product for cosine similarity
        - Supports fast approximate nearest neighbor search
        """)
    
    with st.expander("Generation Models"):
        st.markdown("""
        - **google/flan-t5-base**: Instruction-tuned T5 model
        - Good balance between size and performance
        - Designed for question-answering tasks
        """)
    
    # Performance considerations
    st.markdown("## Performance Considerations")
    
    st.markdown("""
    <div class="info-box">
    <h4>Optimization Tips:</h4>
    <ul>
        <li><strong>Chunk Size</strong>: Balance between context and precision (256-512 tokens)</li>
        <li><strong>Retrieval Count</strong>: More documents = better context but slower processing</li>
        <li><strong>Similarity Threshold</strong>: Filter out irrelevant documents</li>
        <li><strong>Model Selection</strong>: Balance between accuracy and speed</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
