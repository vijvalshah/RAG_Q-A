#!/usr/bin/env python3
"""
Setup script for RAG-Powered Multi-Agent Q&A System
"""
import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def print_header(text):
    """Print a header with decoration."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_step(text):
    """Print a step with decoration."""
    print(f"\n>> {text}")

def check_python_version():
    """Check if Python version is sufficient."""
    print_step("Checking Python version...")
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print(f"Python 3.8 or higher is required. You have {python_version.major}.{python_version.minor}.")
        return False
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro} - OK")
    return True

def create_env_file():
    """Create .env file for the Google API key."""
    print_step("Setting up environment file...")
    env_file = Path('.env')
    dotenv_file = Path('dotenv_file')
    example_file = Path('env.example')
    
    if env_file.exists():
        print(f"The {env_file} file already exists.")
        return
    
    if dotenv_file.exists():
        print(f"The {dotenv_file} file exists. Renaming to .env")
        shutil.copy(dotenv_file, env_file)
        return
    
    if example_file.exists():
        print(f"Creating .env file from example...")
        shutil.copy(example_file, env_file)
    else:
        print("Creating new .env file...")
        with open(env_file, 'w') as f:
            f.write("# Google Gemini API Key\n")
            f.write("GOOGLE_API_KEY=your_google_api_key_here\n\n")
            f.write("# Model configuration\n")
            f.write("# GEMINI_MODEL_NAME=gemini-1.5-pro\n")
    
    print("Please edit the .env file to add your Google Gemini API key.")

def install_dependencies():
    """Install required packages."""
    print_step("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False

def create_directories():
    """Create required directories if they don't exist."""
    print_step("Creating required directories...")
    dirs = ["data", "vector_store"]
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
        print(f"Directory '{dir_name}' is ready.")

def check_sample_documents():
    """Check if sample documents exist."""
    print_step("Checking sample documents...")
    data_dir = Path("data")
    sample_files = list(data_dir.glob("*.txt"))
    if not sample_files:
        print("No sample documents found. Make sure to add some text files to the data directory.")
    else:
        print(f"Found {len(sample_files)} sample document(s).")

def main():
    """Main setup function."""
    print_header("RAG-Powered Multi-Agent Q&A System Setup")
    
    if not check_python_version():
        sys.exit(1)
    
    create_env_file()
    create_directories()
    
    if install_dependencies():
        check_sample_documents()
        
        print_header("Setup Complete!")
        print("""
Next steps:
1. Edit the .env file to add your Google Gemini API key
2. Initialize the vector store: python main.py --init
3. Run the application:
   - CLI mode: python main.py --interactive
   - Web UI: python run_webapp.py OR streamlit run streamlit_app.py
        """)
    else:
        print_header("Setup Incomplete")
        print("Please resolve the dependencies issues and try again.")

if __name__ == "__main__":
    main() 