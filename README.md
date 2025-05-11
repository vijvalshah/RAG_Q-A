# RAG-Powered Multi-Agent Q&A System

A simple knowledge assistant that combines Retrieval-Augmented Generation (RAG) with an agentic workflow to answer questions based on document content and provide additional functionalities through specialized tools.

## Architecture

This system consists of the following components:

1. **Document Loader**: Loads text and PDF documents from the `data` directory, preprocesses them, and splits them into smaller chunks for indexing.

2. **Vector Store**: Creates and manages a FAISS vector index for efficient semantic search over document chunks.

3. **LLM Integration**: Interfaces with Google's Gemini models to generate natural language answers based on retrieved context.

4. **Tools**:
   - **Calculator Tool**: Performs mathematical calculations.
   - **Dictionary Tool**: Provides definitions using Wikipedia.

5. **Agent**: Orchestrates the workflow by:
   - Analyzing the query to determine appropriate routing
   - Executing the appropriate workflow (RAG, calculator, or dictionary)
   - Logging decisions and returning structured results

6. **User Interfaces**:
   - **CLI**: A command-line interface for interacting with the system.
   - **Web UI**: A Streamlit-based web interface with document upload capability.

## Key Design Choices

1. **Modular Architecture**: Each component is implemented as a separate class to promote maintainability and extensibility.

2. **FAISS for Vector Storage**: FAISS provides efficient similarity search for document retrieval.

3. **Agent-Based Routing**: The system uses keyword detection and pattern matching to route queries to the appropriate tool or the RAG pipeline.

4. **Transparent Workflow**: The system provides detailed information about the decision-making process and retrieved documents.

5. **HuggingFace Embeddings**: Using `sentence-transformers/all-MiniLM-L6-v2` as a lightweight but effective embedding model.

6. **Document Processing**: Support for both text (.txt) and PDF (.pdf) files with text preprocessing.

7. **User-Friendly UI**: Streamlit-based interface with document upload capability and interactive elements.

8. **Google Gemini Integration**: Uses Google's Gemini models for natural language generation.

## Features

- **Multi-Document Support**: Process and query both text and PDF documents.
- **Document Management**: Upload, view, and delete documents through the UI.
- **Text Preprocessing**: Clean and normalize text for better retrieval.
- **Multi-Agent Workflow**: Route queries to specialized tools or RAG pipeline.
- **Transparent Results**: View detailed information about the decision-making process.
- **Interactive CLI and Web UI**: Choose between command-line or web-based interaction.
- **Google Gemini LLM**: Leverage Google's powerful generative AI models.

## Setup and Installation

### For Windows Users: Easy Menu Interface

Double-click the `run_app.bat` file to launch a menu-driven interface that lets you:
- Install dependencies
- Initialize the vector store
- Run the CLI or Web UI
- Check your environment setup

No need to remember commands - just select the option you want from the menu!

### Quick Setup (All Platforms)

For a guided setup process, run:

```powershell
python setup.py
```

This will:
1. Check your Python version
2. Create a .env file for your API key
3. Create necessary directories
4. Install dependencies
5. Guide you through next steps

### Manual Setup

1. Clone the repository:
```powershell
git clone <repository-url>
cd rag_qa_system
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the project root directory with your Google Gemini API key:
```
GOOGLE_API_KEY=your_google_api_key_here
```

You can get a Google Gemini API key by:
- Visiting https://ai.google.dev/
- Creating a new project
- Enabling the Gemini API
- Creating an API key

## Optimizing Disk Space Usage

The project's dependencies can take up significant disk space. Here are recommendations for managing space efficiently:

### Using Virtual Environments

Always use a dedicated virtual environment to avoid polluting your global Python installation:

```powershell
# Create a virtual environment
python -m venv rag_env

# Activate it (Windows)
.\rag_env\Scripts\activate

# Activate it (Linux/Mac)
source rag_env/bin/activate

# Install dependencies inside the virtual environment
pip install -r requirements.txt
```

### Minimizing Package Footprint

1. **Use lightweight models**: We've selected the lightweight `all-MiniLM-L6-v2` embedding model to balance performance and disk usage.

2. **Selective dependencies**: Install only what you need:
   ```powershell
   # For CLI-only usage (no Streamlit)
   pip install -r requirements-minimal.txt
   ```

3. **Clean up unused packages**:
   ```powershell
   pip uninstall -y chromadb  # If not using ChromaDB
   ```

4. **Clean pip cache**:
   ```powershell
   pip cache purge
   ```

### Monitoring and Managing Vector Store Size

The vector store can grow large if you add many documents. Monitor the `vector_store` directory size:

1. **Periodically clear out old or unused indexes**:
   ```powershell
   # Back up critical documents first
   python main.py --clean-vector-store
   ```

2. **Compact the vector store** (requires maintenance restart)

## Usage

### Command-Line Interface

1. Initialize the vector store:
```powershell
python main.py --init
```

2. Process a single query:
```powershell
python main.py --query "What is artificial intelligence?"
```

3. Run in interactive mode:
```powershell
python main.py --interactive
```

4. Check your environment setup:
```powershell
python main.py --check-env
```

### Web Interface

There are two ways to run the web application in PowerShell:

1. Using the standalone script:
```powershell
python run_webapp.py
```

2. Running the Streamlit app directly:
```powershell
python -m streamlit run streamlit_app.py
```

Then, open your browser and navigate to the URL displayed in the terminal (typically http://localhost:8501).

## Examples

- **RAG Query**: "What are the key features of blockchain?"
- **Calculator**: "Calculate 25 * 4"
- **Dictionary**: "Define artificial intelligence"

## Data

The system comes with three sample documents:
1. A document about artificial intelligence
2. A document about cloud computing
3. A document about blockchain technology

You can add your own documents to the `data` directory (text files with `.txt` extension or PDF files with `.pdf` extension) or upload them through the web interface.

## Troubleshooting

If you encounter issues with the Gemini API:
1. Check that your API key is correct in the `.env` file
2. Ensure you have enabled the Gemini API in your Google Cloud project
3. Verify your account has proper permissions to use the API
4. Check the API quotas and limits in your Google Cloud console

If you encounter issues running the application in PowerShell:
1. Instead of using `&&` to chain commands, run them separately
2. Ensure you're using full paths when changing directories
3. If running into permission issues, try running PowerShell as administrator

If the application doesn't start properly:
1. Run `python main.py --check-env` to verify your environment
2. Make sure all dependencies are installed with `pip install -r requirements.txt`
3. Check if Streamlit is installed correctly with `pip show streamlit`

## License

MIT 