import os
import streamlit as st
import time
from dotenv import load_dotenv
import json
import sys
import shutil

# Add the current directory to the path so that Python can find our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.document_loader import DocumentLoader
from src.vector_store import VectorStore
from src.llm_integration import LLMIntegration
from src.agent import Agent

# Load environment variables
load_dotenv()

# Set page title and layout
st.set_page_config(
    page_title="RAG-Powered Multi-Agent Q&A",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if "vector_store_initialized" not in st.session_state:
    st.session_state.vector_store_initialized = False
if "agent" not in st.session_state:
    st.session_state.agent = None
if "history" not in st.session_state:
    st.session_state.history = []
if "documents_uploaded" not in st.session_state:
    st.session_state.documents_uploaded = False
if "upload_status" not in st.session_state:
    st.session_state.upload_status = ""
if "show_full_result" not in st.session_state:
    st.session_state.show_full_result = {}

# Paths
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
vector_store_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vector_store")

# Create vector_store directory if it doesn't exist
os.makedirs(vector_store_dir, exist_ok=True)
os.makedirs(data_dir, exist_ok=True)

# Sidebar
st.sidebar.title("RAG-Powered Multi-Agent Q&A")
st.sidebar.markdown("---")

# Document Upload Section
st.sidebar.markdown("### Document Management")

# Upload Documents Section
st.sidebar.subheader("Upload Documents")
uploaded_files = st.sidebar.file_uploader("Upload documents", 
                                 type=["txt", "pdf"], 
                                 accept_multiple_files=True,
                                 help="Upload text or PDF documents to add to the knowledge base.")

if uploaded_files:
    if st.sidebar.button("Process Uploaded Documents"):
        # Process the files outside the expander
        st.session_state.upload_status = "Processing documents..."
        
        # Save uploaded files to data directory
        saved_files = []
        for uploaded_file in uploaded_files:
            file_path = os.path.join(data_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            saved_files.append(f"{uploaded_file.name} ({file_ext[1:]} file)")
        
        st.session_state.documents_uploaded = True
        st.session_state.upload_status = f"Uploaded {len(uploaded_files)} documents. Please initialize the vector store to include them."

# Display upload status if any
if st.session_state.upload_status:
    st.sidebar.success(st.session_state.upload_status)

# Display current documents
with st.sidebar.expander("Current Documents"):
    if os.path.exists(data_dir):
        docs = [f for f in os.listdir(data_dir) if f.endswith(('.txt', '.pdf'))]
        if docs:
            # Group documents by type
            text_docs = [doc for doc in docs if doc.endswith('.txt')]
            pdf_docs = [doc for doc in docs if doc.endswith('.pdf')]
            
            if text_docs:
                st.markdown("**Text Documents:**")
                for doc in text_docs:
                    st.text(doc)
            
            if pdf_docs:
                st.markdown("**PDF Documents:**")
                for doc in pdf_docs:
                    st.text(doc)
            
            if st.button("Clear All Documents"):
                # Create backup directory
                backup_dir = os.path.join(os.path.dirname(data_dir), "data_backup")
                os.makedirs(backup_dir, exist_ok=True)
                
                # Copy files to backup
                for doc in docs:
                    shutil.copy(os.path.join(data_dir, doc), 
                              os.path.join(backup_dir, doc))
                
                # Clear data directory
                for doc in docs:
                    os.remove(os.path.join(data_dir, doc))
                
                st.session_state.documents_uploaded = False
                st.session_state.vector_store_initialized = False
                st.success(f"Cleared {len(docs)} documents. Documents backed up to data_backup directory.")
        else:
            st.text("No documents in the data directory.")

# Initialize Vector Store
if st.sidebar.button("Initialize Vector Store"):
    with st.sidebar.status("Loading documents and initializing vector store..."):
        # Load documents
        st.sidebar.text("Loading documents...")
        loader = DocumentLoader(data_dir)
        documents = loader.load_documents()
        
        # Initialize Vector Store
        st.sidebar.text("Creating vector store...")
        vector_store = VectorStore()
        vector_store.create_vector_store(documents)
        
        # Save Vector Store
        st.sidebar.text("Saving vector store...")
        vector_store.save_vector_store(vector_store_dir)
        
        # Initialize LLM
        st.sidebar.text("Initializing LLM...")
        llm = LLMIntegration()
        
        # Initialize Agent
        st.sidebar.text("Initializing Agent...")
        agent = Agent(vector_store, llm)
        
        # Update session state
        st.session_state.vector_store_initialized = True
        st.session_state.agent = agent
        
    st.sidebar.success("Vector store initialized successfully!")

# Load pre-existing Vector Store
if not st.session_state.vector_store_initialized and os.path.exists(vector_store_dir):
    if st.sidebar.button("Load Existing Vector Store"):
        with st.sidebar.status("Loading existing vector store..."):
            # Initialize Vector Store and load from disk
            st.sidebar.text("Loading vector store...")
            vector_store = VectorStore()
            vector_store.load_vector_store(vector_store_dir)
            
            # Initialize LLM
            st.sidebar.text("Initializing LLM...")
            llm = LLMIntegration()
            
            # Initialize Agent
            st.sidebar.text("Initializing Agent...")
            agent = Agent(vector_store, llm)
            
            # Update session state
            st.session_state.vector_store_initialized = True
            st.session_state.agent = agent
            
        st.sidebar.success("Vector store loaded successfully!")

# Status indicator
st.sidebar.markdown("---")
st.sidebar.markdown("### System Status")
if st.session_state.vector_store_initialized:
    st.sidebar.success("Status: Ready")
    
    # Show document statistics
    docs = [f for f in os.listdir(data_dir) if f.endswith(('.txt', '.pdf'))]
    text_docs = [doc for doc in docs if doc.endswith('.txt')]
    pdf_docs = [doc for doc in docs if doc.endswith('.pdf')]
    
    st.sidebar.info(f"Documents: {len(docs)} total ({len(text_docs)} text, {len(pdf_docs)} PDF)")
else:
    st.sidebar.error("Status: Not Initialized")

st.sidebar.markdown("---")
st.sidebar.markdown("### Instructions")
st.sidebar.markdown("""
- Ask a question about AI, cloud computing, or blockchain
- Try using calculator commands like "calculate 25 * 4"
- Try definition requests like "define blockchain"
- Upload your own text or PDF documents in the Document Management section
""")

# Main content
st.title("RAG-Powered Multi-Agent Q&A")

# Query input
query = st.text_input("Enter your question:", placeholder="e.g., What is artificial intelligence? or calculate 25 * 4")

# Process query on submission
if query and st.button("Submit"):
    if not st.session_state.vector_store_initialized:
        st.error("Please initialize the vector store first!")
    else:
        # Create a placeholder for the spinning animation
        with st.status("Processing your question...") as status:
            # Process the query using the agent
            result = st.session_state.agent.process_query(query)
            
            # Add to history
            st.session_state.history.append({
                "query": query,
                "result": result,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # Mark as complete
            status.update(label="Processing complete!", state="complete", expanded=False)
        
        # Display the result
        st.markdown("### Answer")
        st.write(result["answer"])
        
        # Show workflow information
        st.markdown("### Workflow Information")
        workflow_col1, workflow_col2 = st.columns(2)
        with workflow_col1:
            st.info(f"Workflow: {result['workflow'].capitalize()}")
        with workflow_col2:
            st.info(f"Query: {result['query']}")
        
        # Show retrieved documents for RAG workflow
        if result["workflow"] == "rag" and "retrieved_docs" in result:
            st.markdown("### Retrieved Documents")
            for i, doc in enumerate(result["retrieved_docs"]):
                with st.expander(f"Document {i+1} (Relevance: {doc['relevance_score']:.4f})"):
                    st.write(doc["content"])
                    if "metadata" in doc and doc["metadata"]:
                        st.write("Metadata:", doc["metadata"])
        
        # Show calculation details for calculator workflow
        if result["workflow"] == "calculator" and "result" in result:
            calc_result = result["result"]
            if calc_result["status"] == "success":
                st.markdown("### Calculation Details")
                st.success(f"Expression: {calc_result['expression']}")
                st.success(f"Result: {calc_result['value']}")
        
        # Show dictionary details
        if result["workflow"] == "dictionary" and "result" in result:
            dict_result = result["result"]
            if dict_result["status"] == "success":
                st.markdown("### Definition Details")
                st.success(f"Term: {dict_result['term']}")
                if "note" in dict_result:
                    st.info(dict_result["note"])

# Query history
if st.session_state.history:
    st.markdown("---")
    st.markdown("### Query History")
    
    # Create a container for the history items
    history_container = st.container()
    
    with history_container:
        for i, item in enumerate(reversed(st.session_state.history)):
            # Create a unique key for each history item
            history_key = f"history_{i}"
            
            # Create a container for each history item
            with st.expander(f"{item['timestamp']} - {item['query']}"):
                st.write(f"Workflow: {item['result']['workflow'].capitalize()}")
                st.write(f"Answer: {item['result']['answer']}")
                
                # Use a separate button for showing details
                show_details_key = f"show_details_{i}"
                if show_details_key not in st.session_state.show_full_result:
                    st.session_state.show_full_result[show_details_key] = False
                
                if st.button("Show Full Result Details", key=show_details_key):
                    st.session_state.show_full_result[show_details_key] = not st.session_state.show_full_result[show_details_key]
                
                # Show the full result if the button was clicked
                if st.session_state.show_full_result[show_details_key]:
                    st.json(item['result']) 