"""
Integration Tests for LocalWise End-to-End Workflows

This module contains integration tests that verify the complete LocalWise workflows
from document processing through to query responses, testing the interaction
between multiple components.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from localwise.core.file_processors import FileProcessorRegistry
from localwise.data.data_manager import DataManager
from localwise.data.file_manifest import FileManifest
from localwise.data.change_detector import ChangeDetector
from localwise.core.embedding_service import EmbeddingService
from localwise.core.query_engine import QueryEngine


class TestEndToEndDocumentProcessing:
    """Test complete document processing workflow."""
    
    def test_full_document_processing_pipeline(self, temp_workspace, sample_text_files, mock_ollama_service, mock_vectorstore):
        """Test the complete pipeline from file to embeddings."""
        
        # Setup components
        registry = FileProcessorRegistry()
        data_manager = DataManager(os.path.join(temp_workspace, "processed_data.json"))
        
        # Step 1: Process documents
        with patch('localwise.core.file_processors.FileProcessorRegistry.scan_folder') as mock_scan:
            mock_scan.return_value = []
            
            # Process individual files
            all_documents = []
            for file_path in sample_text_files:
                processor = registry.get_processor_for_file(file_path)
                if processor:
                    documents = processor.process(file_path)
                    all_documents.extend(documents)
        
        assert len(all_documents) > 0, "Should process at least some documents"
        
        # Step 2: Save processed data
        processed_chunks = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in all_documents
        ]
        
        data_manager.save_processed_data(processed_chunks)
        
        # Step 3: Verify data was saved
        loaded_data = data_manager.load_processed_data()
        assert len(loaded_data) == len(processed_chunks)
        
        # Step 4: Test embeddings creation (with mocked service)
        with patch('localwise.core.embedding_service.EmbeddingService') as mock_embedding_service:
            mock_service_instance = mock_embedding_service.return_value
            mock_service_instance.create_embeddings_from_processed_data.return_value = mock_vectorstore
            
            embedding_service = mock_service_instance
            vectorstore = embedding_service.create_embeddings_from_processed_data(processed_chunks)
            
            assert vectorstore is not None
            mock_service_instance.create_embeddings_from_processed_data.assert_called_once_with(processed_chunks)
    
    def test_incremental_processing_workflow(self, temp_workspace, sample_text_files):
        """Test incremental processing when files change."""
        
        # Setup
        change_detector = ChangeDetector(temp_workspace)
        data_manager = DataManager(os.path.join(temp_workspace, "processed_data.json"))
        
        # First processing run
        changes_1 = change_detector.detect_changes(sample_text_files)
        assert len(changes_1['new_files']) == len(sample_text_files)
        
        # Process new files (simulate)
        initial_chunks = [
            {
                "content": f"Content from {os.path.basename(f)}",
                "metadata": {"source": f, "timestamp": "2024-01-01T00:00:00"}
            }
            for f in changes_1['new_files']
        ]
        data_manager.save_processed_data(initial_chunks)
        
        # Modify one file
        with open(sample_text_files[0], 'a') as f:
            f.write("\\n\\nAdditional content added")
        
        # Second processing run
        changes_2 = change_detector.detect_changes(sample_text_files)
        assert len(changes_2['new_files']) == 0
        assert len(changes_2['modified_files']) == 1
        assert sample_text_files[0] in changes_2['modified_files']
        
        # Process only changed files
        modified_chunks = [
            {
                "content": f"Updated content from {os.path.basename(f)}",
                "metadata": {"source": f, "timestamp": "2024-01-02T00:00:00"}
            }
            for f in changes_2['modified_files']
        ]
        data_manager.append_processed_data(modified_chunks)
        
        # Verify incremental processing
        all_data = data_manager.load_processed_data()
        assert len(all_data) == len(initial_chunks) + len(modified_chunks)


class TestQueryWorkflow:
    """Test query processing workflow."""
    
    @patch('localwise.core.query_engine.QueryEngine._ollama_request')
    def test_query_response_pipeline(self, mock_ollama_request, mock_vectorstore):
        """Test complete query to response pipeline."""
        
        # Setup mock response
        mock_ollama_request.return_value = {
            "response": "Based on the provided documents, LocalWise is a professional AI knowledge assistant."
        }
        
        # Create query engine
        query_engine = QueryEngine()
        
        # Perform query
        question = "What is LocalWise?"
        response = query_engine.query_documents(question, mock_vectorstore)
        
        # Verify response
        assert isinstance(response, str)
        assert len(response) > 0
        assert "LocalWise" in response
        
        # Verify vectorstore was queried
        mock_vectorstore.similarity_search.assert_called()
        
        # Verify Ollama was called
        mock_ollama_request.assert_called()
    
    @patch('localwise.core.query_engine.QueryEngine._ollama_request')
    def test_query_with_source_attribution(self, mock_ollama_request, mock_vectorstore):
        """Test query response includes source attribution."""
        
        mock_ollama_request.return_value = {
            "response": "LocalWise supports multiple file formats including PDF, CSV, and JSON."
        }
        
        query_engine = QueryEngine()
        response = query_engine.query_documents("What file formats does LocalWise support?", mock_vectorstore)
        
        # Response should include source information
        assert "Sources:" in response or "Source" in response
        
    def test_query_engine_validation(self):
        """Test query engine validation methods."""
        from localwise.core.query_engine import validate_query_system
        
        # Test system validation
        with patch('localwise.config.validate_ollama_connection') as mock_ollama:
            with patch('localwise.config.validate_database_exists') as mock_db:
                mock_ollama.return_value = (True, None)
                mock_db.return_value = (True, None)
                
                is_ready, issues = validate_query_system()
                
                assert is_ready == True
                assert len(issues) == 0
                
                # Test with issues
                mock_ollama.return_value = (False, "Ollama not running")
                mock_db.return_value = (False, "Database missing")
                
                is_ready, issues = validate_query_system()
                
                assert is_ready == False
                assert len(issues) == 2
                assert any("Ollama" in issue for issue in issues)
                assert any("Database" in issue for issue in issues)


class TestSystemIntegration:
    """Test system-wide integration scenarios."""
    
    def test_configuration_integration(self):
        """Test that configuration is properly shared across components."""
        from localwise import config
        
        # Test configuration values are accessible
        assert hasattr(config, 'DOCS_FOLDER')
        assert hasattr(config, 'DB_FOLDER')
        assert hasattr(config, 'OLLAMA_MODEL')
        assert hasattr(config, 'CHUNK_SIZE')
        
        # Test configuration functions
        assert callable(config.validate_ollama_connection)
        assert callable(config.validate_directories)
        assert callable(config.validate_database_exists)
        assert callable(config.setup_logging)
    
    def test_package_imports(self):
        """Test that all package components can be imported."""
        
        # Test main package imports
        from localwise import QueryEngine, EmbeddingService, DataManager
        
        assert QueryEngine is not None
        assert EmbeddingService is not None  
        assert DataManager is not None
        
        # Test subpackage imports
        from localwise.core import file_processors, embedding_service, query_engine
        from localwise.data import data_manager, file_manifest, change_detector
        from localwise.ui import ui_components
        from localwise.cli import cli_interface
        
        # Verify classes can be instantiated
        registry = file_processors.FileProcessorRegistry()
        assert registry is not None
        
        manifest = file_manifest.FileManifest("test_manifest.json")
        assert manifest is not None
    
    def test_cli_integration(self):
        """Test CLI interface integration."""
        from localwise.cli.cli_interface import LocalWiseCLI
        
        # Test CLI can be instantiated
        cli = LocalWiseCLI()
        assert cli is not None
        assert hasattr(cli, 'setup_argument_parser')
        assert hasattr(cli, 'validate_system')
        
        # Test argument parser setup
        parser = cli.setup_argument_parser()
        assert parser is not None
    
    def test_error_handling_integration(self, temp_workspace):
        """Test error handling across components."""
        
        # Test file processor error handling
        from localwise.core.file_processors import FileProcessorRegistry
        registry = FileProcessorRegistry()
        
        # Test with non-existent file
        processor = registry.get_processor_for_file("nonexistent.txt")
        assert processor is not None  # Should get TextProcessor
        
        with pytest.raises(FileNotFoundError):
            processor.process("nonexistent.txt")
        
        # Test data manager error handling  
        from localwise.data.data_manager import DataManager
        manager = DataManager("/invalid/path/data.json")
        
        # Should handle invalid paths gracefully
        data = manager.load_processed_data()
        assert data == []  # Should return empty list, not crash


class TestPerformanceIntegration:
    """Test performance-related integration scenarios."""
    
    def test_large_file_handling(self, temp_workspace):
        """Test handling of larger files and datasets."""
        
        # Create larger test file
        large_file = os.path.join(temp_workspace, "large_test.txt")
        with open(large_file, 'w') as f:
            for i in range(1000):
                f.write(f"This is line {i} of a larger test document for LocalWise testing.\\n")
        
        # Test processing
        from localwise.core.file_processors import TextProcessor
        processor = TextProcessor()
        
        result = processor.process(large_file)
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Should handle large files without errors
        total_content = ''.join(doc.page_content for doc in result)
        assert len(total_content) > 0
    
    def test_batch_processing_performance(self, temp_workspace):
        """Test batch processing scenarios."""
        
        # Create multiple test files
        files = []
        for i in range(10):
            file_path = os.path.join(temp_workspace, f"test_file_{i}.txt")
            with open(file_path, 'w') as f:
                f.write(f"Test content for file {i}")
            files.append(file_path)
        
        # Test batch processing
        from localwise.core.file_processors import FileProcessorRegistry
        registry = FileProcessorRegistry()
        
        # Group files by type
        files_by_type = {"txt": files}
        
        mock_logger = Mock()
        result = registry.process_files_by_type(files_by_type, mock_logger, max_file_size_mb=10)
        
        assert isinstance(result, list)
        assert len(result) >= len(files)  # Should process all files


if __name__ == "__main__":
    pytest.main([__file__, "-v"])