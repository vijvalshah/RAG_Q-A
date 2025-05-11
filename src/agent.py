import re
import logging
from typing import Dict, Any, List, Tuple

from langchain.schema import Document
from .tools import CalculatorTool, DictionaryTool
from .vector_store import VectorStore
from .llm_integration import LLMIntegration

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Agent:
    """Agent that orchestrates the RAG workflow and tools."""
    
    def __init__(self, vector_store: VectorStore, llm: LLMIntegration):
        """
        Initialize the Agent.
        
        Args:
            vector_store (VectorStore): Vector store for document retrieval.
            llm (LLMIntegration): LLM integration for answer generation.
        """
        self.vector_store = vector_store
        self.llm = llm
        self.calculator = CalculatorTool()
        self.dictionary = DictionaryTool()
        
        # Define keywords for routing
        self.calculator_keywords = [
            "calculate", "compute", "sum", "difference", "product", 
            "divide", "multiply", "add", "subtract", "plus", "minus",
            "times", "divided by", "square root", "power", "percentage"
        ]
        
        self.dictionary_keywords = [
            "define", "meaning of", "definition of", "explain the term",
            "what does the term", "what is the definition"
        ]
        
        # Keywords that should override the dictionary routing and use RAG instead
        self.rag_override_keywords = [
            # People or entities
            "project", "about", "soulmesh", "vijval", "resume", "shah", 
            "author", "creator", "founder", "developer", "team",
            # Document-specific terms
            "document", "pdf", "file", "text", "content", "paper", "report",
            "article", "research", "publication", "book", "chapter",
            # Domain-specific terms (add terms relevant to your documents)
            "artificial intelligence", "ai", "blockchain", "cloud computing",
            "machine learning", "ml", "deep learning", "nlp", "natural language processing",
            # Technical terms
            "technology", "architecture", "framework", "algorithm", "system",
            "protocol", "platform", "infrastructure", "application", "software",
            "hardware", "device", "network", "database", "data"
        ]
    
    def _should_use_calculator(self, query: str) -> bool:
        """Check if the query should be routed to the calculator tool."""
        query_lower = query.lower()
        
        # First, check for mathematical expressions with numbers and operators
        if re.search(r'\d+\s*[\+\-\*/]\s*\d+', query_lower):
            return True
        
        # Next, check for calculator keywords
        for keyword in self.calculator_keywords:
            if keyword in query_lower:
                # Make sure the keyword isn't just part of a longer word
                if re.search(r'\b' + re.escape(keyword) + r'\b', query_lower):
                    return True
        
        return False
    
    def _should_use_dictionary(self, query: str) -> bool:
        """Check if the query should be routed to the dictionary tool."""
        query_lower = query.lower()
        
        # First check if any RAG override keywords are present
        for override in self.rag_override_keywords:
            if override.lower() in query_lower:
                return False
        
        # Check for document-specific context phrases
        doc_phrases = ["in the document", "in this document", "according to the document", 
                       "mentioned in", "based on the", "refers to", "written in", 
                       "from the document", "from the text", "content about"]
        for phrase in doc_phrases:
            if phrase in query_lower:
                return False
        
        # Check for "what is" pattern but not followed by a RAG override term
        if re.search(r'\bwhat\s+is\b', query_lower) or re.search(r'\bwho\s+is\b', query_lower):
            # Check for document contexts like "what is mentioned about X" or "what is X in the document"
            if any(ctx in query_lower for ctx in ["mentioned about", "mentioned in", "in the document", "said about"]):
                return False
            
            # Don't use dictionary for "what is [RAG term]"
            for override in self.rag_override_keywords:
                if override.lower() in query_lower:
                    return False
                
            # Check for context phrases that indicate someone wants information about a topic
            if "about" in query_lower and not any(kw in query_lower for kw in self.dictionary_keywords):
                return False
                
            # Default to dictionary for other "what is" questions when no specific indicators exist
            for keyword in self.dictionary_keywords:
                if keyword in query_lower:
                    return True
            
            # Default to RAG for other information-seeking questions
            return False
        
        # Check for other dictionary keywords (with strict word boundary check)
        for keyword in self.dictionary_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', query_lower):
                # Make sure there's no RAG override in the query after the keyword
                keyword_pos = query_lower.find(keyword)
                remainder = query_lower[keyword_pos + len(keyword):]
                if not any(override.lower() in remainder for override in self.rag_override_keywords):
                    return True
        
        return False
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query through the appropriate workflow.
        
        Args:
            query (str): User query.
            
        Returns:
            Dict[str, Any]: Result dictionary with workflow information and answer.
        """
        logger.info(f"Processing query: {query}")
        
        # Skip routing for code-related questions and specific knowledge domains
        if any(term in query.lower() for term in ["pl/sql", "sql", "code", "programming", "blockchain", "ai", "cloud computing"]):
            return self._rag_workflow(query)
        
        # Determine which workflow to use
        if self._should_use_calculator(query):
            return self._calculator_workflow(query)
        elif self._should_use_dictionary(query):
            return self._dictionary_workflow(query)
        else:
            return self._rag_workflow(query)
    
    def _calculator_workflow(self, query: str) -> Dict[str, Any]:
        """Execute the calculator workflow."""
        logger.info("Using calculator workflow")
        
        result = self.calculator.run(query)
        
        return {
            "workflow": "calculator",
            "query": query,
            "result": result,
            "answer": f"The result is {result['value']}" if result['status'] == 'success' else f"Error: {result['error']}"
        }
    
    def _dictionary_workflow(self, query: str) -> Dict[str, Any]:
        """Execute the dictionary workflow."""
        logger.info("Using dictionary workflow")
        
        result = self.dictionary.run(query)
        
        return {
            "workflow": "dictionary",
            "query": query,
            "result": result,
            "answer": result['definition'] if result['status'] == 'success' else f"Error: {result['error']}"
        }
    
    def _rag_workflow(self, query: str) -> Dict[str, Any]:
        """Execute the RAG workflow."""
        logger.info("Using RAG workflow")
        
        # Retrieve relevant documents
        docs_with_scores = self.vector_store.retrieve(query)
        
        # If no documents found, return an error
        if not docs_with_scores:
            return {
                "workflow": "rag",
                "query": query,
                "retrieved_docs": [],
                "answer": "I couldn't find any relevant information in my knowledge base to answer your question."
            }
        
        # Generate answer using the LLM
        answer = self.llm.generate_answer(query, docs_with_scores)
        
        # Format the retrieved documents for the response
        retrieved_docs = []
        for doc, score in docs_with_scores:
            retrieved_docs.append({
                "content": doc.page_content,
                "relevance_score": score,
                "metadata": doc.metadata
            })
        
        return {
            "workflow": "rag",
            "query": query,
            "retrieved_docs": retrieved_docs,
            "answer": answer
        } 