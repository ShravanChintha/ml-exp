# 🚀 Quick Setup Guide

This guide helps you set up the RAG Learning Application after cloning the repository.

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## ⚡ Quick Start

### 1. Clone and Navigate
```bash
git clone <your-repo-url>
cd ml-exp/rag-app
```

### 2. Set Up Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
# Web Interface (Recommended)
streamlit run app.py

# Or Command Line Interface
python quick_start.py

# Or Basic Demo (no ML models)
python test_basic.py
```

## 🔧 Automated Setup

For easier setup, use the automated setup script:
```bash
python setup.py
```

## 🎯 First Steps

1. **Web Interface**: Open your browser to the Streamlit URL (usually http://localhost:8501)
2. **Add Documents**: Upload some documents in the "Add Documents" page
3. **Ask Questions**: Try asking questions about your documents
4. **Explore Analytics**: Check the analytics dashboard
5. **Learn**: Read the "How RAG Works" section

## 📚 Sample Documents

The app includes sample documents about machine learning, deep learning, and NLP. These are automatically loaded when you first run the application.

## 🐛 Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Model Download Issues**: Models are downloaded automatically on first run. This may take a few minutes.

3. **Performance Issues**: 
   - The app uses CPU by default for compatibility
   - First-time model loading takes longer
   - Subsequent runs will be faster

### Getting Help:

- Check the debug tools: `python debug_retrieval.py`
- Run tests: `python quick_start.py test`
- Check the detailed README.md for more information

## 🎓 Learning Resources

- **README.md**: Comprehensive documentation
- **How RAG Works**: Educational content in the web app
- **Code Comments**: All code is well-documented for learning

---

**Happy Learning!** 🎉
