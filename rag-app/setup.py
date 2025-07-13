#!/usr/bin/env python3
"""
Setup script for the RAG Learning Application.
This script helps you set up the environment and install dependencies.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description=""):
    """Run a shell command and handle errors"""
    if description:
        print(f"📦 {description}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Success!")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8 or higher.")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_pip():
    """Check if pip is available"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=True)
        print("✅ pip is available")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip is not available")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    # Update pip first
    print("Updating pip...")
    if not run_command(f"{sys.executable} -m pip install --upgrade pip"):
        print("⚠️  Warning: Could not update pip")
    
    # Install requirements
    print("Installing requirements...")
    command = f"{sys.executable} -m pip install -r {requirements_file}"
    
    if run_command(command, "Installing dependencies from requirements.txt"):
        print("✅ All dependencies installed successfully!")
        return True
    else:
        print("❌ Failed to install some dependencies")
        return False

def create_virtual_environment():
    """Create a virtual environment"""
    venv_path = Path(__file__).parent / "venv"
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("📦 Creating virtual environment...")
    
    try:
        import venv
        venv.create(venv_path, with_pip=True)
        print("✅ Virtual environment created successfully!")
        
        # Activation instructions
        if platform.system() == "Windows":
            activate_script = venv_path / "Scripts" / "activate.bat"
        else:
            activate_script = venv_path / "bin" / "activate"
        
        print(f"💡 To activate the virtual environment, run:")
        print(f"   source {activate_script}")
        
        return True
    except Exception as e:
        print(f"❌ Error creating virtual environment: {e}")
        return False

def download_models():
    """Download required models"""
    print("📦 Pre-downloading models...")
    
    # Create a simple script to download models
    download_script = """
import os
os.environ['TRANSFORMERS_CACHE'] = './models_cache'

try:
    from sentence_transformers import SentenceTransformer
    print("Downloading embedding model...")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    print("✅ Embedding model downloaded")
except Exception as e:
    print(f"❌ Error downloading embedding model: {e}")

try:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    print("Downloading generation model...")
    tokenizer = AutoTokenizer.from_pretrained('google/flan-t5-base')
    model = AutoModelForSeq2SeqLM.from_pretrained('google/flan-t5-base')
    print("✅ Generation model downloaded")
except Exception as e:
    print(f"❌ Error downloading generation model: {e}")

print("🎉 Model download complete!")
"""
    
    try:
        exec(download_script)
        return True
    except Exception as e:
        print(f"❌ Error downloading models: {e}")
        return False

def test_installation():
    """Test the installation"""
    print("🧪 Testing installation...")
    
    try:
        # Test imports
        print("Testing imports...")
        
        import torch
        print("✅ PyTorch imported")
        
        import transformers
        print("✅ Transformers imported")
        
        import sentence_transformers
        print("✅ Sentence Transformers imported")
        
        import streamlit
        print("✅ Streamlit imported")
        
        import faiss
        print("✅ FAISS imported")
        
        print("🎉 All imports successful!")
        
        # Test basic functionality
        print("\nTesting basic functionality...")
        
        # Run the test function from quick_start
        current_dir = Path(__file__).parent
        test_script = current_dir / "quick_start.py"
        
        if test_script.exists():
            command = f"{sys.executable} {test_script} test"
            if run_command(command, "Running component tests"):
                print("✅ All tests passed!")
                return True
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 RAG Learning Application Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check pip
    if not check_pip():
        sys.exit(1)
    
    # Ask user if they want to create virtual environment
    create_venv = input("\n🤔 Do you want to create a virtual environment? (y/N): ").lower().strip()
    
    if create_venv in ['y', 'yes']:
        if not create_virtual_environment():
            print("⚠️  Continuing without virtual environment...")
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed due to dependency installation errors")
        sys.exit(1)
    
    # Download models
    download_models_choice = input("\n🤔 Do you want to pre-download models? (Y/n): ").lower().strip()
    
    if download_models_choice not in ['n', 'no']:
        download_models()
    
    # Test installation
    test_choice = input("\n🤔 Do you want to test the installation? (Y/n): ").lower().strip()
    
    if test_choice not in ['n', 'no']:
        if test_installation():
            print("\n🎉 Setup completed successfully!")
        else:
            print("\n⚠️  Setup completed but some tests failed")
    else:
        print("\n✅ Setup completed!")
    
    # Show usage instructions
    print("\n📚 Usage Instructions:")
    print("=" * 20)
    print("1. 🌐 Web Interface:")
    print("   streamlit run app.py")
    print()
    print("2. 🖥️  Command Line:")
    print("   python quick_start.py")
    print()
    print("3. 🧪 Run Tests:")
    print("   python quick_start.py test")
    print()
    print("📖 Check README.md for detailed documentation!")

if __name__ == "__main__":
    main()
