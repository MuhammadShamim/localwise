"""
LocalWise Test Suite Configuration

This file provides test configuration and fixtures for the LocalWise test suite.
It includes pytest fixtures, test data setup, and common testing utilities.
"""

import pytest
import tempfile
import os
import shutil
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import MagicMock

# Test configuration
TEST_DATA_DIR = Path(__file__).parent / "fixtures"
SAMPLE_DOCUMENTS_DIR = TEST_DATA_DIR / "sample_documents"
TEST_CONFIG = {
    "DOCS_FOLDER": "test_documents",
    "DB_FOLDER": "test_db", 
    "OLLAMA_MODEL": "llama3.2:latest",
    "OLLAMA_BASE_URL": "http://localhost:11434",
    "CHUNK_SIZE": 100,  # Smaller for testing
    "CHUNK_OVERLAP": 10,
    "NUM_SOURCES": 2,
    "MAX_FILE_SIZE_MB": 5,  # Smaller for testing
}


@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Provide test configuration settings."""
    return TEST_CONFIG.copy()


@pytest.fixture(scope="function")
def temp_workspace(test_config):
    """
    Create a temporary workspace for testing.
    
    Yields:
        str: Path to temporary workspace directory
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test directory structure
        workspace = Path(temp_dir)
        docs_dir = workspace / test_config["DOCS_FOLDER"]
        db_dir = workspace / test_config["DB_FOLDER"]
        
        docs_dir.mkdir()
        db_dir.mkdir()
        
        # Create sample documents
        _create_sample_documents(docs_dir)
        
        yield str(workspace)


@pytest.fixture(scope="function")
def sample_text_files(temp_workspace, test_config):
    """
    Create sample text files for testing.
    
    Returns:
        List[str]: List of file paths created
    """
    docs_dir = Path(temp_workspace) / test_config["DOCS_FOLDER"]
    files = []
    
    # Create various file types
    test_files = {
        "sample.txt": "This is a sample text document for testing LocalWise functionality.",
        "data.csv": "name,age,city\nJohn,25,NYC\nJane,30,SF\nBob,35,LA",
        "config.json": '{"app": "LocalWise", "version": "1.0.0", "features": ["RAG", "AI", "Privacy"]}',
        "settings.yaml": "database:\n  host: localhost\n  port: 5432\nlogging:\n  level: INFO",
        "structure.xml": '<?xml version="1.0"?>\n<config>\n  <app>LocalWise</app>\n  <version>1.0.0</version>\n</config>'
    }
    
    for filename, content in test_files.items():
        file_path = docs_dir / filename
        file_path.write_text(content, encoding="utf-8")
        files.append(str(file_path))
    
    return files


@pytest.fixture(scope="function")
def mock_ollama_service():
    """
    Mock Ollama service for testing without requiring actual AI service.
    
    Returns:
        MagicMock: Mock Ollama service
    """
    mock_service = MagicMock()
    mock_service.embeddings.return_value = [[0.1, 0.2, 0.3, 0.4, 0.5]] * 10  # Mock embeddings
    mock_service.generate.return_value = {
        "response": "This is a test response from LocalWise AI assistant."
    }
    mock_service.list.return_value = {
        "models": [{"name": "llama3.2:latest"}]
    }
    return mock_service


@pytest.fixture(scope="function")
def mock_vectorstore():
    """
    Mock ChromaDB vectorstore for testing.
    
    Returns:
        MagicMock: Mock vectorstore
    """
    mock_store = MagicMock()
    mock_store.similarity_search.return_value = [
        MagicMock(page_content="Sample document content for testing", metadata={"source": "test.txt"}),
        MagicMock(page_content="Another test document content", metadata={"source": "test2.txt"})
    ]
    mock_store.add_documents.return_value = None
    return mock_store


@pytest.fixture(scope="function")
def sample_processed_chunks():
    """
    Provide sample processed document chunks for testing.
    
    Returns:
        List[Dict]: Sample processed chunks
    """
    return [
        {
            "content": "This is the first chunk of sample document content for testing.",
            "metadata": {
                "source": "sample.txt",
                "chunk_id": "chunk_001",
                "file_type": "txt",
                "timestamp": "2024-12-21T10:00:00"
            }
        },
        {
            "content": "This is the second chunk with different content for comprehensive testing.",
            "metadata": {
                "source": "sample.txt", 
                "chunk_id": "chunk_002",
                "file_type": "txt",
                "timestamp": "2024-12-21T10:00:01"
            }
        }
    ]


def _create_sample_documents(docs_dir: Path) -> None:
    """Helper function to create sample documents for testing."""
    # Create PDF placeholder (would need actual PDF in real scenario)
    (docs_dir / "sample.pdf").write_bytes(b"%PDF-1.4 mock content")
    
    # Create code files
    (docs_dir / "test.py").write_text("def hello():\n    return 'Hello from LocalWise!'")
    (docs_dir / "script.js").write_text("function test() { return 'JavaScript test'; }")
    
    # Create subdirectory with files
    sub_dir = docs_dir / "subdocs"
    sub_dir.mkdir()
    (sub_dir / "nested.txt").write_text("This is a nested document for testing recursive scanning.")


# Test utilities
class TestHelper:
    """Helper class with utilities for testing LocalWise components."""
    
    @staticmethod
    def create_test_file(path: str, content: str, encoding: str = "utf-8") -> None:
        """Create a test file with specified content."""
        Path(path).write_text(content, encoding=encoding)
    
    @staticmethod
    def count_files_in_directory(directory: str, pattern: str = "*") -> int:
        """Count files matching pattern in directory."""
        return len(list(Path(directory).glob(pattern)))
    
    @staticmethod
    def assert_file_exists(file_path: str) -> None:
        """Assert that a file exists."""
        assert Path(file_path).exists(), f"File {file_path} should exist"
    
    @staticmethod
    def assert_file_not_exists(file_path: str) -> None:
        """Assert that a file does not exist."""
        assert not Path(file_path).exists(), f"File {file_path} should not exist"


# Custom pytest markers
pytest_plugins = []


# Test data constants
SAMPLE_QUERIES = [
    "What is LocalWise?",
    "How do I process documents?",
    "What file types are supported?",
    "How does the AI embedding work?",
    "Can I use LocalWise offline?"
]

SAMPLE_RESPONSES = [
    "LocalWise is a professional AI knowledge assistant that transforms documents into intelligent, searchable knowledge bases.",
    "You can process documents using the CLI command: python -m localwise.cli process -d documents/",
    "LocalWise supports 40+ file types including PDF, DOC, CSV, JSON, XML, code files, and more.",
    "AI embeddings are created using local Ollama service with vector storage in ChromaDB for privacy.",
    "Yes, LocalWise runs entirely offline with no cloud dependencies or API keys required."
]