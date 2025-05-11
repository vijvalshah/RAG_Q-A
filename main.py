#!/usr/bin/env python3
import os
import argparse
import logging
import sys
import shutil
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

from src.document_loader import DocumentLoader
from src.vector_store import VectorStore
from src.llm_integration import LLMIntegration
from src.agent import Agent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to load environment variables from .env or dotenv_file
env_loaded = load_dotenv(find_dotenv())
if not env_loaded:
    # Try loading from dotenv_file as backup
    if os.path.exists("dotenv_file"):
        load_dotenv("dotenv_file")
        logger.info("Loaded environment variables from dotenv_file")
    else:
        logger.warning("No .env file found. Please create one with your Google Gemini API key.")

# Check if Google API key is set
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    logger.warning("GOOGLE_API_KEY not found in environment variables.")
    logger.warning("Please add GOOGLE_API_KEY=your_google_api_key_here to your .env file.")

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
VECTOR_STORE_DIR = os.path.join(BASE_DIR, "vector_store")


def initialize_vector_store():
    """Initialize the vector store with documents."""
    # Create vector_store directory if it doesn't exist
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    
    # Load documents
    logger.info("Loading documents from %s", DATA_DIR)
    loader = DocumentLoader(DATA_DIR)
    documents = loader.load_documents()
    
    # Initialize Vector Store
    logger.info("Creating vector store")
    vector_store = VectorStore()
    vector_store.create_vector_store(documents)
    
    # Save Vector Store
    logger.info("Saving vector store to %s", VECTOR_STORE_DIR)
    vector_store.save_vector_store(VECTOR_STORE_DIR)
    
    return vector_store


def load_vector_store():
    """Load the vector store from disk."""
    if not os.path.exists(VECTOR_STORE_DIR):
        logger.error("Vector store directory not found. Please initialize the vector store first.")
        return None
    
    logger.info("Loading vector store from %s", VECTOR_STORE_DIR)
    vector_store = VectorStore()
    vector_store.load_vector_store(VECTOR_STORE_DIR)
    
    return vector_store


def initialize_agent():
    """Initialize the agent with vector store and LLM."""
    # Check if Google API key is available
    if not os.getenv("GOOGLE_API_KEY"):
        logger.error("GOOGLE_API_KEY not found in environment variables. Cannot initialize LLM.")
        return None
    
    # Check if vector store exists, if not initialize it
    if not os.path.exists(VECTOR_STORE_DIR):
        vector_store = initialize_vector_store()
    else:
        vector_store = load_vector_store()
    
    if not vector_store:
        return None
    
    try:
        # Initialize LLM
        logger.info("Initializing LLM with Google Gemini")
        llm = LLMIntegration()
        
        # Initialize Agent
        logger.info("Initializing Agent")
        agent = Agent(vector_store, llm)
        
        return agent
    except Exception as e:
        logger.error(f"Error initializing agent: {e}")
        return None


def process_query(agent, query):
    """Process a query using the agent."""
    if not agent:
        logger.error("Agent not initialized")
        return None
    
    logger.info("Processing query: %s", query)
    result = agent.process_query(query)
    
    return result


def display_result(result):
    """Display the result in the CLI."""
    if not result:
        return
    
    print("\n" + "="*50)
    print(f"Query: {result['query']}")
    print(f"Workflow: {result['workflow'].capitalize()}")
    print("="*50)
    
    print("\nAnswer:")
    print(result["answer"])
    
    if result["workflow"] == "rag" and "retrieved_docs" in result:
        print("\nRetrieved Documents:")
        for i, doc in enumerate(result["retrieved_docs"]):
            print(f"\nDocument {i+1} (Relevance: {doc['relevance_score']:.4f}):")
            print("-"*30)
            print(doc["content"])
    
    if result["workflow"] == "calculator" and "result" in result:
        calc_result = result["result"]
        if calc_result["status"] == "success":
            print("\nCalculation Details:")
            print(f"Expression: {calc_result['expression']}")
            print(f"Result: {calc_result['value']}")
    
    if result["workflow"] == "dictionary" and "result" in result:
        dict_result = result["result"]
        if dict_result["status"] == "success":
            print("\nDefinition Details:")
            print(f"Term: {dict_result['term']}")
            if "note" in dict_result:
                print(f"Note: {dict_result['note']}")
    
    print("\n" + "="*50 + "\n")


def clean_vector_store():
    """Clean the vector store to manage disk space."""
    if not os.path.exists(VECTOR_STORE_DIR):
        logger.error("Vector store directory not found.")
        return False
    
    try:
        # Create a backup first
        backup_dir = os.path.join(BASE_DIR, f"vector_store_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        logger.info(f"Creating backup of vector store at {backup_dir}")
        shutil.copytree(VECTOR_STORE_DIR, backup_dir)
        
        # Calculate space used
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(VECTOR_STORE_DIR):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        
        # Remove the vector store
        logger.info("Cleaning vector store...")
        shutil.rmtree(VECTOR_STORE_DIR)
        os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
        
        logger.info(f"Vector store cleaned. Freed approximately {total_size / (1024*1024):.2f} MB.")
        logger.info(f"Backup saved at {backup_dir}")
        logger.info("Use 'python main.py --init' to reinitialize the vector store.")
        
        return True
    except Exception as e:
        logger.error(f"Error cleaning vector store: {e}")
        return False


def display_disk_usage():
    """Display disk usage information for the vector store and data directories."""
    print("\nDisk Usage Information:")
    
    # Check vector store directory
    if os.path.exists(VECTOR_STORE_DIR):
        vector_store_size = 0
        for dirpath, dirnames, filenames in os.walk(VECTOR_STORE_DIR):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                vector_store_size += os.path.getsize(fp)
        
        print(f"Vector Store: {vector_store_size / (1024*1024):.2f} MB")
    else:
        print("Vector Store: Not initialized")
    
    # Check data directory
    if os.path.exists(DATA_DIR):
        data_size = 0
        num_files = 0
        for dirpath, dirnames, filenames in os.walk(DATA_DIR):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                data_size += os.path.getsize(fp)
                num_files += 1
        
        print(f"Data Directory: {data_size / (1024*1024):.2f} MB ({num_files} files)")
    else:
        print("Data Directory: Not found")
    
    # Display Python packages (estimated)
    try:
        import pkg_resources
        packages_size = 0
        for package in pkg_resources.working_set:
            package_path = os.path.dirname(package.location)
            if os.path.exists(package_path):
                pkg_size = 0
                for dirpath, dirnames, filenames in os.walk(package_path):
                    for f in filenames:
                        try:
                            fp = os.path.join(dirpath, f)
                            pkg_size += os.path.getsize(fp)
                        except (OSError, FileNotFoundError):
                            pass
                if "langchain" in package.project_name or "google" in package.project_name or "transformers" in package.project_name:
                    print(f"  - {package.project_name}: {pkg_size / (1024*1024):.2f} MB")
                packages_size += pkg_size
        
        print(f"Total Python Packages: {packages_size / (1024*1024):.2f} MB (estimate)")
    except Exception as e:
        print(f"Could not estimate package sizes: {e}")


def main():
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(description="RAG-Powered Multi-Agent Q&A System")
    parser.add_argument("--init", action="store_true", help="Initialize the vector store")
    parser.add_argument("--query", type=str, help="Query to process")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--check-env", action="store_true", help="Check environment setup")
    parser.add_argument("--clean-vector-store", action="store_true", help="Clean the vector store to manage disk space")
    parser.add_argument("--disk-usage", action="store_true", help="Display disk usage information")
    
    args = parser.parse_args()
    
    if args.check_env:
        # Display environment information
        print("\nEnvironment Check:")
        print(f"Google API Key: {'Set' if os.getenv('GOOGLE_API_KEY') else 'Not Set'}")
        print(f"Data Directory: {os.path.exists(DATA_DIR)}")
        print(f"Vector Store: {'Exists' if os.path.exists(VECTOR_STORE_DIR) else 'Not Found'}")
        print(f"Python Version: {sys.version}")
        return
    
    if args.clean_vector_store:
        if input("This will delete your vector store. A backup will be created. Continue? (y/n): ").lower() == 'y':
            clean_vector_store()
        else:
            print("Vector store cleaning aborted.")
        return
    
    if args.disk_usage:
        display_disk_usage()
        return
    
    if args.init:
        initialize_vector_store()
        return
    
    # Initialize agent
    agent = initialize_agent()
    if not agent:
        print("\nERROR: Could not initialize agent. Please check your environment setup.")
        print("1. Make sure you have set your GOOGLE_API_KEY in the .env file")
        print("2. Ensure the vector store is initialized (run with --init)")
        print("3. Check that all dependencies are installed")
        print("\nRun with --check-env to verify your environment setup")
        return
    
    if args.query:
        # Process a single query
        result = process_query(agent, args.query)
        display_result(result)
        return
    
    if args.interactive:
        # Run in interactive mode
        print("\nRAG-Powered Multi-Agent Q&A System")
        print("Type 'exit' or 'quit' to exit\n")
        
        while True:
            try:
                query = input("Enter your question: ")
                if query.lower() in ["exit", "quit"]:
                    break
                
                if not query:
                    continue
                
                result = process_query(agent, query)
                display_result(result)
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error processing query: {e}")
    
    else:
        # Show help if no action specified
        parser.print_help()


if __name__ == "__main__":
    main() 