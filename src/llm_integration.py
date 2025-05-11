import os
import time
import logging
import random
from typing import List, Tuple, Optional, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMIntegration:
    def __init__(self, model_name: str = "gemini-1.5-pro"):
        """
        Initialize the LLM integration with Google's Gemini model.
        
        Args:
            model_name (str): Name of the Google Gemini model to use.
        """
        # Get API key from environment variable
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set. Please add it to your .env file.")
        
        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=google_api_key,
            temperature=0.1,
            convert_system_message_to_human=True
        )
        
        self.qa_prompt_template = """
        You are a helpful assistant that provides accurate and informative answers based on the context provided.
        
        Context:
        {context}
        
        Question: {question}
        
        Please provide a comprehensive answer to the question based only on the information in the context.
        If the context doesn't contain the relevant information, admit that you don't know rather than making up an answer.
        
        Answer:
        """
        
        self.qa_prompt = PromptTemplate(
            template=self.qa_prompt_template,
            input_variables=["context", "question"]
        )
        
        self.qa_chain = LLMChain(llm=self.llm, prompt=self.qa_prompt)
        
        # Retry configuration
        self.max_retries = 3
        self.base_delay = 2  # Base delay in seconds
        
    def generate_answer(self, query: str, docs_with_scores: List[Tuple[Document, float]]) -> str:
        """
        Generate an answer based on the query and retrieved documents.
        
        Args:
            query (str): User query.
            docs_with_scores (List[Tuple[Document, float]]): List of retrieved documents with relevance scores.
            
        Returns:
            str: Generated answer.
        """
        # Format the context from retrieved documents
        context = self._format_context(docs_with_scores)
        
        # Try to generate a response with retries
        return self._call_with_retries(context, query)
    
    def _call_with_retries(self, context: str, question: str) -> str:
        """
        Call the LLM with exponential backoff retry logic.
        
        Args:
            context (str): Context information.
            question (str): User question.
            
        Returns:
            str: Generated answer or error message.
        """
        retries = 0
        last_exception = None
        
        while retries <= self.max_retries:
            try:
                # Generate answer using the LLM chain
                logger.info(f"Attempt {retries + 1}/{self.max_retries + 1} to call LLM API")
                response = self.qa_chain.run(context=context, question=question)
                return response
            except Exception as e:
                last_exception = e
                error_str = str(e).lower()
                
                # Check if this is a quota/rate limit issue
                if ("429" in error_str or "quota" in error_str or "rate limit" in error_str) and retries < self.max_retries:
                    # Get retry delay information if available
                    retry_delay = self._extract_retry_delay(error_str)
                    if retry_delay:
                        delay = retry_delay
                    else:
                        # Exponential backoff with jitter
                        delay = (self.base_delay * (2 ** retries)) + (random.random() * 2)
                    
                    logger.warning(f"Rate limit exceeded. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                    retries += 1
                    continue
                
                # For other errors or if we've exhausted retries, break the loop
                break
        
        # If we're here, all retries failed or a non-retryable error occurred
        logger.error(f"Failed to generate response after {retries} retries: {last_exception}")
        
        # Provide appropriate error message
        error_str = str(last_exception).lower()
        if "429" in error_str or "quota" in error_str or "rate limit" in error_str:
            return "I'm unable to generate a response due to API rate limits. Options:\n1. Wait for quota to reset\n2. Check your Google Gemini API plan\n3. Ensure your API key is valid"
        elif "authentication" in error_str or "api key" in error_str:
            return "There's an issue with the API key. Please check your Google Gemini API key configuration."
        else:
            return f"Error generating response: {str(last_exception)}"
    
    def _extract_retry_delay(self, error_str: str) -> Optional[float]:
        """
        Extract retry delay from error message if available.
        
        Args:
            error_str (str): Error message string.
            
        Returns:
            Optional[float]: Retry delay in seconds, or None if not found.
        """
        # Try to find the retry_delay section in the error message
        # Common format: "retry_delay { seconds: 43 }"
        try:
            if "retry_delay" in error_str and "seconds" in error_str:
                # Very simple parser - extract the number after "seconds:"
                import re
                match = re.search(r'seconds:\s*(\d+)', error_str)
                if match:
                    return float(match.group(1))
        except Exception:
            pass
        return None

    def _format_context(self, docs_with_scores: List[Tuple[Document, float]]) -> str:
        """
        Format the retrieved documents into a context string for the LLM.
        
        Args:
            docs_with_scores (List[Tuple[Document, float]]): List of retrieved documents with relevance scores.
            
        Returns:
            str: Formatted context string.
        """
        # Extract text content from documents and join with separators
        context = "\n\n".join([doc.page_content for doc, _ in docs_with_scores])
        return context 