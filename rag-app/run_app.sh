#!/bin/bash

# RAG Learning Application Launcher Script
# This script helps you run the RAG application

echo "🤖 RAG Learning Application Launcher"
echo "===================================="

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Found virtual environment, activating..."
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  No virtual environment found, using system Python"
fi

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
python -c "import streamlit, torch, transformers, sentence_transformers, faiss" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ All dependencies are installed"
else
    echo "❌ Some dependencies are missing"
    echo "🔧 Please run: python setup.py"
    exit 1
fi

# Check if we have documents
if [ ! -d "sample_documents" ]; then
    echo "⚠️  No sample documents found, creating sample documents..."
    mkdir -p sample_documents
fi

echo ""
echo "🚀 Starting RAG Learning Application..."
echo "📝 The app will open in your web browser"
echo "🛑 Press Ctrl+C to stop the application"
echo ""

# Run the Streamlit app
streamlit run app.py --server.address localhost --server.port 8501

echo ""
echo "👋 RAG Learning Application stopped"
