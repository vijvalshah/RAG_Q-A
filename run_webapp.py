#!/usr/bin/env python3
import os
import subprocess
import sys
import platform
import argparse

def run_app(lightweight=False):
    """Run the Streamlit web application."""
    try:
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                  "streamlit_app_light.py" if lightweight else "streamlit_app.py")
        
        # Check if script exists
        if not os.path.exists(script_path):
            print(f"Error: Could not find {script_path}")
            return False
        
        # Try to run the Streamlit app
        print(f"Starting {'lightweight' if lightweight else 'full'} RAG Q&A web interface...")
        process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", script_path])
        
        print("Streamlit app is running! Open your browser to view it.")
        print("Press Ctrl+C to stop the application")
        
        # Wait for the process to complete (or be interrupted)
        process.wait()
        return True
    
    except KeyboardInterrupt:
        print("\nStopping the application...")
        return True
    except Exception as e:
        print(f"\nError running Streamlit app: {e}")
        print("\nDo you have Streamlit installed? Try 'pip install streamlit'")
        return False

def main():
    """Main entry point for running the web application."""
    parser = argparse.ArgumentParser(description="Run the RAG Q&A Web Interface")
    parser.add_argument("--lightweight", action="store_true", help="Run the lightweight version without LLM generation (for when API quota is exceeded)")
    
    args = parser.parse_args()
    
    print("\nRAG-Powered Multi-Agent Q&A System")
    print("===================================")
    
    # Check if streamlit is installed
    try:
        import streamlit
        print(f"Streamlit version: {streamlit.__version__}")
    except ImportError:
        print("Streamlit is not installed. Installing...")
        subprocess.call([sys.executable, "-m", "pip", "install", "streamlit"])
        print("Streamlit installed. Continuing...")
    
    # Run the appropriate version
    if args.lightweight:
        print("\nStarting LIGHTWEIGHT mode (document retrieval only, no LLM generation)")
        run_app(lightweight=True)
    else:
        print("\nStarting FULL mode with LLM generation")
        # First try running the full version
        try:
            run_app(lightweight=False)
        except Exception as e:
            print(f"\nError running full version: {e}")
            # Ask if user wants to try lightweight version
            response = input("\nWould you like to try the lightweight version instead? (y/n): ")
            if response.lower() == 'y':
                run_app(lightweight=True)

if __name__ == "__main__":
    main() 