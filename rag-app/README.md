# 🤖 RAG Learning Application

A comprehensive **Retrieval-Augmented Generation (RAG)** implementation using Hugging Face models, designed to help you understand how RAG works from the ground up!

## 🚀 **Quick Start**

```bash
git clone <your-repo-url>
cd ml-exp/rag-app
pip install -r requirements.txt
streamlit run app.py
```

📖 **New to this repo?** Check [SETUP.md](SETUP.md) for detailed setup instructions.

## 🎯 What is RAG?

RAG (Retrieval-Augmented Generation) is a powerful AI technique that combines:
1. **🔍 Information Retrieval**: Finding relevant documents/passages from a knowledge base
2. **🤖 Text Generation**: Using an LLM to generate answers based on retrieved context

## 🔄 How RAG Works

```
User Query → [Embedding] → Vector Search → Relevant Documents → LLM → Final Answer
```

### The Process:
1. **📄 Document Ingestion**: Documents are split into chunks and converted to embeddings
2. **🗃️ Vector Storage**: Embeddings are stored in a vector database for similarity search
3. **🔍 Query Processing**: User query is converted to an embedding
4. **📊 Retrieval**: Most similar document chunks are retrieved using cosine similarity
5. **🤖 Generation**: Retrieved context + query are fed to an LLM for answer generation

## 📁 Project Structure

```
rag-app/
├── 🌐 app.py              # Main Streamlit web application
├── 🔄 rag_pipeline.py     # Core RAG implementation
├── 📚 document_loader.py  # Document processing utilities
├── 🗃️ vector_store.py     # Vector database implementation
├── ⚙️ config.py          # Configuration settings
├── 📦 requirements.txt    # Python dependencies
├── 🚀 setup.py           # Easy setup script
├── 💻 quick_start.py     # Command-line interface
├── 🧪 test_basic.py      # Basic concept demonstration
├── 📄 sample_documents/  # Sample documents for testing
├── 🔧 run_app.sh         # App launcher script
└── 📖 README.md          # This file
```

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
cd rag-app
python setup.py
```

### Option 2: Manual Setup
```bash
cd rag-app
pip install -r requirements.txt
```

## 🎮 Usage Options

### 1. 🌐 Web Interface (Recommended for Learning)
```bash
streamlit run app.py
# Or use the launcher script
./run_app.sh
```

### 2. 💻 Command Line Interface
```bash
python quick_start.py
```

### 3. 🧪 Basic Concept Test (No Dependencies)
```bash
python test_basic.py
```

## ✨ Features

- 📚 **Document Upload**: Support for PDF, TXT, DOCX, MD files
- 🔍 **Smart Retrieval**: Vector similarity search with FAISS
- 🤖 **Question Answering**: Context-aware answer generation
- 🌐 **Interactive Web UI**: Beautiful Streamlit interface
- 📊 **Analytics Dashboard**: Performance metrics and visualizations
- 🔬 **Process Explanation**: Step-by-step RAG process breakdown
- 📖 **Educational Content**: Learn how each component works
- 🎯 **Sample Documents**: Pre-loaded ML/AI content to get started

## 🤖 Models Used

- **🔤 Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
  - Converts text to 384-dimensional vectors
  - Fast and efficient for similarity search
  
- **🧠 Language Model**: `google/flan-t5-base`
  - Instruction-tuned for question answering
  - Good balance of performance and speed

## 🎓 Learning Objectives

After using this app, you'll understand:

### 📚 Document Processing
- How to load and preprocess various document formats
- Text chunking strategies and best practices
- Metadata management for better retrieval

### 🔢 Embeddings & Vector Search
- How text is converted to numerical vectors
- Similarity search algorithms and optimization
- Vector database operations and indexing

### 🤖 Language Model Integration
- How to use pre-trained Hugging Face models
- Prompt engineering for RAG applications
- Context window management and optimization

### 🔄 Complete RAG Pipeline
- End-to-end workflow from query to answer
- Performance optimization techniques
- Error handling and edge case management

### 📊 Evaluation & Metrics
- How to measure RAG system performance
- Retrieval quality assessment
- Generation quality evaluation

## 🛠️ Technical Stack

- **🐍 Python 3.8+**: Core programming language
- **🤗 Hugging Face Transformers**: Pre-trained models
- **🔍 FAISS**: Vector similarity search
- **🌐 Streamlit**: Web interface
- **📊 Plotly**: Data visualization
- **🧮 NumPy/Pandas**: Data manipulation

## 📖 Documentation

### 🏠 Web Interface Pages:
- **Home**: Overview and quick start guide
- **Add Documents**: Upload and process documents
- **Ask Questions**: Interactive Q&A with explanations
- **Analytics**: Performance metrics and visualizations
- **How RAG Works**: Educational content and explanations

### 💻 Command Line:
- Interactive Q&A session
- Real-time performance metrics
- Step-by-step process explanation
- Query history and statistics

## 🎯 Example Use Cases

1. **📚 Educational**: Learn ML/AI concepts from uploaded textbooks
2. **🏢 Corporate**: Query company documentation and policies
3. **🔬 Research**: Ask questions about research papers
4. **💼 Legal**: Search through contracts and legal documents
5. **🩺 Healthcare**: Query medical literature and guidelines

## 🔧 Configuration

Customize the RAG system by modifying `config.py`:

```python
# Model settings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GENERATION_MODEL = "google/flan-t5-base"

# Processing settings
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
TOP_K_DOCUMENTS = 3

# Performance settings
SIMILARITY_THRESHOLD = 0.5
MAX_GENERATION_LENGTH = 256
```

## 🚀 Next Steps

1. **🎮 Try the Demo**: Start with the web interface
2. **📚 Upload Documents**: Add your own documents
3. **🔍 Experiment**: Try different queries and settings
4. **📊 Analyze**: Check the analytics dashboard
5. **🛠️ Customize**: Modify models and parameters
6. **🔬 Learn**: Explore the code and documentation

## 🤝 Contributing

Feel free to:
- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🔧 Submit pull requests

## 📚 Further Learning

- **📖 RAG Paper**: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
- **🤗 Hugging Face Docs**: Transformers and Datasets libraries
- **🔍 FAISS Docs**: Vector similarity search
- **🌐 Streamlit Docs**: Web app framework

---

**🎉 Happy Learning!** This RAG application is designed to be your comprehensive guide to understanding and implementing Retrieval-Augmented Generation systems.
