"""
LocalWise Core Module

This module contains the core functionality of LocalWise:
- File processing and document extraction
- AI embedding generation and management
- Intelligent document querying and retrieval

Core Components:
- file_processors: Extensible file processing system for 40+ file types
- embedding_service: AI-powered text embedding generation using Ollama
- query_engine: Retrieval Augmented Generation (RAG) for document queries

Version: 1.0.0
"""

from .file_processors import (
    FileProcessor,
    FileProcessorRegistry,
    TextFileProcessor,
    PDFProcessor,
    CSVProcessor,
    JSONProcessor,
    YAMLProcessor,
    XMLProcessor,
    OfficeProcessor,
    RTFProcessor
)

from .embedding_service import EmbeddingService
from .query_engine import QueryEngine

__all__ = [
    # File Processing
    'FileProcessor',
    'FileProcessorRegistry', 
    'TextFileProcessor',
    'PDFProcessor',
    'CSVProcessor',
    'JSONProcessor',
    'YAMLProcessor',
    'XMLProcessor',
    'OfficeProcessor',
    'RTFProcessor',
    
    # AI Services
    'EmbeddingService',
    'QueryEngine'
]