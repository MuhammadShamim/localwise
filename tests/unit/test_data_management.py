"""
Unit Tests for LocalWise Data Management Components

This module contains comprehensive unit tests for data management components
including DataManager, FileManifest, and ChangeDetector.
"""

import pytest
from unittest.mock import Mock, patch, mock_open
import json
import tempfile
import os
from pathlib import Path
from datetime import datetime

from localwise.data.data_manager import DataManager
from localwise.data.file_manifest import FileManifest
from localwise.data.change_detector import ChangeDetector


class TestDataManager:
    """Test the DataManager class."""
    
    def test_data_manager_instantiation(self, temp_workspace):
        """Test DataManager can be instantiated."""
        data_file = os.path.join(temp_workspace, "test_data.json")
        manager = DataManager(data_file)
        
        assert manager is not None
        assert manager.data_file == data_file
        assert hasattr(manager, 'data')
    
    def test_data_manager_save_load_data(self, temp_workspace, sample_processed_chunks):
        """Test saving and loading processed data."""
        data_file = os.path.join(temp_workspace, "test_data.json")
        manager = DataManager(data_file)
        
        # Save data
        manager.save_processed_data(sample_processed_chunks)
        
        # Verify file was created
        assert os.path.exists(data_file)
        
        # Load data
        loaded_data = manager.load_processed_data()
        
        assert isinstance(loaded_data, list)
        assert len(loaded_data) == len(sample_processed_chunks)
        assert loaded_data[0]['content'] == sample_processed_chunks[0]['content']
    
    def test_data_manager_append_data(self, temp_workspace, sample_processed_chunks):
        """Test appending data to existing file."""
        data_file = os.path.join(temp_workspace, "test_data.json")
        manager = DataManager(data_file)
        
        # Save initial data
        initial_data = sample_processed_chunks[:1]
        manager.save_processed_data(initial_data)
        
        # Append more data
        additional_data = sample_processed_chunks[1:]
        manager.append_processed_data(additional_data)
        
        # Load and verify
        loaded_data = manager.load_processed_data()
        assert len(loaded_data) == len(sample_processed_chunks)
    
    def test_data_manager_get_statistics(self, temp_workspace, sample_processed_chunks):
        """Test getting data statistics."""
        data_file = os.path.join(temp_workspace, "test_data.json")
        manager = DataManager(data_file)
        
        # Save sample data
        manager.save_processed_data(sample_processed_chunks)
        
        # Get statistics
        stats = manager.get_statistics()
        
        assert isinstance(stats, dict)
        assert 'total_chunks' in stats
        assert 'total_files' in stats
        assert 'file_types' in stats
        assert stats['total_chunks'] == len(sample_processed_chunks)
    
    def test_data_manager_clear_data(self, temp_workspace, sample_processed_chunks):
        """Test clearing all data."""
        data_file = os.path.join(temp_workspace, "test_data.json")
        manager = DataManager(data_file)
        
        # Save data
        manager.save_processed_data(sample_processed_chunks)
        assert len(manager.load_processed_data()) > 0
        
        # Clear data
        manager.clear_data()
        
        # Verify data is cleared
        loaded_data = manager.load_processed_data()
        assert len(loaded_data) == 0
    
    def test_data_manager_file_not_exists(self, temp_workspace):
        """Test behavior when data file doesn't exist."""
        data_file = os.path.join(temp_workspace, "nonexistent.json")
        manager = DataManager(data_file)
        
        # Load from non-existent file should return empty list
        loaded_data = manager.load_processed_data()
        assert loaded_data == []
    
    @patch("json.dump")
    def test_data_manager_save_error_handling(self, mock_json_dump, temp_workspace):
        """Test error handling during save operations."""
        mock_json_dump.side_effect = IOError("Save failed")
        
        data_file = os.path.join(temp_workspace, "test_data.json")
        manager = DataManager(data_file)
        
        with pytest.raises(IOError):
            manager.save_processed_data([{"test": "data"}])


class TestFileManifest:
    """Test the FileManifest class."""
    
    def test_file_manifest_instantiation(self, temp_workspace):
        """Test FileManifest can be instantiated."""
        manifest_file = os.path.join(temp_workspace, "manifest.json")
        manifest = FileManifest(manifest_file)
        
        assert manifest is not None
        assert manifest.manifest_file == manifest_file
        assert hasattr(manifest, 'manifest_data')
    
    def test_file_manifest_add_file(self, temp_workspace, sample_text_files):
        """Test adding files to manifest."""
        manifest_file = os.path.join(temp_workspace, "manifest.json")
        manifest = FileManifest(manifest_file)
        
        # Add a file
        test_file = sample_text_files[0]
        manifest.add_file(test_file)
        
        # Verify file was added
        assert test_file in manifest.manifest_data
        
        file_info = manifest.manifest_data[test_file]
        assert 'hash' in file_info
        assert 'size' in file_info
        assert 'modified_time' in file_info
        assert 'file_type' in file_info
    
    def test_file_manifest_has_file_changed(self, temp_workspace, sample_text_files):
        """Test detecting file changes."""
        manifest_file = os.path.join(temp_workspace, "manifest.json")
        manifest = FileManifest(manifest_file)
        
        # Add file to manifest
        test_file = sample_text_files[0]
        manifest.add_file(test_file)
        
        # File shouldn't be changed initially
        assert manifest.has_file_changed(test_file) == False
        
        # Modify file
        with open(test_file, 'a') as f:
            f.write("\\nModified content")
        
        # Now file should be detected as changed
        assert manifest.has_file_changed(test_file) == True
    
    def test_file_manifest_get_changed_files(self, temp_workspace, sample_text_files):
        """Test getting list of changed files."""
        manifest_file = os.path.join(temp_workspace, "manifest.json")
        manifest = FileManifest(manifest_file)
        
        # Add files to manifest
        for file_path in sample_text_files[:2]:
            manifest.add_file(file_path)
        
        # Modify one file
        with open(sample_text_files[0], 'a') as f:
            f.write("\\nModified")
        
        # Get changed files
        changed_files = manifest.get_changed_files(sample_text_files[:2])
        
        assert len(changed_files) == 1
        assert sample_text_files[0] in changed_files
        assert sample_text_files[1] not in changed_files
    
    def test_file_manifest_save_load(self, temp_workspace, sample_text_files):
        """Test saving and loading manifest."""
        manifest_file = os.path.join(temp_workspace, "manifest.json")
        manifest = FileManifest(manifest_file)
        
        # Add files
        for file_path in sample_text_files:
            manifest.add_file(file_path)
        
        # Save manifest
        manifest.save()
        assert os.path.exists(manifest_file)
        
        # Create new manifest instance and load
        new_manifest = FileManifest(manifest_file)
        new_manifest.load()
        
        # Verify data was loaded correctly
        assert len(new_manifest.manifest_data) == len(sample_text_files)
        for file_path in sample_text_files:
            assert file_path in new_manifest.manifest_data
    
    def test_file_manifest_calculate_hash(self, temp_workspace):
        """Test file hash calculation."""
        manifest_file = os.path.join(temp_workspace, "manifest.json")
        manifest = FileManifest(manifest_file)
        
        # Create test file
        test_file = os.path.join(temp_workspace, "test_hash.txt")
        with open(test_file, 'w') as f:
            f.write("Test content for hash")
        
        # Calculate hash
        hash_value = manifest._calculate_file_hash(test_file)
        
        assert isinstance(hash_value, str)
        assert len(hash_value) == 32  # MD5 hash length
        
        # Same file should produce same hash
        hash_value2 = manifest._calculate_file_hash(test_file)
        assert hash_value == hash_value2


class TestChangeDetector:
    """Test the ChangeDetector class."""
    
    def test_change_detector_instantiation(self, temp_workspace):
        """Test ChangeDetector can be instantiated."""
        detector = ChangeDetector(temp_workspace)
        
        assert detector is not None
        assert detector.workspace_dir == temp_workspace
        assert hasattr(detector, 'manifest')
    
    def test_change_detector_detect_changes(self, temp_workspace, sample_text_files):
        """Test detecting changes in files."""
        detector = ChangeDetector(temp_workspace)
        
        # First scan (no changes expected)
        changes = detector.detect_changes(sample_text_files)
        
        assert isinstance(changes, dict)
        assert 'new_files' in changes
        assert 'modified_files' in changes
        assert 'deleted_files' in changes
        
        # All files should be new on first scan
        assert len(changes['new_files']) == len(sample_text_files)
        assert len(changes['modified_files']) == 0
        assert len(changes['deleted_files']) == 0
    
    def test_change_detector_subsequent_scan(self, temp_workspace, sample_text_files):
        """Test change detection in subsequent scans."""
        detector = ChangeDetector(temp_workspace)
        
        # First scan
        detector.detect_changes(sample_text_files)
        
        # Modify one file
        with open(sample_text_files[0], 'a') as f:
            f.write("\\nModified content")
        
        # Second scan
        changes = detector.detect_changes(sample_text_files)
        
        assert len(changes['new_files']) == 0
        assert len(changes['modified_files']) == 1
        assert sample_text_files[0] in changes['modified_files']
        assert len(changes['deleted_files']) == 0
    
    def test_change_detector_deleted_files(self, temp_workspace, sample_text_files):
        """Test detection of deleted files."""
        detector = ChangeDetector(temp_workspace)
        
        # First scan with all files
        detector.detect_changes(sample_text_files)
        
        # Second scan with fewer files (simulate deletion)
        remaining_files = sample_text_files[:-1]  # Remove last file
        changes = detector.detect_changes(remaining_files)
        
        assert len(changes['deleted_files']) == 1
        assert sample_text_files[-1] in changes['deleted_files']
    
    def test_change_detector_get_statistics(self, temp_workspace, sample_text_files):
        """Test getting change detection statistics."""
        detector = ChangeDetector(temp_workspace)
        
        # Perform detection
        detector.detect_changes(sample_text_files)
        
        # Get statistics
        stats = detector.get_statistics()
        
        assert isinstance(stats, dict)
        assert 'total_files_tracked' in stats
        assert 'last_scan_time' in stats
        assert stats['total_files_tracked'] == len(sample_text_files)
    
    def test_change_detector_performance_mode(self, temp_workspace, sample_text_files):
        """Test quick scan performance mode."""
        detector = ChangeDetector(temp_workspace)
        
        # First scan to establish baseline
        detector.detect_changes(sample_text_files)
        
        # Quick scan (should skip manifest comparison if no file changes)
        changes = detector.detect_changes(sample_text_files, quick_scan=True)
        
        assert isinstance(changes, dict)
        # In quick scan mode, if no filesystem changes, should be minimal changes
        total_changes = len(changes['new_files']) + len(changes['modified_files']) + len(changes['deleted_files'])
        assert total_changes == 0


if __name__ == "__main__":
    pytest.main([__file__])