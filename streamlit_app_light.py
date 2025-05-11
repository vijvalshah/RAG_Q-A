import os
import streamlit as st
import time
from dotenv import load_dotenv
import sys
import shutil
import re

# Add the current directory to the path so that Python can find our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.document_loader import DocumentLoader
from src.vector_store import VectorStore

# Load environment variables
load_dotenv()

def main_app():
    """Main function to run the lightweight Streamlit app."""
    
    # Initialize session state variables
    if "vector_store_initialized" not in st.session_state:
        st.session_state.vector_store_initialized = False
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None
    if "history" not in st.session_state:
        st.session_state.history = []
    if "documents_uploaded" not in st.session_state:
        st.session_state.documents_uploaded = False
    if "upload_status" not in st.session_state:
        st.session_state.upload_status = ""

    # Paths
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    vector_store_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vector_store")

    # Create vector_store directory if it doesn't exist
    os.makedirs(vector_store_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)

    # Sidebar
    st.sidebar.title("RAG Document Viewer")
    st.sidebar.markdown("### Lightweight Version")
    st.sidebar.markdown("This version uses document retrieval only without LLM generation, perfect for when you've hit API quotas.")
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
            
            # Update session state
            st.session_state.vector_store_initialized = True
            st.session_state.vector_store = vector_store
            
        st.sidebar.success("Vector store initialized successfully!")

    # Load pre-existing Vector Store
    if not st.session_state.vector_store_initialized and os.path.exists(vector_store_dir):
        if st.sidebar.button("Load Existing Vector Store"):
            with st.sidebar.status("Loading existing vector store..."):
                # Initialize Vector Store and load from disk
                st.sidebar.text("Loading vector store...")
                vector_store = VectorStore()
                vector_store.load_vector_store(vector_store_dir)
                
                # Update session state
                st.session_state.vector_store_initialized = True
                st.session_state.vector_store = vector_store
                
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
    - This lightweight version only retrieves relevant documents without LLM generation
    - Perfect for when your API quota has been reached
    - Use specific keywords for better document retrieval
    - Upload your own text or PDF documents in the Document Management section
    """)

    # Main content
    if not st.title:  # Only show this if we're not in streamlit_cloud.py mode
        st.title("RAG Document Viewer (Lightweight)")
    
    st.write("""
    🔍 **API Quota-Friendly Mode**: This lightweight version only does document retrieval without using the LLM API, 
    so you can continue searching your documents even when you've reached API limits.
    """)

    # Query input
    query = st.text_input("Enter your search terms:", placeholder="e.g., SoulMesh, Blockchain, AI")

    # Simple keyword highlighting function
    def highlight_keywords(text, keywords):
        """Highlight keywords in text with markdown formatting."""
        highlighted = text
        for keyword in keywords:
            if not keyword.strip():
                continue
            pattern = re.compile(r'(' + re.escape(keyword) + r')', re.IGNORECASE)
            highlighted = pattern.sub(r'**\1**', highlighted)
        return highlighted

    # Process query on submission
    if query and st.button("Search"):
        if not st.session_state.vector_store_initialized:
            st.error("Please initialize the vector store first!")
        else:
            # Create a placeholder for the spinning animation
            with st.status("Searching documents...") as status:
                # Retrieve relevant documents
                docs_with_scores = st.session_state.vector_store.retrieve(query)
                
                # Add to history
                st.session_state.history.append({
                    "query": query,
                    "docs_with_scores": docs_with_scores,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })
                
                # Mark as complete
                status.update(label="Search complete!", state="complete", expanded=False)
            
            if not docs_with_scores:
                st.warning("No relevant documents found. Try broadening your search terms.")
            else:
                # Show retrieved documents
                st.markdown("### Retrieved Documents")
                
                # Get keywords for highlighting
                keywords = [k.strip() for k in query.split()]
                
                for i, (doc, score) in enumerate(docs_with_scores):
                    with st.expander(f"Document {i+1} (Relevance: {score:.4f})"):
                        # Highlight keywords in the document
                        highlighted_content = highlight_keywords(doc.page_content, keywords)
                        st.markdown(highlighted_content)
                        
                        if doc.metadata:
                            st.markdown("**Metadata:**")
                            for key, value in doc.metadata.items():
                                st.write(f"- {key}: {value}")

    # Query history
    if st.session_state.history:
        st.markdown("---")
        st.markdown("### Search History")
        
        # Create a container for the history items
        history_container = st.container()
        
        with history_container:
            for i, item in enumerate(reversed(st.session_state.history)):
                # Create a unique key for each history item
                with st.expander(f"{item['timestamp']} - {item['query']}"):
                    docs_with_scores = item['docs_with_scores']
                    
                    if not docs_with_scores:
                        st.write("No relevant documents found.")
                    else:
                        st.write(f"Found {len(docs_with_scores)} relevant documents")
                        
                        if st.button("Show Documents", key=f"show_docs_{i}"):
                            # Get keywords for highlighting
                            keywords = [k.strip() for k in item['query'].split()]
                            
                            for j, (doc, score) in enumerate(docs_with_scores):
                                st.markdown(f"**Document {j+1} (Relevance: {score:.4f})**")
                                # Highlight keywords in the document
                                highlighted_content = highlight_keywords(doc.page_content, keywords)
                                st.markdown(highlighted_content)
                                st.markdown("---")

# For direct execution of this file
if __name__ == "__main__":
    # Set page title and layout
    st.set_page_config(
        page_title="RAG Document Viewer (Lightweight)",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    main_app() 