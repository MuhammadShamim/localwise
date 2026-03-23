"""
LocalWise Data Module

This module provides comprehensive data management capabilities for LocalWise,
including document storage, file tracking, and change detection for efficient
incremental processing.

Data Management Components:
- data_manager: Storage and retrieval of processed text chunks and metadata
- file_manifest: File tracking with hash-based change detection
- change_detector: Intelligent incremental processing with change identification

Key Features:
- JSON-based intermediate storage for cross-platform compatibility
- MD5 hash-based file change detection for reliable incremental updates
- Comprehensive metadata tracking for processing history and statistics
- Atomic operations for data safety and integrity
- Performance optimization for large document collections

Usage Patterns:
1. Document Processing Pipeline:
   - FileManifest tracks all processed files with hashes and metadata
   - ChangeDetector identifies new/modified files for reprocessing
   - DataManager stores processed text chunks for embedding generation

2. Incremental Updates:
   - Only new and modified files are reprocessed
   - Existing embeddings are preserved for unchanged files
   - Manifest maintains complete processing history

3. Data Integrity:
   - Atomic file operations prevent corruption during updates
   - Hash validation ensures data consistency
   - Comprehensive error handling and recovery

Version: 1.0.0
Author: LocalWise Development Team
"""

from .data_manager import (
    DataManager,
    save_processed_data,
    load_processed_data,
    get_processed_data_info,
    clear_processed_data
)

from .file_manifest import (
    FileManifest,
    get_file_hash,
    load_file_manifest,
    save_file_manifest,
    update_file_in_manifest,
    remove_file_from_manifest
)

from .change_detector import (
    ChangeDetector,
    detect_file_changes,
    scan_folder_for_changes
)

__all__ = [
    # Data Management
    'DataManager',
    'save_processed_data',
    'load_processed_data', 
    'get_processed_data_info',
    'clear_processed_data',
    
    # File Manifest
    'FileManifest',
    'get_file_hash',
    'load_file_manifest',
    'save_file_manifest',
    'update_file_in_manifest',
    'remove_file_from_manifest',
    
    # Change Detection
    'ChangeDetector',
    'detect_file_changes',
    'scan_folder_for_changes'
]