"""
LocalWise File Manifest Management

This module provides comprehensive file tracking and change detection capabilities
for the LocalWise document processing system. It maintains a manifest of all
processed files with metadata for efficient incremental updates.

Key Features:
- MD5 hash-based change detection for reliable file tracking
- Comprehensive file metadata storage (size, modification time, type)
- Atomic manifest updates for data safety
- Performance optimization for large file collections
- Support for file lifecycle management

Architecture:
- FileManifest: Main class for manifest operations
- JSON-based storage for cross-platform compatibility
- Atomic file operations for data integrity
- Efficient hash calculation with chunked reading

Use Cases:
- Incremental document processing (only process changed files)
- File dependency tracking for cache invalidation
- Processing history and audit trails
- Performance optimization for large document sets

Version: 1.0.0
Author: LocalWise Development Team
"""

import os
import hashlib
import json
from typing import Dict, Any, Optional, List, Tuple, Set
from datetime import datetime
from pathlib import Path

from localwise import config


class FileManifest:
    """
    Comprehensive file manifest management for LocalWise document processing.
    
    This class maintains a detailed record of all processed files with
    metadata including hashes, timestamps, and processing information.
    It enables efficient incremental processing by tracking file changes.
    
    Features:
    - Fast MD5 hash-based change detection
    - Comprehensive metadata tracking
    - Atomic manifest updates for safety
    - Efficient bulk operations
    - File lifecycle management
    
    Attributes:
        db_folder (str): Database storage directory
        manifest_file (str): Path to manifest JSON file
    """
    
    def __init__(self, db_folder: str = None):
        """
        Initialize the file manifest with storage configuration.
        
        Args:
            db_folder: Directory for manifest storage (defaults to config.DB_FOLDER)
        """
        self.db_folder = db_folder or config.DB_FOLDER
        self.manifest_file = os.path.join(self.db_folder, "file_manifest.json")
        
        # Ensure storage directory exists
        os.makedirs(self.db_folder, exist_ok=True)
    
    def get_file_hash(self, file_path: str) -> Optional[str]:
        """
        Calculate MD5 hash of a file for change detection.
        
        Uses chunked reading for memory efficiency with large files.
        
        Args:
            file_path: Path to the file to hash
            
        Returns:
            MD5 hash string or None if file cannot be read
        """
        hash_md5 = hashlib.md5()
        
        try:
            with open(file_path, "rb") as f:
                # Read in 64KB chunks for memory efficiency
                for chunk in iter(lambda: f.read(65536), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
            
        except (IOError, OSError, PermissionError) as e:
            print(f"⚠️  Cannot hash file {file_path}: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error hashing {file_path}: {e}")
            return None
    
    def load_file_manifest(self) -> Dict[str, Dict[str, Any]]:
        """
        Load the file manifest from storage.
        
        Returns:
            Dictionary mapping file paths to their metadata, or empty dict if none exists
        """
        if not os.path.exists(self.manifest_file):
            return {}
        
        try:
            with open(self.manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
                
            # Validate manifest structure
            if isinstance(manifest, dict):
                return manifest
            else:
                print("⚠️  Invalid manifest format, starting fresh")
                return {}
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Corrupt manifest file, starting fresh: {e}")
            return {}
        except Exception as e:
            print(f"❌ Error loading manifest: {e}")
            return {}
    
    def save_file_manifest(self, manifest: Dict[str, Dict[str, Any]]) -> bool:
        """
        Save the file manifest to storage with atomic write operation.
        
        Args:
            manifest: Dictionary of file metadata to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Add manifest metadata
            manifest_with_meta = {
                "_manifest_info": {
                    "version": "1.0.0",
                    "last_updated": datetime.now().isoformat(),
                    "file_count": len(manifest),
                    "total_size": sum(entry.get("size", 0) for entry in manifest.values())
                }
            }
            manifest_with_meta.update(manifest)
            
            # Atomic write operation
            temp_file = self.manifest_file + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(manifest_with_meta, f, indent=2, ensure_ascii=False)
            
            # Atomic rename for data safety
            os.replace(temp_file, self.manifest_file)
            return True
            
        except Exception as e:
            print(f"❌ Error saving manifest: {e}")
            return False
    
    def update_file_in_manifest(self, file_path: str, file_type: str) -> bool:
        """
        Update or add a single file entry in the manifest.
        
        Args:
            file_path: Path to the file to update
            file_type: Type of file (e.g., 'pdf', 'txt', 'python')
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            # Get file statistics
            stat = os.stat(file_path)
            file_hash = self.get_file_hash(file_path)
            
            if file_hash is None:
                return False  # Cannot hash file
            
            # Load current manifest
            manifest = self.load_file_manifest()
            
            # Create comprehensive file entry
            manifest[file_path] = {
                "type": file_type,
                "hash": file_hash,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "modified_iso": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "last_processed": datetime.now().isoformat(),
                "processing_count": manifest.get(file_path, {}).get("processing_count", 0) + 1,
                "file_extension": Path(file_path).suffix.lower(),
                "file_name": Path(file_path).name
            }
            
            # Save updated manifest
            return self.save_file_manifest(manifest)
            
        except (OSError, IOError) as e:
            print(f"⚠️  Cannot access file {file_path}: {e}")
            return False
        except Exception as e:
            print(f"❌ Error updating manifest for {file_path}: {e}")
            return False
    
    def remove_file_from_manifest(self, file_path: str) -> bool:
        """
        Remove a file entry from the manifest.
        
        Args:
            file_path: Path to the file to remove
            
        Returns:
            True if removed successfully, False if file not found or error
        """
        try:
            manifest = self.load_file_manifest()
            
            if file_path in manifest:
                del manifest[file_path]
                return self.save_file_manifest(manifest)
            else:
                return False  # File not in manifest
                
        except Exception as e:
            print(f"❌ Error removing {file_path} from manifest: {e}")
            return False
    
    def bulk_update_manifest(self, 
                            file_updates: Dict[str, str]) -> Tuple[int, int]:
        """
        Update multiple files in the manifest efficiently.
        
        Args:
            file_updates: Dictionary mapping file_path to file_type
            
        Returns:
            Tuple of (successful_updates, failed_updates)
        """
        manifest = self.load_file_manifest()
        successful = 0
        failed = 0
        
        for file_path, file_type in file_updates.items():
            try:
                stat = os.stat(file_path)
                file_hash = self.get_file_hash(file_path)
                
                if file_hash is not None:
                    manifest[file_path] = {
                        "type": file_type,
                        "hash": file_hash,
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                        "modified_iso": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "last_processed": datetime.now().isoformat(),
                        "processing_count": manifest.get(file_path, {}).get("processing_count", 0) + 1,
                        "file_extension": Path(file_path).suffix.lower(),
                        "file_name": Path(file_path).name
                    }
                    successful += 1
                else:
                    failed += 1
                    
            except Exception:
                failed += 1
        
        # Save all updates at once
        if successful > 0:
            self.save_file_manifest(manifest)
        
        return successful, failed
    
    def get_file_status(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed status information for a specific file.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            Dictionary with file status information
        """
        manifest = self.load_file_manifest()
        
        # Check if file exists in manifest
        if file_path not in manifest:
            return {
                "in_manifest": False,
                "exists": os.path.exists(file_path),
                "status": "new"
            }
        
        entry = manifest[file_path]
        current_hash = self.get_file_hash(file_path) if os.path.exists(file_path) else None
        
        return {
            "in_manifest": True,
            "exists": os.path.exists(file_path),
            "stored_hash": entry.get("hash"),
            "current_hash": current_hash,
            "changed": current_hash != entry.get("hash") if current_hash else False,
            "last_processed": entry.get("last_processed"),
            "processing_count": entry.get("processing_count", 0),
            "file_type": entry.get("type"),
            "file_size": entry.get("size", 0),
            "status": self._determine_file_status(entry, current_hash, os.path.exists(file_path))
        }
    
    def get_changed_files(self, file_paths: List[str]) -> Tuple[List[str], List[str], List[str]]:
        """
        Identify new, modified, and deleted files from a list of current files.
        
        Args:
            file_paths: List of current file paths to check
            
        Returns:
            Tuple of (new_files, modified_files, deleted_files)
        """
        manifest = self.load_file_manifest()
        current_files = set(file_paths)
        manifest_files = set(manifest.keys()) - {"_manifest_info"}  # Exclude metadata
        
        # Find new and modified files
        new_files = []
        modified_files = []
        
        for file_path in current_files:
            if file_path not in manifest:
                new_files.append(file_path)
            else:
                # Check if file has changed
                current_hash = self.get_file_hash(file_path)
                stored_hash = manifest[file_path].get("hash")
                
                if current_hash and current_hash != stored_hash:
                    modified_files.append(file_path)
        
        # Find deleted files
        deleted_files = [f for f in manifest_files if f not in current_files]
        
        return new_files, modified_files, deleted_files
    
    def cleanup_manifest(self) -> Tuple[int, int]:
        """
        Clean up manifest by removing entries for non-existent files.
        
        Returns:
            Tuple of (removed_count, remaining_count)
        """
        manifest = self.load_file_manifest()
        removed = 0
        
        # Find files that no longer exist
        files_to_remove = []
        for file_path in manifest:
            if file_path == "_manifest_info":  # Skip metadata
                continue
                
            if not os.path.exists(file_path):
                files_to_remove.append(file_path)
        
        # Remove non-existent files
        for file_path in files_to_remove:
            del manifest[file_path]
            removed += 1
        
        # Save cleaned manifest
        if removed > 0:
            self.save_file_manifest(manifest)
        
        remaining = len(manifest) - (1 if "_manifest_info" in manifest else 0)
        return removed, remaining
    
    def get_manifest_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the file manifest.
        
        Returns:
            Dictionary with detailed manifest statistics
        """
        manifest = self.load_file_manifest()
        
        if not manifest:
            return {"status": "empty", "file_count": 0}
        
        # Extract file entries (excluding metadata)
        file_entries = {k: v for k, v in manifest.items() if k != "_manifest_info"}
        
        if not file_entries:
            return {"status": "empty", "file_count": 0}
        
        # Calculate statistics
        file_types = {}
        total_size = 0
        missing_files = 0
        
        for file_path, entry in file_entries.items():
            file_type = entry.get("type", "unknown")
            file_types[file_type] = file_types.get(file_type, 0) + 1
            total_size += entry.get("size", 0)
            
            if not os.path.exists(file_path):
                missing_files += 1
        
        return {
            "status": "ready",
            "file_count": len(file_entries),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": file_types,
            "missing_files": missing_files,
            "manifest_info": manifest.get("_manifest_info", {}),
            "health": "good" if missing_files == 0 else "needs_cleanup"
        }
    
    def _determine_file_status(self, 
                              entry: Dict[str, Any], 
                              current_hash: Optional[str], 
                              exists: bool) -> str:
        """Determine the status of a file based on manifest entry and current state."""
        if not exists:
            return "deleted"
        elif current_hash is None:
            return "error"
        elif current_hash != entry.get("hash"):
            return "modified"
        else:
            return "unchanged"


# Convenience functions for backward compatibility and easy access
def get_file_hash(file_path: str) -> Optional[str]:
    """
    Convenience function for calculating file hash.
    
    Args:
        file_path: Path to the file
        
    Returns:
        MD5 hash string or None
    """
    manifest = FileManifest()
    return manifest.get_file_hash(file_path)


def load_file_manifest() -> Dict[str, Dict[str, Any]]:
    """
    Convenience function for loading file manifest.
    
    Returns:
        Manifest dictionary
    """
    manifest = FileManifest()
    return manifest.load_file_manifest()


def save_file_manifest(manifest_data: Dict[str, Dict[str, Any]]) -> bool:
    """
    Convenience function for saving file manifest.
    
    Args:
        manifest_data: Manifest dictionary to save
        
    Returns:
        True if successful
    """
    manifest = FileManifest()
    return manifest.save_file_manifest(manifest_data)


def update_file_in_manifest(file_path: str, file_type: str) -> bool:
    """
    Convenience function for updating single file in manifest.
    
    Args:
        file_path: Path to the file
        file_type: Type of file
        
    Returns:
        True if successful
    """
    manifest = FileManifest()
    return manifest.update_file_in_manifest(file_path, file_type)


def remove_file_from_manifest(file_path: str) -> bool:
    """
    Convenience function for removing file from manifest.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if successful
    """
    manifest = FileManifest()
    return manifest.remove_file_from_manifest(file_path)