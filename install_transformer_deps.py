#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Installation script for Transformer-based Sehat Nabha
Installs all required dependencies for the application
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"\n[*] {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False)
        if result.returncode != 0:
            print(f"✗ {description} failed!")
            return False
        print(f"✓ {description} completed")
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("Sehat Nabha - Transformer Model Installation")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print(f"✗ Python 3.8+ is required (you have {sys.version_info.major}.{sys.version_info.minor})")
        return False
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    steps = [
        (f"{sys.executable} -m pip install --upgrade pip setuptools wheel", "Updating pip, setuptools, wheel"),
        (f"{sys.executable} -m pip install numpy pandas scikit-learn pyyaml", "Installing core dependencies"),
        (f"{sys.executable} -m pip install flask==3.0.0 flask-cors==4.0.0 gunicorn", "Installing Flask"),
        (f"{sys.executable} -m pip install torch>=2.0.0", "Installing PyTorch (this may take a few minutes)"),
        (f"{sys.executable} -m pip install transformers>=4.30.0", "Installing Transformers"),
        (f"{sys.executable} -m pip install sentence-transformers==2.2.2", "Installing Sentence Transformers"),
        (f"{sys.executable} -m pip install faiss-cpu==1.12.0", "Installing FAISS"),
        (f"{sys.executable} -m pip install Cython", "Installing Cython"),
    ]
    
    for cmd, description in steps:
        if not run_command(cmd, description):
            print("\n" + "=" * 60)
            print("✗ Installation failed!")
            print("=" * 60)
            return False
    
    print("\n" + "=" * 60)
    print("✓ All dependencies installed successfully!")
    print("=" * 60)
    
    print("\nNext steps:")
    print("1. Start the Python API server:")
    print("   python api_server.py")
    print("\n2. In another terminal, start the React frontend:")
    print("   npm run dev")
    print("\n3. Open your browser and navigate to http://localhost:3000")
    print("\nNote: On first run, the transformer models will be downloaded (~2GB)")
    print("This may take 5-10 minutes depending on your internet speed.")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
