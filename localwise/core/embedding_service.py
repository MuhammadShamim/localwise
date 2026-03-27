"""
LocalWise Embedding Service

This module provides AI-powered text embedding generation and vector database management
for semantic document search and retrieval. It integrates with Ollama for local LLM
embeddings and ChromaDB for efficient vector storage.

Key Features:
- Ollama integration for local, private embeddings
- Batch processing for memory efficiency
- Progress tracking for large document sets
- Vector database persistence and loading
- Health checks and validation

Architecture:
- EmbeddingService: Main service class for embedding operations
- Validation utilities for Ollama connectivity
- Batch processing system for large datasets
- Statistics and monitoring capabilities

Dependencies:
- Ollama: Local LLM server for embedding generation
- ChromaDB: Vector database for similarity search
- LangChain: Framework for LLM integration

Version: 1.0.0
Author: LocalWise Development Team
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

from ..data.data_manager import DataManager
from localwise import config


class EmbeddingService:
    """
    Service for generating and managing text embeddings using Ollama and ChromaDB.
    
    This service handles the complete embedding workflow:
    1. Validation of Ollama service availability
    2. Batch processing of text chunks for memory efficiency  
    3. Vector database creation and persistence
    4. Loading and querying existing embeddings
    
    Attributes:
        model_name (str): Ollama model used for embeddings
        base_url (str): Ollama server URL
        db_folder (str): ChromaDB persistence directory
        batch_size (int): Batch size for processing large datasets
    """
    
    def __init__(self, 
                 model_name: str = None,
                 base_url: str = None,
                 db_folder: str = None,
                 batch_size: int = None):
        """
        Initialize the embedding service with configuration.
        
        Args:
            model_name: Ollama model name (defaults to config.OLLAMA_MODEL)
            base_url: Ollama server URL (defaults to config.OLLAMA_BASE_URL)
            db_folder: Vector DB directory (defaults to config.DB_FOLDER)
            batch_size: Processing batch size (defaults to config.CHUNK_BATCH_SIZE)
        """
        self.model_name = model_name or config.OLLAMA_MODEL
        self.base_url = base_url or config.OLLAMA_BASE_URL
        self.db_folder = db_folder or config.DB_FOLDER
        self.batch_size = batch_size or config.CHUNK_BATCH_SIZE
        
        self._embeddings = None
        self._vectorstore = None
    
    @property
    def embeddings(self) -> OllamaEmbeddings:
        """Lazy-load Ollama embeddings instance."""
        if self._embeddings is None:
            self._embeddings = OllamaEmbeddings(
                model=self.model_name,
                base_url=self.base_url
            )
        return self._embeddings
    
    @property
    def vectorstore(self) -> Optional[Chroma]:
        """Lazy-load vector database instance."""
        if self._vectorstore is None and self.check_embeddings_exist():
            self._vectorstore = self.load_vector_database()
        return self._vectorstore
    
    def validate_ollama_connection(self) -> Tuple[bool, Optional[str]]:
        """
        Validate Ollama service availability and model accessibility.
        
        Returns:
            Tuple of (is_available, error_message)
            - is_available: True if Ollama is ready, False otherwise
            - error_message: None if available, error description if not
        """
        try:
            # Use config validation if available, otherwise implement basic check
            return config.validate_ollama_connection()
        except Exception as e:
            return False, f"Connection validation failed: {str(e)}"
    
    def create_embeddings_from_processed_data(self, logger) -> bool:
        """
        Create embeddings from previously processed document data.
        
        This is Step 2 of the LocalWise pipeline, loading text chunks
        from the data manager and generating vector embeddings.
        
        Args:
            logger: Logger instance for status reporting
            
        Returns:
            True if embeddings created successfully, False otherwise
        """
        logger.info("=== Step 2: Creating Embeddings ===")
        print("🧠 Step 2: Creating Embeddings")
        
        # Load processed text data
        data_manager = DataManager()
        texts, metadatas = data_manager.load_processed_data(logger)
        
        if texts is None or len(texts) == 0:
            logger.error("No processed data found. Please run Step 1 first.")
            print("❌ No processed data found. Please run Step 1 first.")
            return False
        
        logger.info(f"Loaded {len(texts)} text chunks from processed data")
        
        # Validate Ollama connection before processing
        is_available, error_msg = self.validate_ollama_connection()
        if not is_available:
            logger.error(f"Ollama validation failed: {error_msg}")
            print(f"❌ Ollama Error: {error_msg}")
            self._print_ollama_troubleshooting()
            return False
        
        logger.info("Ollama connection validated successfully")
        print("✅ Ollama service is available")
        
        return self.create_embeddings_from_texts(texts, metadatas, logger)
    
    def create_embeddings_from_texts(self, 
                                   texts: List[str], 
                                   metadatas: List[Dict[str, Any]], 
                                   logger) -> bool:
        """
        Create vector embeddings from text chunks and metadata.
        
        Processes texts in batches for memory efficiency and provides
        progress feedback for large datasets.
        
        Args:
            texts: List of text chunks to embed
            metadatas: Corresponding metadata for each text chunk
            logger: Logger instance for status reporting
            
        Returns:
            True if embeddings created successfully, False otherwise
        """
        logger.info(f"Creating embeddings with Ollama model: {self.model_name}")
        print(f"🧠 Creating embeddings with {self.model_name}...")
        
        try:
            # Prepare batch processing
            total_chunks = len(texts)
            print(f"📊 Processing {total_chunks:,} text chunks in batches of {self.batch_size}")
            
            # Split into batches
            text_batches = [
                texts[i:i + self.batch_size] 
                for i in range(0, total_chunks, self.batch_size)
            ]
            metadata_batches = [
                metadatas[i:i + self.batch_size] 
                for i in range(0, len(metadatas), self.batch_size)
            ]
            
            total_batches = len(text_batches)
            logger.info(f"Processing {total_batches} batches")
            
            # Progress tracking
            print("Progress: [", end="", flush=True)
            vectordb = None
            
            # Process each batch
            for batch_idx, (batch_texts, batch_metas) in enumerate(zip(text_batches, metadata_batches)):
                logger.debug(f"Processing batch {batch_idx + 1}/{total_batches} "
                           f"({len(batch_texts)} chunks)")
                
                if vectordb is None:
                    # Create initial vector database
                    vectordb = Chroma.from_texts(
                        texts=batch_texts,
                        metadatas=batch_metas,
                        embedding=self.embeddings,
                        persist_directory=self.db_folder
                    )
                    logger.info(f"Created vector database at {self.db_folder}")
                else:
                    # Add to existing database
                    vectordb.add_texts(
                        texts=batch_texts,
                        metadatas=batch_metas
                    )
                
                # Update progress bar
                progress = int(50 * (batch_idx + 1) / total_batches)
                bar = "=" * progress + (" " * (50 - progress))
                print(f"\\r Progress: [{bar}]", end="", flush=True)
            
            print("] 100% ✅")
            
            # Store vectorstore reference
            self._vectorstore = vectordb
            
            # Success logging
            stats = self.get_embedding_stats()
            logger.info(f"Successfully created embeddings for {total_chunks:,} text chunks")
            logger.info(f"Vector database saved to: {self.db_folder}")
            
            print("✅ Step 2 Complete: Embedding Creation")
            print(f"💾 Vector database saved to '{self.db_folder}/'")
            if stats:
                print(f"📊 Database contains {stats.get('document_count', 'N/A'):,} documents")
            print("\\n🚀 Next step: python ingest.py --step3 (launch app)")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create embeddings: {e}")
            print(f"❌ Error creating embeddings: {e}")
            return False
    
    def load_vector_database(self) -> Optional[Chroma]:
        """
        Load existing vector database from persistent storage.
        
        Returns:
            Chroma vectorstore instance or None if loading failed
        """
        try:
            vectorstore = Chroma(
                persist_directory=self.db_folder,
                embedding_function=self.embeddings
            )
            return vectorstore
            
        except Exception as e:
            print(f"❌ Error loading vector database: {e}")
            return None
    
    def check_embeddings_exist(self) -> bool:
        """
        Check if vector database exists and contains data.
        
        Returns:
            True if database exists and has content, False otherwise
        """
        # Check if database directory exists
        if not os.path.exists(self.db_folder):
            return False
        
        # Check for database files
        try:
            db_files = [
                f for f in os.listdir(self.db_folder) 
                if f.startswith('chroma') or f.endswith('.sqlite3') or f.endswith('.parquet')
            ]
            return len(db_files) > 0
            
        except (OSError, PermissionError):
            return False
    
    def get_embedding_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get statistics about the vector database.
        
        Returns:
            Dictionary with database statistics or None if unavailable
        """
        if not self.check_embeddings_exist():
            return None
        
        try:
            vectorstore = self.vectorstore or self.load_vector_database()
            if vectorstore and vectorstore._collection:
                collection = vectorstore._collection
                return {
                    "document_count": collection.count(),
                    "database_path": self.db_folder,
                    "model_name": self.model_name,
                    "status": "ready"
                }
        except Exception as e:
            # Return basic info if detailed stats unavailable
            return {
                "status": "exists",
                "database_path": self.db_folder,
                "model_name": self.model_name,
                "error": str(e)
            }
        
        return None
    
    def clear_embeddings(self) -> bool:
        """
        Clear the vector database by removing all stored embeddings.
        
        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            if os.path.exists(self.db_folder):
                import shutil
                shutil.rmtree(self.db_folder)
                self._vectorstore = None
                return True
            return True
            
        except Exception as e:
            print(f"❌ Error clearing embeddings: {e}")
            return False
    
    def get_vector_search(self, 
                         query: str, 
                         k: int = 5,
                         filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search on the database.
        
        Args:
            query: Search query text
            k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of matching documents with scores and metadata
        """
        if not self.vectorstore:
            return []
        
        try:
            if filter_dict:
                results = self.vectorstore.similarity_search_with_score(
                    query, k=k, filter=filter_dict
                )
            else:
                results = self.vectorstore.similarity_search_with_score(query, k=k)
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": score
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Error during vector search: {e}")
            return []
    
    def _print_ollama_troubleshooting(self):
        """Print troubleshooting information for Ollama connectivity issues."""
        print("\\n🔧 To fix Ollama connectivity:")
        print("   1. Start Ollama service:")
        print("      $ ollama serve")
        print(f"   2. Ensure model is available:")
        print(f"      $ ollama pull {self.model_name}")
        print("   3. Verify service is running:")
        print(f"      $ curl {self.base_url}")
        print("   4. Check firewall settings and port availability")


# Convenience functions for backward compatibility and easy access
def create_embeddings_from_processed_data(logger) -> bool:
    """
    Convenience function for Step 2 of LocalWise pipeline.
    
    Args:
        logger: Logger instance
        
    Returns:
        True if embeddings created successfully
    """
    service = EmbeddingService()
    return service.create_embeddings_from_processed_data(logger)


def create_embeddings_from_texts(texts: List[str], 
                                metadatas: List[Dict[str, Any]], 
                                logger) -> bool:
    """
    Convenience function for creating embeddings from text lists.
    
    Args:
        texts: List of text chunks
        metadatas: List of metadata dictionaries
        logger: Logger instance
        
    Returns:
        True if successful
    """
    service = EmbeddingService()
    return service.create_embeddings_from_texts(texts, metadatas, logger)


def load_vector_database() -> Optional[Chroma]:
    """
    Convenience function for loading existing vector database.
    
    Returns:
        Chroma vectorstore instance or None
    """
    service = EmbeddingService()
    return service.load_vector_database()


def check_embeddings_exist() -> bool:
    """
    Convenience function for checking if embeddings exist.
    
    Returns:
        True if embeddings database exists
    """
    service = EmbeddingService()
    return service.check_embeddings_exist()


def get_embedding_stats() -> Optional[Dict[str, Any]]:
    """
    Convenience function for getting embedding statistics.
    
    Returns:
        Statistics dictionary or None
    """
    service = EmbeddingService()
    return service.get_embedding_stats()