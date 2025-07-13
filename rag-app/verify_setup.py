#!/usr/bin/env python3
"""
Post-clone verification script
This script verifies that the RAG app can be set up properly after git clone.
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} not supported. Need Python 3.8+")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_required_files():
    """Check if all required files are present"""
    required_files = [
        'requirements.txt',
        'app.py',
        'rag_pipeline.py',
        'vector_store.py',
        'document_loader.py',
        'config.py',
        'README.md',
        'SETUP.md'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files present")
    return True

def check_sample_documents():
    """Check if sample documents exist"""
    sample_dir = Path("sample_documents")
    if not sample_dir.exists():
        print("⚠️  Sample documents directory missing")
        return False
    
    sample_files = list(sample_dir.glob("*.txt"))
    if len(sample_files) < 3:
        print(f"⚠️  Only {len(sample_files)} sample documents found")
        return False
    
    print(f"✅ {len(sample_files)} sample documents found")
    return True

def test_imports():
    """Test if the app can import without installing dependencies"""
    try:
        # Test config import
        sys.path.insert(0, '.')
        from config import RAGConfig
        print("✅ Config imports successfully")
        
        # Test if we can read requirements
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
            req_lines = [line.strip() for line in requirements.split('\n') if line.strip() and not line.startswith('#')]
            print(f"✅ Requirements file has {len(req_lines)} dependencies")
        
        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def simulate_fresh_install():
    """Simulate what happens on a fresh git clone"""
    print("🧪 Simulating fresh install scenario...")
    
    # Check if virtual environment would be creatable
    try:
        import venv
        print("✅ venv module available")
    except ImportError:
        print("⚠️  venv module not available")
    
    # Check if pip is available
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ pip available")
        else:
            print("❌ pip not available")
            return False
    except Exception:
        print("❌ pip check failed")
        return False
    
    return True

def main():
    """Main verification function"""
    print("🔍 Post-Clone Verification for RAG Learning App")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Files", check_required_files),
        ("Sample Documents", check_sample_documents),
        ("Basic Imports", test_imports),
        ("Install Prerequisites", simulate_fresh_install)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"\n🔍 Checking {name}...")
        if check_func():
            passed += 1
        else:
            print(f"   ⚠️  {name} check had issues")
    
    print(f"\n📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 Repository is ready for cloning and setup!")
        print("\n📋 Next steps for users:")
        print("1. pip install -r requirements.txt")
        print("2. streamlit run app.py")
    elif passed >= total - 1:
        print("✅ Repository is mostly ready. Minor issues detected.")
        print("💡 Users should follow SETUP.md for installation")
    else:
        print("❌ Repository has significant issues")
        print("🔧 Please fix the issues before committing")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
