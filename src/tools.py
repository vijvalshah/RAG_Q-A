import re
import math
import requests
import wikipedia
from typing import Dict, Any


class CalculatorTool:
    """A simple calculator tool that can perform basic arithmetic operations."""
    
    def run(self, query: str) -> Dict[str, Any]:
        """
        Evaluate a mathematical expression.
        
        Args:
            query (str): Mathematical expression to evaluate.
            
        Returns:
            Dict[str, Any]: Result dictionary with status and value.
        """
        # Extract mathematical expression from the query
        expression = self._extract_expression(query)
        
        if not expression:
            return {
                "status": "error",
                "error": "No valid mathematical expression found in the query",
                "value": None
            }
        
        try:
            # Replace mathematical words with symbols
            expression = self._normalize_expression(expression)
            
            # Safely evaluate the expression
            result = self._safe_eval(expression)
            
            return {
                "status": "success",
                "value": result,
                "expression": expression
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "value": None
            }
    
    def _extract_expression(self, query: str) -> str:
        """Extract mathematical expression from the query."""
        # Try to find expressions like "calculate 2+2" or "what is 5*3?"
        match = re.search(r'(?:calculate|compute|what\s+is|find)?\s*(.+?)[?.]?$', query, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return query
    
    def _normalize_expression(self, expression: str) -> str:
        """Replace mathematical words with symbols."""
        expression = expression.lower()
        expression = re.sub(r'\bplus\b', '+', expression)
        expression = re.sub(r'\bminus\b', '-', expression)
        expression = re.sub(r'\btimes\b', '*', expression)
        expression = re.sub(r'\bdivided\s+by\b', '/', expression)
        expression = re.sub(r'\bsquare\s+root\s+of\b', 'math.sqrt(', expression)
        if 'math.sqrt(' in expression and ')' not in expression:
            expression += ')'
        return expression
    
    def _safe_eval(self, expression: str) -> float:
        """Safely evaluate a mathematical expression."""
        # List of allowed names for evaluation
        allowed_names = {
            'math': math,
            'abs': abs,
            'pow': pow,
            'round': round
        }
        
        # Evaluate the expression with limited built-in functions
        return eval(expression, {"__builtins__": {}}, allowed_names)


class DictionaryTool:
    """A tool that provides definitions for words and concepts."""
    
    def run(self, query: str) -> Dict[str, Any]:
        """
        Get the definition of a word or concept using Wikipedia.
        
        Args:
            query (str): Word or concept to define.
            
        Returns:
            Dict[str, Any]: Result dictionary with status and definition.
        """
        # Extract the term to define
        term = self._extract_term(query)
        
        if not term:
            return {
                "status": "error",
                "error": "No term to define found in the query",
                "definition": None
            }
        
        try:
            # Try to get a Wikipedia summary for the term
            summary = wikipedia.summary(term, sentences=3, auto_suggest=True)
            
            return {
                "status": "success",
                "term": term,
                "definition": summary
            }
        except wikipedia.exceptions.DisambiguationError as e:
            # If there are multiple matches, choose the first option
            try:
                summary = wikipedia.summary(e.options[0], sentences=3)
                return {
                    "status": "success",
                    "term": e.options[0],
                    "definition": summary,
                    "note": f"Multiple matches found. Showing definition for '{e.options[0]}'"
                }
            except:
                return {
                    "status": "error",
                    "error": f"Multiple matches found: {', '.join(e.options[:5])}...",
                    "definition": None
                }
        except wikipedia.exceptions.PageError:
            # If no exact match found, try searching
            try:
                search_results = wikipedia.search(term, results=1)
                if search_results:
                    summary = wikipedia.summary(search_results[0], sentences=3)
                    return {
                        "status": "success",
                        "term": search_results[0],
                        "definition": summary,
                        "note": f"No exact match found. Showing definition for '{search_results[0]}'"
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"No definition found for '{term}'",
                        "definition": None
                    }
            except:
                return {
                    "status": "error",
                    "error": f"Failed to find definition for '{term}'",
                    "definition": None
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "definition": None
            }
    
    def _extract_term(self, query: str) -> str:
        """Extract the term to define from the query."""
        # Try to find patterns like "define AI" or "what is blockchain?"
        match = re.search(r'(?:define|what\s+is|meaning\s+of|definition\s+of)\s+(.+?)[?.]?$', query, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # If no pattern matched, use the whole query
        return query.strip() 