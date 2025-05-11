import os
import glob
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader, PyPDFLoader, DirectoryLoader
from langchain.schema import Document


class DocumentLoader:
    def __init__(self, data_dir: str, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the DocumentLoader.
        
        Args:
            data_dir (str): Directory containing the documents to load.
            chunk_size (int): Size of text chunks for splitting documents.
            chunk_overlap (int): Overlap between consecutive chunks.
        """
        self.data_dir = data_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    
    def load_documents(self) -> List[Document]:
        """
        Load documents from the data directory and split them into chunks.
        
        Returns:
            List[Document]: List of document chunks.
        """
        documents = []
        
        # Load text files
        text_files = glob.glob(os.path.join(self.data_dir, "*.txt"))
        for file_path in text_files:
            try:
                loader = TextLoader(file_path, encoding="utf-8")
                docs = loader.load()
                documents.extend(docs)
                print(f"Loaded text file: {file_path}")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        # Load PDF files
        pdf_files = glob.glob(os.path.join(self.data_dir, "*.pdf"))
        for file_path in pdf_files:
            try:
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                documents.extend(docs)
                print(f"Loaded PDF file: {file_path}")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        print(f"Loaded {len(documents)} documents from {self.data_dir}")
        
        # Apply text preprocessing
        documents = self._preprocess_documents(documents)
        
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        print(f"Split into {len(chunks)} chunks")
        
        return chunks
    
    def _preprocess_documents(self, documents: List[Document]) -> List[Document]:
        """
        Preprocess documents to clean and normalize text.
        
        Args:
            documents (List[Document]): List of documents to preprocess.
            
        Returns:
            List[Document]: List of preprocessed documents.
        """
        preprocessed_docs = []
        
        for doc in documents:
            # Get document content
            content = doc.page_content
            
            # Basic text cleaning
            content = content.replace('\n\n', ' ')
            content = content.replace('\t', ' ')
            content = ' '.join(content.split())  # Normalize whitespace
            
            # Create new document with cleaned content
            new_doc = Document(
                page_content=content,
                metadata=doc.metadata
            )
            
            preprocessed_docs.append(new_doc)
        
        return preprocessed_docs 