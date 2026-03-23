"""
Unit Tests for LocalWise File Processors

This module contains comprehensive unit tests for the file processing components
of LocalWise, including individual processor classes and the registry system.
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import tempfile
import os

from localwise.core.file_processors import (
    FileProcessor, 
    PDFProcessor,
    CSVProcessor, 
    JSONProcessor,
    YAMLProcessor,
    XMLProcessor,
    TextProcessor,
    CodeProcessor,
    FileProcessorRegistry
)


class TestFileProcessor:
    """Test the base FileProcessor class."""
    
    def test_base_processor_instantiation(self):
        """Test that base FileProcessor can be instantiated."""
        processor = FileProcessor()
        assert processor is not None
        assert hasattr(processor, 'process')
        assert hasattr(processor, 'can_process')
        assert hasattr(processor, 'get_supported_extensions')
    
    def test_base_processor_abstract_methods(self):
        """Test that base class methods raise NotImplementedError."""
        processor = FileProcessor()
        
        with pytest.raises(NotImplementedError):
            processor.process("test.txt")
        
        with pytest.raises(NotImplementedError):
            processor.can_process("test.txt")
        
        with pytest.raises(NotImplementedError):
            processor.get_supported_extensions()


class TestTextProcessor:
    """Test the TextProcessor class."""
    
    def test_text_processor_supported_extensions(self):
        """Test that TextProcessor supports correct extensions."""
        processor = TextProcessor()
        extensions = processor.get_supported_extensions()
        
        assert '.txt' in extensions
        assert '.md' in extensions
        assert '.rtf' in extensions
        assert isinstance(extensions, list)
    
    def test_text_processor_can_process(self):
        """Test TextProcessor file detection."""
        processor = TextProcessor()
        
        assert processor.can_process("document.txt") == True
        assert processor.can_process("README.md") == True
        assert processor.can_process("notes.rtf") == True
        assert processor.can_process("image.jpg") == False
        assert processor.can_process("data.pdf") == False
    
    def test_text_processor_process_success(self, sample_text_files):
        """Test successful text file processing."""
        processor = TextProcessor()
        
        # Find the txt file from fixtures
        txt_file = next((f for f in sample_text_files if f.endswith('.txt')), None)
        assert txt_file is not None, "No .txt file found in fixtures"
        
        result = processor.process(txt_file)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(hasattr(doc, 'page_content') for doc in result)
        assert all(hasattr(doc, 'metadata') for doc in result)
    
    @patch("pathlib.Path.read_text")
    def test_text_processor_encoding_handling(self, mock_read_text):
        """Test that TextProcessor handles different encodings."""
        processor = TextProcessor()
        mock_read_text.return_value = "Test content with üñíçødé"
        
        result = processor.process("test.txt")
        
        mock_read_text.assert_called_once()
        assert len(result) > 0
        assert "üñíçødé" in result[0].page_content
    
    def test_text_processor_file_not_found(self):
        """Test TextProcessor behavior with non-existent file."""
        processor = TextProcessor()
        
        with pytest.raises(FileNotFoundError):
            processor.process("nonexistent.txt")


class TestCSVProcessor:
    """Test the CSVProcessor class."""
    
    def test_csv_processor_supported_extensions(self):
        """Test CSV processor supported extensions."""
        processor = CSVProcessor()
        extensions = processor.get_supported_extensions()
        
        assert '.csv' in extensions
        assert '.tsv' in extensions
    
    def test_csv_processor_can_process(self):
        """Test CSV processor file detection."""
        processor = CSVProcessor()
        
        assert processor.can_process("data.csv") == True
        assert processor.can_process("export.tsv") == True
        assert processor.can_process("document.txt") == False
    
    def test_csv_processor_process_success(self, sample_text_files):
        """Test successful CSV file processing."""
        processor = CSVProcessor()
        
        # Find the csv file from fixtures
        csv_file = next((f for f in sample_text_files if f.endswith('.csv')), None)
        assert csv_file is not None, "No .csv file found in fixtures"
        
        result = processor.process(csv_file)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(hasattr(doc, 'page_content') for doc in result)
        assert "John" in result[0].page_content  # From test data
        assert "Jane" in result[0].page_content


class TestJSONProcessor:
    """Test the JSONProcessor class."""
    
    def test_json_processor_supported_extensions(self):
        """Test JSON processor supported extensions."""
        processor = JSONProcessor()
        extensions = processor.get_supported_extensions()
        
        assert '.json' in extensions
        assert '.jsonl' in extensions
    
    def test_json_processor_process_success(self, sample_text_files):
        """Test successful JSON file processing."""
        processor = JSONProcessor()
        
        # Find the json file from fixtures
        json_file = next((f for f in sample_text_files if f.endswith('.json')), None)
        assert json_file is not None, "No .json file found in fixtures"
        
        result = processor.process(json_file)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert "LocalWise" in result[0].page_content  # From test data
    
    @patch("json.loads")
    def test_json_processor_invalid_json(self, mock_json_loads):
        """Test JSON processor with invalid JSON."""
        mock_json_loads.side_effect = ValueError("Invalid JSON")
        processor = JSONProcessor()
        
        with patch("pathlib.Path.read_text", return_value="invalid json"):
            with pytest.raises(ValueError):
                processor.process("invalid.json")


class TestYAMLProcessor:
    """Test the YAMLProcessor class."""
    
    def test_yaml_processor_supported_extensions(self):
        """Test YAML processor supported extensions.""" 
        processor = YAMLProcessor()
        extensions = processor.get_supported_extensions()
        
        assert '.yaml' in extensions
        assert '.yml' in extensions
    
    def test_yaml_processor_process_success(self, sample_text_files):
        """Test successful YAML file processing."""
        processor = YAMLProcessor()
        
        # Find the yaml file from fixtures
        yaml_file = next((f for f in sample_text_files if f.endswith('.yaml')), None)
        assert yaml_file is not None, "No .yaml file found in fixtures"
        
        result = processor.process(yaml_file)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert "database" in result[0].page_content  # From test data


class TestXMLProcessor:
    """Test the XMLProcessor class."""
    
    def test_xml_processor_supported_extensions(self):
        """Test XML processor supported extensions."""
        processor = XMLProcessor()
        extensions = processor.get_supported_extensions()
        
        assert '.xml' in extensions
    
    def test_xml_processor_process_success(self, sample_text_files):
        """Test successful XML file processing."""
        processor = XMLProcessor()
        
        # Find the xml file from fixtures  
        xml_file = next((f for f in sample_text_files if f.endswith('.xml')), None)
        assert xml_file is not None, "No .xml file found in fixtures"
        
        result = processor.process(xml_file)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert "LocalWise" in result[0].page_content  # From test data


class TestCodeProcessor:
    """Test the CodeProcessor class."""
    
    def test_code_processor_supported_extensions(self):
        """Test Code processor supported extensions."""
        processor = CodeProcessor()
        extensions = processor.get_supported_extensions()
        
        assert '.py' in extensions
        assert '.js' in extensions
        assert '.java' in extensions
        assert '.sql' in extensions
        assert len(extensions) > 10  # Should support many code formats
    
    def test_code_processor_can_process(self):
        """Test Code processor file detection."""
        processor = CodeProcessor()
        
        assert processor.can_process("script.py") == True
        assert processor.can_process("app.js") == True
        assert processor.can_process("query.sql") == True
        assert processor.can_process("document.txt") == False
    
    @patch("pathlib.Path.read_text")
    def test_code_processor_process_success(self, mock_read_text):
        """Test successful code file processing."""
        mock_read_text.return_value = "def hello():\n    return 'Hello World!'"
        
        processor = CodeProcessor()
        result = processor.process("test.py")
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert "def hello" in result[0].page_content
        assert result[0].metadata['source'] == "test.py"
        assert result[0].metadata['file_type'] == 'py'


class TestFileProcessorRegistry:
    """Test the FileProcessorRegistry class."""
    
    def test_registry_instantiation(self):
        """Test registry can be instantiated."""
        registry = FileProcessorRegistry()
        assert registry is not None
        assert hasattr(registry, 'processors')
        assert isinstance(registry.processors, list)
    
    def test_registry_default_processors(self):
        """Test registry has default processors registered."""
        registry = FileProcessorRegistry()
        
        # Should have processors for common file types
        assert any(isinstance(p, TextProcessor) for p in registry.processors)
        assert any(isinstance(p, CSVProcessor) for p in registry.processors)
        assert any(isinstance(p, JSONProcessor) for p in registry.processors)
        assert any(isinstance(p, YAMLProcessor) for p in registry.processors)
        assert any(isinstance(p, XMLProcessor) for p in registry.processors)
        assert any(isinstance(p, CodeProcessor) for p in registry.processors)
    
    def test_registry_register_processor(self):
        """Test registering a new processor."""
        registry = FileProcessorRegistry()
        initial_count = len(registry.processors)
        
        # Create mock processor
        mock_processor = Mock()
        mock_processor.get_supported_extensions.return_value = ['.test']
        
        registry.register_processor(mock_processor)
        
        assert len(registry.processors) == initial_count + 1
        assert mock_processor in registry.processors
    
    def test_registry_get_processor_for_file(self):
        """Test getting processor for specific file."""
        registry = FileProcessorRegistry()
        
        # Test known file types
        txt_processor = registry.get_processor_for_file("test.txt")
        assert txt_processor is not None
        assert isinstance(txt_processor, TextProcessor)
        
        csv_processor = registry.get_processor_for_file("data.csv")
        assert csv_processor is not None
        assert isinstance(csv_processor, CSVProcessor)
        
        json_processor = registry.get_processor_for_file("config.json")
        assert json_processor is not None
        assert isinstance(json_processor, JSONProcessor)
    
    def test_registry_get_processor_unknown_file(self):
        """Test getting processor for unknown file type."""
        registry = FileProcessorRegistry()
        
        processor = registry.get_processor_for_file("unknown.xyz")
        assert processor is None
    
    def test_registry_process_files_by_type(self, temp_workspace, test_config):
        """Test processing files by type through registry."""
        registry = FileProcessorRegistry()
        
        # Create test files in temporary workspace
        docs_dir = Path(temp_workspace) / test_config["DOCS_FOLDER"]
        test_files = {
            "txt": [str(docs_dir / "test.txt")],
            "csv": [str(docs_dir / "data.csv")],
            "json": [str(docs_dir / "config.json")]
        }
        
        # Create actual files
        (docs_dir / "test.txt").write_text("Test content")
        (docs_dir / "data.csv").write_text("name,value\ntest,123")
        (docs_dir / "config.json").write_text('{"test": "value"}')
        
        # Mock logger
        mock_logger = Mock()
        
        # Process files
        result = registry.process_files_by_type(test_files, mock_logger, max_file_size_mb=5)
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Verify logger was called
        assert mock_logger.info.called
    
    def test_registry_scan_folder(self, temp_workspace, test_config):
        """Test scanning folder functionality."""
        registry = FileProcessorRegistry()
        docs_dir = Path(temp_workspace) / test_config["DOCS_FOLDER"]
        
        # Create test files
        (docs_dir / "test.txt").write_text("Test content")
        (docs_dir / "data.csv").write_text("name,value\ntest,123")
        
        # Create subdirectory with file
        sub_dir = docs_dir / "subdir"
        sub_dir.mkdir()
        (sub_dir / "nested.json").write_text('{"nested": true}')
        
        mock_logger = Mock()
        
        # Scan folder
        result = registry.scan_folder(str(docs_dir), mock_logger)
        
        assert isinstance(result, list)
        assert len(result) >= 3  # Should find all files including nested
        
        # Verify all files were processed
        sources = [doc.metadata['source'] for doc in result]
        assert any('test.txt' in source for source in sources)
        assert any('data.csv' in source for source in sources)
        assert any('nested.json' in source for source in sources)


if __name__ == "__main__":
    pytest.main([__file__])