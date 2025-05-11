from typing import List, Tuple
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document


class VectorStore:
    def __init__(self, embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the VectorStore.
        
        Args:
            embedding_model_name (str): Name of the Hugging Face embedding model to use.
        """
        self.embedding_model = HuggingFaceEmbeddings(model_name=embedding_model_name)
        self.vector_store = None
    
    def create_vector_store(self, documents: List[Document]):
        """
        Create a vector store from documents.
        
        Args:
            documents (List[Document]): List of document chunks to index.
        """
        self.vector_store = FAISS.from_documents(documents, self.embedding_model)
        print(f"Created vector store with {len(documents)} documents")
    
    def save_vector_store(self, path: str):
        """
        Save the vector store to disk.
        
        Args:
            path (str): Path to save the vector store.
        """
        if self.vector_store:
            self.vector_store.save_local(path)
            print(f"Saved vector store to {path}")
        else:
            print("No vector store to save")
    
    def load_vector_store(self, path: str):
        """
        Load a vector store from disk.
        
        Args:
            path (str): Path to load the vector store from.
        """
        self.vector_store = FAISS.load_local(path, self.embedding_model)
        print(f"Loaded vector store from {path}")
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[Document, float]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query (str): Query text.
            top_k (int): Number of documents to retrieve.
            
        Returns:
            List[Tuple[Document, float]]: List of (document, score) tuples.
        """
        if not self.vector_store:
            print("No vector store available for retrieval")
            return []
        
        docs_with_scores = self.vector_store.similarity_search_with_score(query, k=top_k)
        return docs_with_scores 