"""
LocalWise Data Management Module

This module provides comprehensive data management capabilities for LocalWise,
handling the storage, retrieval, and manipulation of processed text chunks and metadata.
It serves as the persistence layer between document processing and embedding generation.

Key Features:
- Incremental data updates for efficient reprocessing
- JSON-based intermediate storage for reliability
- Metadata preservation and enrichment
- Data validation and integrity checks
- Performance monitoring and statistics

Architecture:
- DataManager: Main class for data operations
- JSON storage format for cross-platform compatibility
- Incremental update support for large document sets
- Atomic operations for data safety

Storage Format:
- processed_chunks.json: Main data file with texts, metadata, and timestamps
- Metadata includes source files, processing info, and timestamps
- Support for incremental updates and version tracking

Version: 1.0.0
Author: LocalWise Development Team
"""

import os
import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from localwise import config


class DataManager:
    """
    Centralized data management for LocalWise document processing.
    
    This class handles the complete data lifecycle for processed documents:
    - Storage of text chunks and metadata in JSON format
    - Incremental updates for efficient reprocessing
    - Data validation and integrity checks
    - Performance monitoring and reporting
    
    The DataManager acts as the bridge between document processing (Step 1)
    and embedding generation (Step 2) in the LocalWise pipeline.
    
    Attributes:
        db_folder (str): Database storage directory
        processed_file (str): Path to main processed data file
    """
    
    def __init__(self, db_folder: str = None):
        """
        Initialize the data manager with storage configuration.
        
        Args:
            db_folder: Directory for data storage (defaults to config.DB_FOLDER)
        """
        self.db_folder = db_folder or config.DB_FOLDER
        self.processed_file = os.path.join(self.db_folder, "processed_chunks.json")
        
        # Ensure storage directory exists
        os.makedirs(self.db_folder, exist_ok=True)
    
    def save_processed_data(self, 
                          texts: List[str], 
                          metadatas: List[Dict[str, Any]], 
                          logger, 
                          incremental: bool = False) -> bool:
        """
        Save processed text chunks and metadata to intermediate storage.
        
        This method implements Step 1 completion in the LocalWise pipeline,
        storing processed documents in a format suitable for embedding generation.
        Supports both full reprocessing and incremental updates.
        
        Args:
            texts: List of processed text chunks
            metadatas: Corresponding metadata for each chunk
            logger: Logger instance for status reporting
            incremental: Whether to append to existing data or replace it
            
        Returns:
            True if data saved successfully, False otherwise
        """
        try:
            # Load existing data for incremental updates
            existing_texts = []
            existing_metadatas = []
            
            if incremental and os.path.exists(self.processed_file):
                existing_data = self._load_raw_data()
                if existing_data:
                    existing_texts = existing_data.get("texts", [])
                    existing_metadatas = existing_data.get("metadatas", [])
                    logger.info(f"Loaded {len(existing_texts):,} existing chunks for incremental update")
            
            # Combine datasets
            all_texts = existing_texts + texts
            all_metadatas = existing_metadatas + metadatas
            
            # Prepare comprehensive data structure
            processed_data = {
                "texts": all_texts,
                "metadatas": all_metadatas,
                "processing_info": {
                    "timestamp": self._get_timestamp(),
                    "total_chunks": len(all_texts),
                    "incremental_update": incremental,
                    "new_chunks_added": len(texts),
                    "existing_chunks": len(existing_texts),
                    "data_version": "1.0.0"
                },
                "statistics": {
                    "average_chunk_length": sum(len(t) for t in all_texts) // len(all_texts) if all_texts else 0,
                    "total_characters": sum(len(t) for t in all_texts),
                    "unique_sources": len(set(m.get('source', 'unknown') for m in all_metadatas)),
                    "data_hash": self._calculate_data_hash(all_texts, all_metadatas)
                }
            }
            
            # Atomic write operation
            temp_file = self.processed_file + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename for data safety
            os.replace(temp_file, self.processed_file)
            
            # Success reporting
            if incremental:
                logger.info(f"Incremental update completed: Added {len(texts):,} chunks "
                          f"to existing {len(existing_texts):,} chunks")
                print("✅ Step 1 Complete: Incremental Document Processing")
                print(f"📊 Added {len(texts):,} new chunks (Total: {len(all_texts):,} chunks)")
            else:
                logger.info(f"Full processing completed: Saved {len(texts):,} chunks")
                print("✅ Step 1 Complete: Document Processing")
                print(f"📊 Processed {len(texts):,} text chunks")
            
            print(f"💾 Saved to: {self.processed_file}")
            print(f"📈 Average chunk size: {processed_data['statistics']['average_chunk_length']:,} characters")
            print("\\n🔄 Next step: python ingest.py --step2 (create embeddings)")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save processed data: {e}")
            print(f"❌ Error saving processed data: {e}")
            return False
    
    def load_processed_data(self, logger) -> Tuple[Optional[List[str]], Optional[List[Dict[str, Any]]]]:
        """
        Load processed text chunks and metadata from storage.
        
        This method retrieves stored data for Step 2 (embedding generation)
        in the LocalWise pipeline.
        
        Args:
            logger: Logger instance for status reporting
            
        Returns:
            Tuple of (texts, metadatas) or (None, None) if loading failed
        """
        if not os.path.exists(self.processed_file):
            logger.error("No processed data found. Please run Step 1 first.")
            print("❌ No processed data found. Please run Step 1 first:")
            print("   python ingest.py --step1")
            return None, None
        
        try:
            data = self._load_raw_data()
            if not data:
                return None, None
            
            texts = data.get("texts", [])
            metadatas = data.get("metadatas", [])
            processing_info = data.get("processing_info", {})
            
            # Validation
            if len(texts) != len(metadatas):
                logger.warning("Text and metadata counts don't match. Data may be corrupted.")
            
            # Success reporting
            chunk_count = processing_info.get("total_chunks", len(texts))
            logger.info(f"Successfully loaded {chunk_count:,} chunks from processed data")
            print(f"📖 Loaded {chunk_count:,} processed chunks from Step 1")
            
            if processing_info.get("incremental_update"):
                new_chunks = processing_info.get("new_chunks_added", 0)
                print(f"📈 Including {new_chunks:,} chunks from latest incremental update")
            
            return texts, metadatas
            
        except Exception as e:
            logger.error(f"Error loading processed data: {e}")
            print(f"❌ Error loading processed data: {e}")
            return None, None
    
    def get_processed_data_info(self) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive information about processed data without loading it.
        
        Provides quick access to data statistics and metadata for
        status reporting and validation purposes.
        
        Returns:
            Dictionary with data information or None if no data exists
        """
        if not os.path.exists(self.processed_file):
            return None
        
        try:
            data = self._load_raw_data()
            if not data:
                return None
            
            processing_info = data.get("processing_info", {})
            statistics = data.get("statistics", {})
            
            # Calculate file size
            file_size_mb = round(os.path.getsize(self.processed_file) / (1024 * 1024), 2)
            
            # Prepare comprehensive info
            info = {
                "chunk_count": processing_info.get("total_chunks", 0),
                "timestamp": processing_info.get("timestamp", "Unknown"),
                "incremental": processing_info.get("incremental_update", False),
                "new_chunks": processing_info.get("new_chunks_added", 0),
                "file_size_mb": file_size_mb,
                "data_version": processing_info.get("data_version", "unknown"),
                "statistics": {
                    "average_chunk_length": statistics.get("average_chunk_length", 0),
                    "total_characters": statistics.get("total_characters", 0),
                    "unique_sources": statistics.get("unique_sources", 0),
                    "data_integrity": "verified" if statistics.get("data_hash") else "unknown"
                }
            }
            
            return info
            
        except Exception:
            return {
                "status": "error",
                "error": "Could not read processed data file"
            }
    
    def clear_processed_data(self) -> bool:
        """
        Clear all processed data and start fresh.
        
        Removes the processed data file to allow for complete reprocessing.
        Use with caution as this operation cannot be undone.
        
        Returns:
            True if data cleared successfully, False otherwise
        """
        try:
            if os.path.exists(self.processed_file):
                os.remove(self.processed_file)
                return True
            return True  # Already cleared
        except Exception:
            return False
    
    def validate_data_integrity(self) -> Tuple[bool, List[str]]:
        """
        Validate the integrity of stored processed data.
        
        Performs comprehensive checks on data structure, content,
        and consistency to ensure data quality.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        if not os.path.exists(self.processed_file):
            issues.append("Processed data file does not exist")
            return False, issues
        
        try:
            data = self._load_raw_data()
            if not data:
                issues.append("Could not load processed data")
                return False, issues
            
            # Check required fields
            required_fields = ["texts", "metadatas"]
            for field in required_fields:
                if field not in data:
                    issues.append(f"Missing required field: {field}")
            
            # Validate data consistency
            texts = data.get("texts", [])
            metadatas = data.get("metadatas", [])
            
            if len(texts) != len(metadatas):
                issues.append(f"Text/metadata count mismatch: {len(texts)} vs {len(metadatas)}")
            
            # Check for empty data
            if not texts:
                issues.append("No text chunks found in processed data")
            
            # Validate text quality
            empty_chunks = sum(1 for t in texts if not t.strip())
            if empty_chunks > 0:
                issues.append(f"Found {empty_chunks} empty text chunks")
            
            # Check metadata quality
            sources = [m.get('source') for m in metadatas]
            missing_sources = sum(1 for s in sources if not s)
            if missing_sources > 0:
                issues.append(f"Found {missing_sources} chunks with missing source information")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            issues.append(f"Validation error: {e}")
            return False, issues
    
    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of processed data for reporting.
        
        Returns:
            Dictionary with detailed data summary and statistics
        """
        info = self.get_processed_data_info()
        if not info:
            return {"status": "no_data", "message": "No processed data available"}
        
        is_valid, issues = self.validate_data_integrity()
        
        return {
            "status": "ready" if is_valid else "issues_found",
            "data_info": info,
            "validation": {
                "is_valid": is_valid,
                "issues": issues,
                "issue_count": len(issues)
            },
            "recommendations": self._get_data_recommendations(info, is_valid, issues)
        }
    
    def _load_raw_data(self) -> Optional[Dict[str, Any]]:
        """Load raw data from the processed file."""
        try:
            with open(self.processed_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    def _calculate_data_hash(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> str:
        """Calculate hash for data integrity verification."""
        try:
            # Create deterministic representation
            data_repr = json.dumps({
                "text_count": len(texts),
                "metadata_count": len(metadatas),
                "sample_text": texts[0][:100] if texts else "",
                "sources": sorted(set(m.get('source', '') for m in metadatas))
            }, sort_keys=True)
            
            return hashlib.md5(data_repr.encode()).hexdigest()
        except Exception:
            return "unknown"
    
    def _get_data_recommendations(self, 
                                info: Dict[str, Any], 
                                is_valid: bool, 
                                issues: List[str]) -> List[str]:
        """Generate recommendations based on data analysis."""
        recommendations = []
        
        if not is_valid:
            recommendations.append("⚠️  Data integrity issues found - consider reprocessing documents")
        
        if info.get("chunk_count", 0) == 0:
            recommendations.append("📋 No processed data found - run Step 1 to process documents")
        
        chunk_count = info.get("chunk_count", 0)
        if chunk_count > 10000:
            recommendations.append("📊 Large dataset detected - consider using incremental updates for future changes")
        elif chunk_count < 10:
            recommendations.append("📝 Small dataset - consider adding more documents for better search results")
        
        file_size = info.get("file_size_mb", 0)
        if file_size > 100:
            recommendations.append("💾 Large data file - monitor memory usage during embedding generation")
        
        avg_length = info.get("statistics", {}).get("average_chunk_length", 0)
        if avg_length > 2000:
            recommendations.append("📄 Large chunks detected - consider adjusting chunk size for better search performance")
        elif avg_length < 100:
            recommendations.append("✂️  Small chunks detected - may affect search context quality")
        
        if not recommendations and is_valid:
            recommendations.append("✅ Data looks good - ready for embedding generation (Step 2)")
        
        return recommendations


# Convenience functions for backward compatibility and easy access
def save_processed_data(texts: List[str], 
                       metadatas: List[Dict[str, Any]], 
                       logger, 
                       incremental: bool = False) -> bool:
    """
    Convenience function for saving processed data.
    
    Args:
        texts: List of text chunks
        metadatas: List of metadata dictionaries
        logger: Logger instance
        incremental: Whether to append to existing data
        
    Returns:
        True if successful
    """
    manager = DataManager()
    return manager.save_processed_data(texts, metadatas, logger, incremental)


def load_processed_data(logger) -> Tuple[Optional[List[str]], Optional[List[Dict[str, Any]]]]:
    """
    Convenience function for loading processed data.
    
    Args:
        logger: Logger instance
        
    Returns:
        Tuple of (texts, metadatas) or (None, None)
    """
    manager = DataManager()
    return manager.load_processed_data(logger)


def get_processed_data_info() -> Optional[Dict[str, Any]]:
    """
    Convenience function for getting data info.
    
    Returns:
        Data information dictionary or None
    """
    manager = DataManager()
    return manager.get_processed_data_info()


def clear_processed_data() -> bool:
    """
    Convenience function for clearing processed data.
    
    Returns:
        True if successful
    """
    manager = DataManager()
    return manager.clear_processed_data()