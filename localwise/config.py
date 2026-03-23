"""
🧠 LocalWise v1.0.0 - Centralized Configuration Module

Developed by: Akhtar Shamim (WWEX Group)
Version: 1.0.0
License: MIT

Description:
    Clean, simple configuration for LocalWise AI knowledge assistant.
    Provides core settings and validation for reliable document processing.

Components:
    - Core application settings
    - Ollama service validation
    - Input sanitization functions
    - Directory and database validation
    - Basic logging configuration

Usage:
    from localwise import config
    logger = config.setup_logging()
    is_valid, msg = config.validate_ollama_connection()
"""

import os
import logging
import requests
from datetime import datetime
from typing import Optional

# ─────────────────────────────────────────────
# CORE SETTINGS
# ─────────────────────────────────────────────
DOCS_FOLDER = "documents"     # Folder where your documents and files live
DB_FOLDER = "db"        # Where the database will be saved
OLLAMA_MODEL = "llama3.2:latest"        # Must match what you pulled with: ollama pull llama3.2
OLLAMA_BASE_URL = "http://localhost:11434"  # Default Ollama endpoint
CHUNK_SIZE = 500                 # How many characters per chunk
CHUNK_OVERLAP = 50               # Overlap between chunks (helps with context)
NUM_SOURCES = 4                  # Number of source chunks to retrieve per query

# ─────────────────────────────────────────────
# PERFORMANCE & SAFETY LIMITS
# ─────────────────────────────────────────────
MAX_MEMORY_MESSAGES = 20         # Max conversation history length
MAX_QUERY_LENGTH = 1000          # Max characters in user input
MAX_FILE_SIZE_MB = 50           # Max file size to process
CHUNK_BATCH_SIZE = 100          # Process documents in batches
REQUEST_TIMEOUT = 30            # Timeout for Ollama requests in seconds

# ─────────────────────────────────────────────
# LOGGING CONFIGURATION
# ─────────────────────────────────────────────
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "localwise.log"  # Main application log file

def setup_logging() -> logging.Logger:
    """
    Configure logging for LocalWise application.
    
    Sets up dual logging output:
    - File logging: Persistent audit trail in localwise.log
    - Console logging: Real-time feedback during development
    
    Log format includes:
    - Timestamp with millisecond precision
    - Logger name for component identification  
    - Log level for filtering
    - Detailed message content
    
    Returns:
        logging.Logger: Configured logger instance for LocalWise
        
    Example:
        >>> logger = setup_logging()
        >>> logger.info("LocalWise initialization started")
    """
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),  # UTF-8 for international characters
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger('LocalWise')
    logger.info("LocalWise logging system initialized")
    return logger


def validate_ollama_connection() -> tuple[bool, Optional[str]]:
    """
    Validate Ollama service connectivity and model availability.
    
    This function performs health checks on the Ollama service:
    1. Tests HTTP connectivity to the Ollama API endpoint
    2. Verifies the service is responding correctly
    3. Confirms the required model is installed and available
    4. Provides detailed error messaging for troubleshooting
    
    Returns:
        tuple[bool, Optional[str]]: 
            - bool: True if Ollama is available and model exists, False otherwise
            - str: None if successful, otherwise detailed error message
            
    Example:
        >>> is_available, error_msg = validate_ollama_connection()
        >>> if not is_available:
        ...     logger.error(f"Ollama validation failed: {error_msg}")
    """
    try:
        # Check if Ollama service is running
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code != 200:
            return False, f"Ollama service not responding (status: {response.status_code})"
        
        # Check if our model is available
        models = response.json().get("models", [])
        model_names = [model["name"] for model in models]
        
        if OLLAMA_MODEL not in model_names:
            available_models = ", ".join(model_names) if model_names else "none"
            return False, f"Model '{OLLAMA_MODEL}' not found. Available models: {available_models}"
        
        return True, None
        
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to Ollama service. Is Ollama running?"
    except requests.exceptions.Timeout:
        return False, "Ollama service timeout. Service may be overloaded."
    except Exception as e:
        return False, f"Unexpected error checking Ollama: {str(e)}"


def validate_directories() -> tuple[bool, Optional[str]]:
    """
    Validate that required directories exist and are accessible.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        # Check if docs folder exists
        if not os.path.exists(DOCS_FOLDER):
            os.makedirs(DOCS_FOLDER)
            return True, f"Created '{DOCS_FOLDER}' directory"
        
        # Check if it's readable
        if not os.access(DOCS_FOLDER, os.R_OK):
            return False, f"Cannot read from '{DOCS_FOLDER}' directory"
        
        return True, None
    
    except PermissionError:
        return False, f"Permission denied accessing '{DOCS_FOLDER}'"
    except Exception as e:
        return False, f"Error validating directories: {str(e)}"


def validate_database_exists() -> tuple[bool, Optional[str]]:
    """
    Check if the ChromaDB database exists and appears valid.
    
    Returns:
        tuple: (exists, error_message)
    """
    if not os.path.exists(DB_FOLDER):
        return False, "No document database found. Run 'python ingest.py' first."
    
    # Check for ChromaDB files
    required_files = ["chroma.sqlite3"]
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(os.path.join(DB_FOLDER, file)):
            missing_files.append(file)
    
    if missing_files:
        return False, f"Database appears corrupted. Missing: {', '.join(missing_files)}"
    
    return True, None


def sanitize_input(user_input: str) -> str:
    """
    Sanitize user input for safety.
    
    Args:
        user_input: Raw user input string
        
    Returns:
        str: Sanitized input
    """
    if not user_input:
        return ""
    
    # Remove control characters and limit length
    sanitized = ''.join(char for char in user_input if ord(char) >= 32 or char in '\n\r\t')
    sanitized = sanitized[:MAX_QUERY_LENGTH]
    
    return sanitized.strip()


def get_timestamp() -> str:
    """Get current timestamp for tracking processing steps."""
    return datetime.now().isoformat()


# ─────────────────────────────────────────────
# PACKAGE PATHS AND DATABASE CONFIGURATION
# ─────────────────────────────────────────────

# For package-level access from the main localwise directory
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "my_vectordb")
PROCESSED_CHUNKS_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "processed_chunks.json")

def get_database_path() -> str:
    """Get the absolute path to the vector database."""
    return os.path.abspath(DATABASE_PATH)

def get_processed_chunks_path() -> str:
    """Get the absolute path to the processed chunks file."""
    return os.path.abspath(PROCESSED_CHUNKS_PATH)