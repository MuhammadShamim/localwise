"""
LocalWise Query Engine

This module provides intelligent document querying and retrieval capabilities using
Retrieval Augmented Generation (RAG). It combines vector similarity search with
large language model (LLM) reasoning to provide accurate, context-aware answers.

Key Features:
- RAG-based document querying with Ollama LLMs
- Vector similarity search for relevant context retrieval
- Intelligent prompt engineering for accurate responses
- Source attribution and citation tracking
- Query validation and error handling
- Search suggestions and document exploration

Architecture:
- QueryEngine: Main service class for document querying
- RAG implementation with configurable retrieval parameters
- Integration with embedding service for vector search
- Streamlit-compatible response streaming

Dependencies:
- Ollama: Local LLM for response generation
- ChromaDB: Vector database for similarity search
- LangChain: LLM framework and abstractions

Version: 1.0.0
Author: LocalWise Development Team
"""

import streamlit as st
from typing import List, Dict, Any, Optional, Tuple
from langchain_ollama import ChatOllama
from langchain.schema import Document

from .embedding_service import EmbeddingService
import config


class QueryEngine:
    """
    Intelligent document querying engine using RAG (Retrieval Augmented Generation).
    
    This class provides the core querying capabilities for LocalWise, combining
    vector similarity search with language model reasoning to answer questions
    based on the user's document collection.
    
    Features:
    - Context-aware response generation
    - Source attribution and citation
    - Configurable retrieval parameters
    - Error handling and validation
    - Query suggestions and exploration
    
    Attributes:
        model_name (str): Ollama model for response generation
        base_url (str): Ollama server URL
        temperature (float): LLM temperature for response generation
        max_context_docs (int): Maximum documents to use as context
        embedding_service (EmbeddingService): Service for vector operations
    """
    
    def __init__(self, 
                 model_name: str = None,
                 base_url: str = None,
                 temperature: float = None,
                 max_context_docs: int = None):
        """
        Initialize the query engine with configuration.
        
        Args:
            model_name: Ollama model name (defaults to config.OLLAMA_MODEL)
            base_url: Ollama server URL (defaults to config.OLLAMA_BASE_URL)
            temperature: LLM temperature (defaults to 0.1)
            max_context_docs: Max docs for context (defaults to config.NUM_RETRIEVED_DOCS)
        """
        self.model_name = model_name or config.OLLAMA_MODEL
        self.base_url = base_url or config.OLLAMA_BASE_URL
        self.temperature = temperature or 0.1
        self.max_context_docs = max_context_docs or getattr(config, 'NUM_RETRIEVED_DOCS', 5)
        
        self.embedding_service = EmbeddingService(
            model_name=self.model_name,
            base_url=self.base_url
        )
        self._llm = None
        self._vectorstore = None
    
    @property
    def llm(self) -> Optional[ChatOllama]:
        """Lazy-load language model instance."""
        if self._llm is None:
            self._llm = self.create_llm()
        return self._llm
    
    @property
    def vectorstore(self):
        """Get vectorstore from embedding service."""
        if self._vectorstore is None:
            self._vectorstore = self.embedding_service.vectorstore
        return self._vectorstore
    
    def create_llm(self) -> Optional[ChatOllama]:
        """
        Create and configure the language model for response generation.
        
        Returns:
            ChatOllama instance or None if creation failed
        """
        try:
            return ChatOllama(
                model=self.model_name,
                base_url=self.base_url,
                temperature=self.temperature
            )
        except Exception as e:
            if st:  # Only use Streamlit if available
                st.error(f"Failed to create language model: {e}")
            else:
                print(f"❌ Failed to create language model: {e}")
            return None
    
    def query_documents(self, 
                       question: str, 
                       vectorstore=None, 
                       llm=None,
                       include_sources: bool = True) -> str:
        """
        Query documents using RAG (Retrieval Augmented Generation).
        
        This method implements the complete RAG pipeline:
        1. Retrieve relevant documents via vector similarity search
        2. Prepare context from retrieved documents
        3. Generate response using LLM with context
        4. Format and return the final answer
        
        Args:
            question: User's question or query
            vectorstore: Optional vectorstore override
            llm: Optional LLM override
            include_sources: Whether to include source attributions
            
        Returns:
            Generated response string with answer and optional sources
        """
        # Use provided or default vectorstore
        vectorstore = vectorstore or self.vectorstore
        if vectorstore is None:
            return ("❌ Error: Vector database not available. "
                   "Please ensure documents are processed and embeddings are created.")
        
        # Use provided or default LLM
        llm = llm or self.llm
        if llm is None:
            return ("❌ Error: Language model not available. "
                   "Please check Ollama service and model availability.")
        
        try:
            # Step 1: Retrieve relevant documents
            if st:  # Streamlit interface
                with st.spinner("🔍 Searching through your documents..."):
                    docs = self.search_similar_documents(
                        question, vectorstore, k=self.max_context_docs
                    )
            else:  # CLI interface
                print("🔍 Searching documents...")
                docs = self.search_similar_documents(
                    question, vectorstore, k=self.max_context_docs
                )
            
            if not docs:
                return ("❌ No relevant documents found for your question. "
                       "Try rephrasing your query or check if documents are properly processed.")
            
            # Step 2: Prepare context from retrieved documents  
            context = self._prepare_context(docs)
            
            # Step 3: Create optimized prompt
            prompt = self._create_rag_prompt(question, context)
            
            # Step 4: Generate response
            if st:  # Streamlit interface
                with st.spinner("🧠 Generating response..."):
                    response = llm.invoke(prompt)
            else:  # CLI interface
                print("🧠 Generating response...")
                response = llm.invoke(prompt)
            
            # Step 5: Extract and format response
            answer_text = response.content if hasattr(response, 'content') else str(response)
            
            # Step 6: Add source information if requested
            if include_sources:
                sources_text = self._format_sources(docs)
                final_response = f"{answer_text}\\n\\n📚 **Sources:**\\n{sources_text}"
            else:
                final_response = answer_text
            
            return final_response
            
        except Exception as e:
            error_msg = f"❌ Error processing your question: {str(e)}"
            if st:
                st.error(error_msg)
            return error_msg
    
    def search_similar_documents(self, 
                               query: str, 
                               vectorstore=None, 
                               k: int = 5) -> List[Document]:
        """
        Search for documents similar to the query using vector similarity.
        
        Args:
            query: Search query text
            vectorstore: Optional vectorstore override
            k: Number of documents to retrieve
            
        Returns:
            List of relevant Document objects with content and metadata
        """
        vectorstore = vectorstore or self.vectorstore
        if vectorstore is None:
            return []
        
        try:
            docs = vectorstore.similarity_search(query, k=k)
            return docs
        except Exception as e:
            error_msg = f"Error searching documents: {e}"
            if st:
                st.error(error_msg)
            else:
                print(f"❌ {error_msg}")
            return []
    
    def get_document_suggestions(self, 
                               vectorstore=None, 
                               num_suggestions: int = 5) -> List[str]:
        """
        Get sample document-based query suggestions.
        
        Analyzes available documents to suggest relevant queries
        that users might find helpful.
        
        Args:
            vectorstore: Optional vectorstore override
            num_suggestions: Number of suggestions to generate
            
        Returns:
            List of suggested query strings
        """
        vectorstore = vectorstore or self.vectorstore
        if vectorstore is None:
            return []
        
        try:
            # Get diverse sample documents
            docs = vectorstore.similarity_search("", k=num_suggestions * 2)
            
            suggestions = []
            seen_sources = set()
            
            for doc in docs:
                source = doc.metadata.get('source', 'Unknown')
                
                # Avoid duplicate sources
                if source in seen_sources:
                    continue
                seen_sources.add(source)
                
                # Extract meaningful content for suggestions
                content = doc.page_content[:150].strip()
                if content:
                    # Create contextual suggestions based on content
                    if '.pdf' in source.lower():
                        suggestions.append(f"Summarize the PDF document: {source}")
                    elif '.py' in source.lower():
                        suggestions.append(f"Explain the Python code in: {source}")
                    elif '.md' in source.lower():
                        suggestions.append(f"What does the documentation say about: {source}")
                    else:
                        suggestions.append(f"What information is available in: {source}")
                
                if len(suggestions) >= num_suggestions:
                    break
            
            return suggestions
            
        except Exception:
            return [
                "What are the main topics covered in my documents?",
                "Can you summarize the key information?",
                "What are the most important points mentioned?",
                "Find information about specific topics",
                "Explain technical concepts from my files"
            ]
    
    def validate_query_system(self) -> Tuple[bool, List[str]]:
        """
        Validate that the query system is ready to handle requests.
        
        Checks all dependencies and services required for querying:
        - Ollama service availability
        - Vector database accessibility  
        - Language model initialization
        
        Returns:
            Tuple of (is_ready, list_of_issues)
        """
        issues = []
        
        # Check Ollama connection
        is_available, error_msg = self.embedding_service.validate_ollama_connection()
        if not is_available:
            issues.append(f"Ollama service: {error_msg}")
        
        # Check vector database
        if not self.embedding_service.check_embeddings_exist():
            issues.append("Vector database: No embeddings found. Please run document processing first.")
        else:
            try:
                vectorstore = self.vectorstore
                if vectorstore is None:
                    issues.append("Vector database: Could not load existing embeddings")
            except Exception as e:
                issues.append(f"Vector database: Loading error - {e}")
        
        # Check language model
        try:
            llm = self.llm
            if llm is None:
                issues.append("Language model: Could not initialize Ollama LLM")
        except Exception as e:
            issues.append(f"Language model: Initialization error - {e}")
        
        return len(issues) == 0, issues
    
    def _prepare_context(self, docs: List[Document]) -> str:
        """
        Prepare context text from retrieved documents.
        
        Args:
            docs: List of retrieved Document objects
            
        Returns:
            Formatted context string for LLM prompt
        """
        context_parts = []
        
        for i, doc in enumerate(docs):
            source = doc.metadata.get('source', 'Unknown')
            content = doc.page_content.strip()
            
            # Format each document with clear separation
            doc_context = f"Document {i+1} (Source: {source}):\\n{content}"
            context_parts.append(doc_context)
        
        return "\\n\\n".join(context_parts)
    
    def _create_rag_prompt(self, question: str, context: str) -> str:
        """
        Create an optimized RAG prompt for the language model.
        
        Args:
            question: User's question
            context: Retrieved document context
            
        Returns:
            Formatted prompt string
        """
        return f"""You are LocalWise, an AI assistant that helps users understand their documents.

Based on the following documents from the user's collection, please answer their question accurately and helpfully.

Context from documents:
{context}

User Question: {question}

Instructions:
1. Answer based primarily on the provided document context
2. Be specific and cite relevant information when possible
3. If the documents don't contain sufficient information, state that clearly
4. Keep your response well-organized and easy to understand
5. When referencing information, mention which document it came from
6. Use clear, professional language appropriate for the content

Answer:"""
    
    def _format_sources(self, docs: List[Document]) -> str:
        """
        Format source documents for display in the response.
        
        Args:
            docs: List of source Document objects
            
        Returns:
            Formatted sources string
        """
        if not docs:
            return "No sources found."
        
        sources = []
        seen_sources = set()
        
        for i, doc in enumerate(docs):
            source = doc.metadata.get('source', 'Unknown')
            
            # Avoid duplicate sources in display
            if source in seen_sources:
                continue
            seen_sources.add(source)
            
            # Create preview of document content
            preview = doc.page_content[:200].strip()
            if len(doc.page_content) > 200:
                preview += "..."
            
            sources.append(f"**{len(sources) + 1}. {source}**\\n{preview}")
        
        return "\\n\\n".join(sources)


# Convenience functions for backward compatibility and easy access
def create_llm():
    """
    Convenience function for creating language model.
    
    Returns:
        ChatOllama instance or None
    """
    engine = QueryEngine()
    return engine.create_llm()


def query_documents(question: str, vectorstore=None, llm=None) -> str:
    """
    Convenience function for document querying.
    
    Args:
        question: User's question
        vectorstore: Optional vectorstore override
        llm: Optional LLM override
        
    Returns:
        Generated response string
    """
    engine = QueryEngine()
    return engine.query_documents(question, vectorstore, llm)


def search_similar_documents(query: str, vectorstore=None, k: int = 5) -> List[Document]:
    """
    Convenience function for document search.
    
    Args:
        query: Search query
        vectorstore: Optional vectorstore override
        k: Number of results
        
    Returns:
        List of relevant documents
    """
    engine = QueryEngine()
    return engine.search_similar_documents(query, vectorstore, k)


def get_document_suggestions(vectorstore=None, num_suggestions: int = 5) -> List[str]:
    """
    Convenience function for getting query suggestions.
    
    Args:
        vectorstore: Optional vectorstore override
        num_suggestions: Number of suggestions
        
    Returns:
        List of suggested queries
    """
    engine = QueryEngine()
    return engine.get_document_suggestions(vectorstore, num_suggestions)


def validate_query_system() -> Tuple[bool, List[str]]:
    """
    Convenience function for validating query system.
    
    Returns:
        Tuple of (is_ready, issues_list)
    """
    engine = QueryEngine()
    return engine.validate_query_system()


def format_sources(docs: List[Document]) -> str:
    """
    Convenience function for formatting document sources.
    
    Args:
        docs: List of Document objects
        
    Returns:
        Formatted sources string
    """
    engine = QueryEngine()
    return engine._format_sources(docs)