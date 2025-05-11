import os
import streamlit as st
import time
from dotenv import load_dotenv
import json

from .document_loader import DocumentLoader
from .vector_store import VectorStore
from .llm_integration import LLMIntegration
from .agent import Agent

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

# Paths
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
vector_store_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vector_store")

# Create vector_store directory if it doesn't exist
os.makedirs(vector_store_dir, exist_ok=True)

# Sidebar
st.sidebar.title("RAG-Powered Multi-Agent Q&A")
st.sidebar.markdown("---")

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
if st.session_state.vector_store_initialized:
    st.sidebar.markdown("Status: :green[Ready]")
else:
    st.sidebar.markdown("Status: :red[Not Initialized]")

st.sidebar.markdown("---")
st.sidebar.markdown("### Instructions")
st.sidebar.markdown("""
- Ask a question about AI, cloud computing, or blockchain
- Try using calculator commands like "calculate 25 * 4"
- Try definition requests like "define blockchain"
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
    
    for i, item in enumerate(reversed(st.session_state.history)):
        with st.expander(f"{item['timestamp']} - {item['query']}"):
            st.write(f"Workflow: {item['result']['workflow'].capitalize()}")
            st.write(f"Answer: {item['result']['answer']}")
            
            # Add a button to expand the full result as JSON
            if st.button(f"Show Full Result Details", key=f"details_{i}"):
                st.json(item['result']) 