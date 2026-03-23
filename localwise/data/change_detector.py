"""
LocalWise Change Detection System

This module provides intelligent file change detection for incremental document
processing in LocalWise. It efficiently identifies new, modified, and deleted
files to minimize unnecessary reprocessing and improve performance.

Key Features:
- Hash-based change detection for reliable file comparison
- Support for force refresh and incremental processing modes
- Integration with file processor registry for type-aware scanning
- Efficient manifest-based tracking for large document collections
- Performance optimization with quick change scanning

Architecture:
- ChangeDetector: Main class for change detection operations
- Integration with FileManifest for persistent tracking
- FileProcessorRegistry integration for comprehensive file type support
- Bulk operations for performance optimization

Use Cases:
- Incremental document processing (only process changed files)
- Build system optimization (avoid reprocessing unchanged files)
- Content management (track document lifecycle)
- Performance optimization (reduce processing time)

Version: 1.0.0
Author: LocalWise Development Team
"""

import os
import glob
from typing import Dict, List, Any, Tuple, Set
from datetime import datetime
from pathlib import Path

from .file_manifest import FileManifest
from ..core.file_processors import FileProcessorRegistry


class ChangeDetector:
    """
    Intelligent file change detection system for LocalWise document processing.
    
    This class provides comprehensive change detection capabilities including
    identification of new, modified, and deleted files since the last processing
    run. It integrates with the file manifest system for persistent tracking.
    
    Features:
    - Hash-based change detection for accurate comparison
    - Support for different processing modes (incremental, force refresh)
    - Efficient scanning with early termination optimization
    - Comprehensive file type support via processor registry
    - Detailed change reporting and statistics
    
    Attributes:
        folder (str): Root folder being monitored for changes
        file_manifest (FileManifest): Manifest manager for tracking files
        processor_registry (FileProcessorRegistry): Registry for file type detection
    """
    
    def __init__(self, 
                 folder: str, 
                 db_folder: str = None):
        """
        Initialize change detector for the specified folder.
        
        Args:
            folder: Root folder to monitor for file changes
            db_folder: Database folder for manifest storage (optional)
        """
        self.folder = os.path.abspath(folder)
        self.file_manifest = FileManifest(db_folder)
        self.processor_registry = FileProcessorRegistry()
        
        # Ensure folder exists
        if not os.path.exists(self.folder):
            raise ValueError(f"Folder does not exist: {self.folder}")
    
    def detect_file_changes(self, 
                          logger, 
                          force_refresh: bool = False,
                          include_hidden: bool = False) -> Dict[str, List[str]]:
        """
        Detect new, modified, and deleted files since last processing.
        
        This method performs a comprehensive comparison between the current
        state of files and the stored manifest to identify changes.
        
        Args:
            logger: Logger instance for status reporting
            force_refresh: If True, treat all files as new (full reprocessing)
            include_hidden: Whether to include hidden files and folders
            
        Returns:
            Dictionary with 'new', 'modified', 'deleted', and 'to_process' file lists
        """
        logger.info("🔍 Detecting file changes for incremental processing...")
        
        # Load existing manifest
        manifest = self.file_manifest.load_file_manifest()
        
        # Scan current files
        current_files = self._scan_current_files(logger, include_hidden)
        
        # Determine file changes
        if force_refresh:
            logger.info("🔄 Force refresh mode: processing all files")
            new_files = list(current_files.keys())
            modified_files = []
            deleted_files = []
        else:
            new_files, modified_files, deleted_files = self._compare_with_manifest(
                current_files, manifest, logger
            )
        
        # Update manifest with current state
        self._update_manifest_for_processed_files(
            current_files, new_files + modified_files, deleted_files
        )
        
        # Prepare results
        results = {
            "new": new_files,
            "modified": modified_files,
            "deleted": deleted_files,
            "to_process": new_files + modified_files,
            "statistics": {
                "total_current": len(current_files),
                "total_changes": len(new_files) + len(modified_files) + len(deleted_files),
                "manifest_size": len(manifest)
            }
        }
        
        # Report results
        self._log_change_detection_results(logger, results)
        
        return results
    
    def quick_change_scan(self, logger) -> bool:
        """
        Perform a quick scan to check if any files have changed.
        
        This is an optimization method for quickly determining if incremental
        processing is needed without performing a full scan.
        
        Args:
            logger: Logger instance for error reporting
            
        Returns:
            True if changes detected, False if no changes found
        """
        try:
            manifest = self.file_manifest.load_file_manifest()
            
            # Quick check: sample some tracked files
            tracked_files = list(manifest.keys())
            if "_manifest_info" in tracked_files:
                tracked_files.remove("_manifest_info")
            
            # Check a sample of tracked files for modifications
            sample_size = min(10, len(tracked_files))
            for file_path in tracked_files[:sample_size]:
                if not os.path.exists(file_path):
                    logger.debug(f"Quick scan: Found deleted file {file_path}")
                    return True
                
                current_hash = self.file_manifest.get_file_hash(file_path)
                stored_hash = manifest[file_path].get("hash")
                
                if current_hash and current_hash != stored_hash:
                    logger.debug(f"Quick scan: Found modified file {file_path}")
                    return True
            
            # Quick check: look for new files in common locations
            new_files_found = self._quick_scan_for_new_files(manifest, logger)
            if new_files_found:
                return True
            
            logger.debug("Quick scan: No changes detected")
            return False
            
        except Exception as e:
            logger.warning(f"Error during quick change scan: {e}")
            return True  # Assume changes if we can't check reliably
    
    def get_change_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about tracked files and recent changes.
        
        Returns:
            Dictionary with detailed statistics and insights
        """
        manifest_stats = self.file_manifest.get_manifest_statistics()
        
        if manifest_stats.get("status") == "empty":
            return {
                "status": "no_tracking",
                "message": "No files are currently being tracked",
                "recommendation": "Run initial processing to establish baseline"
            }
        
        # Analyze file patterns and ages
        manifest = self.file_manifest.load_file_manifest()
        file_entries = {k: v for k, v in manifest.items() if k != "_manifest_info"}
        
        if not file_entries:
            return manifest_stats
        
        # Calculate additional insights
        now = datetime.now()
        processing_dates = []
        
        for entry in file_entries.values():
            last_processed = entry.get("last_processed")
            if last_processed:
                try:
                    proc_date = datetime.fromisoformat(last_processed)
                    processing_dates.append(proc_date)
                except (ValueError, TypeError):
                    continue
        
        # Add temporal analysis
        if processing_dates:
            latest_processing = max(processing_dates)
            oldest_processing = min(processing_dates)
            
            manifest_stats["temporal_analysis"] = {
                "latest_processing": latest_processing.isoformat(),
                "oldest_processing": oldest_processing.isoformat(),
                "days_since_latest": (now - latest_processing).days,
                "tracking_span_days": (latest_processing - oldest_processing).days
            }
        
        return manifest_stats
    
    def cleanup_deleted_files(self, logger) -> Tuple[int, List[str]]:
        """
        Clean up manifest entries for files that no longer exist.
        
        Args:
            logger: Logger instance for status reporting
            
        Returns:
            Tuple of (removed_count, list_of_removed_files)
        """
        logger.info("🧹 Cleaning up manifest entries for deleted files...")
        
        manifest = self.file_manifest.load_file_manifest()
        removed_files = []
        
        for file_path in list(manifest.keys()):
            if file_path == "_manifest_info":  # Skip metadata
                continue
                
            if not os.path.exists(file_path):
                removed_files.append(file_path)
        
        # Remove deleted files from manifest
        for file_path in removed_files:
            self.file_manifest.remove_file_from_manifest(file_path)
        
        if removed_files:
            logger.info(f"Cleaned up {len(removed_files)} deleted file entries")
        else:
            logger.info("No cleanup needed - all tracked files still exist")
        
        return len(removed_files), removed_files
    
    def _scan_current_files(self, 
                           logger, 
                           include_hidden: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        Scan current files in the folder using processor registry patterns.
        
        Args:
            logger: Logger instance
            include_hidden: Whether to include hidden files
            
        Returns:
            Dictionary mapping file paths to their metadata
        """
        current_files = {}
        file_patterns = self.processor_registry.get_all_patterns()
        
        logger.debug(f"Scanning {len(file_patterns)} file patterns in {self.folder}")
        
        for pattern, file_type in file_patterns:
            pattern_path = os.path.join(self.folder, pattern)
            
            try:
                for file_path in glob.glob(pattern_path, recursive=True):
                    # Skip hidden files if not requested
                    if not include_hidden and self._is_hidden_file(file_path):
                        continue
                    
                    # Skip directories
                    if os.path.isdir(file_path):
                        continue
                    
                    try:
                        stat = os.stat(file_path)
                        file_hash = self.file_manifest.get_file_hash(file_path)
                        
                        if file_hash:  # Only include hashable files
                            current_files[file_path] = {
                                "type": file_type,
                                "hash": file_hash,
                                "modified": stat.st_mtime,
                                "size": stat.st_size,
                                "extension": Path(file_path).suffix.lower(),
                                "name": Path(file_path).name
                            }
                        
                    except (OSError, PermissionError) as e:
                        logger.warning(f"Cannot access file {file_path}: {e}")
                        continue
                        
            except Exception as e:
                logger.warning(f"Error scanning pattern {pattern}: {e}")
                continue
        
        logger.debug(f"Found {len(current_files)} accessible files")
        return current_files
    
    def _compare_with_manifest(self,
                              current_files: Dict[str, Dict[str, Any]],
                              manifest: Dict[str, Dict[str, Any]],
                              logger) -> Tuple[List[str], List[str], List[str]]:
        """
        Compare current files with manifest to identify changes.
        
        Args:
            current_files: Currently scanned files
            manifest: Stored manifest data
            logger: Logger instance
            
        Returns:
            Tuple of (new_files, modified_files, deleted_files)
        """
        # Extract file entries from manifest (exclude metadata)
        manifest_files = {k: v for k, v in manifest.items() if k != "_manifest_info"}
        
        new_files = []
        modified_files = []
        
        # Find new and modified files
        for file_path, file_info in current_files.items():
            if file_path not in manifest_files:
                new_files.append(file_path)
            else:
                # Check for modifications
                stored_entry = manifest_files[file_path]
                stored_hash = stored_entry.get("hash")
                stored_modified = stored_entry.get("modified", 0)
                
                current_hash = file_info["hash"]
                current_modified = file_info["modified"]
                
                # File is modified if hash changed or timestamp is newer
                if (stored_hash != current_hash or 
                    stored_modified < current_modified):
                    modified_files.append(file_path)
        
        # Find deleted files
        current_paths = set(current_files.keys())
        manifest_paths = set(manifest_files.keys())
        deleted_files = list(manifest_paths - current_paths)
        
        return new_files, modified_files, deleted_files
    
    def _update_manifest_for_processed_files(self,
                                           current_files: Dict[str, Dict[str, Any]],
                                           processed_files: List[str],
                                           deleted_files: List[str]):
        """
        Update manifest with information for files that were processed.
        
        Args:
            current_files: Current file information
            processed_files: List of files that will be processed
            deleted_files: List of files that were deleted
        """
        # Update entries for processed files
        for file_path in processed_files:
            if file_path in current_files:
                file_info = current_files[file_path].copy()
                file_info["last_processed"] = datetime.now().isoformat()
                self.file_manifest.update_file_in_manifest(file_path, file_info["type"])
        
        # Remove deleted files
        for file_path in deleted_files:
            self.file_manifest.remove_file_from_manifest(file_path)
    
    def _quick_scan_for_new_files(self, 
                                 manifest: Dict[str, Dict[str, Any]], 
                                 logger) -> bool:
        """
        Quick scan for new files using a subset of patterns.
        
        Args:
            manifest: Current manifest
            logger: Logger instance
            
        Returns:
            True if new files found, False otherwise
        """
        # Use only common file patterns for quick scanning
        common_patterns = [
            ("**/*.pdf", "pdf"),
            ("**/*.txt", "txt"), 
            ("**/*.md", "markdown"),
            ("**/*.py", "python"),
            ("**/*.json", "json")
        ]
        
        manifest_files = set(manifest.keys()) - {"_manifest_info"}
        
        for pattern, file_type in common_patterns:
            pattern_path = os.path.join(self.folder, pattern)
            
            try:
                for file_path in glob.glob(pattern_path, recursive=True):
                    if os.path.isfile(file_path) and file_path not in manifest_files:
                        logger.debug(f"Quick scan: Found new file {file_path}")
                        return True
            except Exception:
                continue  # Skip patterns that cause errors
        
        return False
    
    def _is_hidden_file(self, file_path: str) -> bool:
        """Check if file is hidden (starts with dot or in hidden directory)."""
        path = Path(file_path)
        
        # Check if file itself is hidden
        if path.name.startswith('.'):
            return True
        
        # Check if any parent directory is hidden
        for parent in path.parents:
            if parent.name.startswith('.'):
                return True
        
        return False
    
    def _log_change_detection_results(self, 
                                    logger, 
                                    results: Dict[str, Any]):
        """
        Log comprehensive change detection results.
        
        Args:
            logger: Logger instance
            results: Change detection results dictionary
        """
        new_count = len(results["new"])
        modified_count = len(results["modified"])
        deleted_count = len(results["deleted"])
        total_changes = new_count + modified_count + deleted_count
        
        logger.info("📊 File change detection complete:")
        logger.info(f"   📄 New files: {new_count:,}")
        logger.info(f"   🔄 Modified files: {modified_count:,}")
        logger.info(f"   🗑️  Deleted files: {deleted_count:,}")
        logger.info(f"   📈 Total changes: {total_changes:,}")
        logger.info(f"   🎯 Files to process: {len(results['to_process']):,}")
        
        if total_changes == 0:
            logger.info("✅ No changes detected - all files are up to date")
        elif len(results['to_process']) > 0:
            logger.info(f"🔄 Incremental processing will handle {len(results['to_process']):,} files")


# Convenience functions for backward compatibility and easy access
def detect_file_changes(folder: str, 
                       logger, 
                       force_refresh: bool = False) -> Dict[str, List[str]]:
    """
    Convenience function for detecting file changes.
    
    Args:
        folder: Folder to scan for changes
        logger: Logger instance
        force_refresh: Whether to force full refresh
        
    Returns:
        Dictionary with change detection results
    """
    detector = ChangeDetector(folder)
    return detector.detect_file_changes(logger, force_refresh)


def scan_folder_for_changes(folder: str, logger) -> bool:
    """
    Convenience function for quick change scanning.
    
    Args:
        folder: Folder to scan
        logger: Logger instance
        
    Returns:
        True if changes detected
    """
    detector = ChangeDetector(folder)
    return detector.quick_change_scan(logger)