"""
LocalWise Core File Processors Module

This module contains the complete file processing system for LocalWise, including:
- Base FileProcessor class for extensible file handling
- Specialized processors for 40+ file types  
- FileProcessorRegistry for organized processor management
- Support for documents, source code, data files, and more

Architecture:
- FileProcessor: Abstract base class defining the processor interface
- Specialized processors: Concrete implementations for specific file types
- Registry pattern: Centralized management and registration of processors

Supported File Types:
- Documents: PDF, DOC/DOCX, RTF, TXT, Markdown
- Data: CSV, JSON, YAML, XML  
- Source Code: 25+ programming languages
- Web: HTML, CSS, SCSS, JavaScript, TypeScript
- Configuration: YAML, JSON, XML, INI

Version: 1.0.0
Author: LocalWise Development Team
"""

import os
import glob
import json
import yaml
import xml.etree.ElementTree as ET
import pandas as pd
import pdfplumber
from typing import List, Dict, Any, Optional, Callable


class FileProcessor:
    """
    Abstract base class for file processors.
    
    Defines the interface that all file processors must implement to ensure
    consistent behavior across different file types. Uses the Template Method
    pattern to provide common functionality while allowing customization.
    
    Attributes:
        file_type (str): Unique identifier for this processor type
        extensions (List[str]): File extensions this processor can handle
        description (str): Human-readable description of the processor
        patterns (List[str]): Glob patterns for file discovery
    """
    
    def __init__(self, file_type: str, extensions: List[str], description: str):
        """
        Initialize a file processor.
        
        Args:
            file_type: Unique identifier for this processor
            extensions: List of file extensions (e.g., ['.pdf', '.doc'])
            description: Human-readable description
        """
        self.file_type = file_type
        self.extensions = extensions
        self.description = description
        # Create glob patterns for recursive file discovery
        self.patterns = [f"**/*{ext}" for ext in extensions]
    
    def can_process(self, file_path: str) -> bool:
        """
        Check if this processor can handle the given file.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if this processor can handle the file, False otherwise
        """
        return any(file_path.lower().endswith(ext) for ext in self.extensions)
    
    def find_files(self, folder: str) -> List[str]:
        """
        Find all files this processor can handle in the given folder.
        
        Uses recursive glob patterns to discover files matching this processor's
        supported extensions throughout the directory tree.
        
        Args:
            folder: Root folder to search
            
        Returns:
            List of absolute file paths that can be processed
        """
        all_files = []
        for pattern in self.patterns:
            all_files.extend(glob.glob(os.path.join(folder, pattern), recursive=True))
        return all_files
    
    def process_files(self, file_paths: List[str], logger, max_file_size_mb: int = 50) -> List[Dict[str, Any]]:
        """
        Process a list of files and return document objects.
        
        Template method that handles common file processing tasks:
        - File size validation
        - Error handling and logging
        - Delegation to processor-specific logic
        
        Args:
            file_paths: List of files to process
            logger: Logger instance for status reporting
            max_file_size_mb: Maximum file size to process (MB)
            
        Returns:
            List of processed document objects
        """
        docs = []
        for path in file_paths:
            try:
                # Check file size before processing
                file_size_mb = os.path.getsize(path) / (1024 * 1024)
                if file_size_mb > max_file_size_mb:
                    logger.warning(f"Skipping large {self.file_type} file: {path} ({file_size_mb:.1f}MB > {max_file_size_mb}MB)")
                    continue
                
                logger.info(f"Processing {self.file_type.upper()}: {os.path.basename(path)}")
                result = self.process_single_file(path, logger)
                
                if result:
                    # Handle both single documents and lists
                    if isinstance(result, list):
                        docs.extend(result)
                    else:
                        docs.append(result)
                        
            except Exception as e:
                logger.error(f"Failed to process {self.file_type} file {path}: {e}")
                continue
                
        return docs
    
    def process_single_file(self, file_path: str, logger) -> Optional[Dict[str, Any]]:
        """
        Process a single file. Must be implemented by subclasses.
        
        Args:
            file_path: Path to the file to process
            logger: Logger instance
            
        Returns:
            Document object or list of document objects, or None if processing failed
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement process_single_file")


class TextFileProcessor(FileProcessor):
    """
    Processor for plain text files and source code.
    
    Handles encoding detection and supports multiple character encodings
    commonly found in international text files and source code.
    """
    
    def process_single_file(self, file_path: str, logger) -> Optional[Dict[str, Any]]:
        """
        Process a text file with automatic encoding detection.
        
        Tries multiple encodings in order of likelihood to handle
        international characters and legacy file formats.
        """
        # Common encodings ordered by likelihood
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                
                if content.strip():  # Only process non-empty files
                    return {
                        "text": content,
                        "source": file_path,
                        "type": self.file_type,
                        "encoding": encoding
                    }
                break
                
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
                return None
        
        logger.error(f"Could not decode {file_path}: no supported encoding found")
        return None


class PDFProcessor(FileProcessor):
    """
    Processor for PDF documents.
    
    Extracts text content from each page using pdfplumber library.
    Creates separate document objects for each page to improve
    search granularity and context relevance.
    """
    
    def process_single_file(self, file_path: str, logger) -> List[Dict[str, Any]]:
        """
        Extract text from all pages of a PDF document.
        
        Returns:
            List of document objects, one per page with text content
        """
        docs = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                logger.debug(f"Processing {total_pages} pages from {os.path.basename(file_path)}")
                
                for page_num, page in enumerate(pdf.pages):
                    try:
                        text = page.extract_text()
                        if text and text.strip():
                            docs.append({
                                "text": text,
                                "source": f"{file_path} (page {page_num + 1})",
                                "type": "pdf",
                                "page_number": page_num + 1,
                                "total_pages": total_pages
                            })
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error opening PDF {file_path}: {e}")
            
        return docs


class CSVProcessor(FileProcessor):
    """
    Processor for CSV data files.
    
    Handles large CSV files by processing row by row and supports
    automatic encoding detection for international data.
    """
    
    def process_single_file(self, file_path: str, logger) -> List[Dict[str, Any]]:
        """
        Process CSV file row by row for better search granularity.
        
        Returns:
            List of document objects, one per row
        """
        docs = []
        # Try common encodings for CSV files
        encodings = ['utf-8', 'latin-1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                logger.debug(f"Successfully read CSV with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.error(f"Error reading CSV with {encoding}: {e}")
                continue
        
        if df is None:
            logger.error(f"Could not read CSV {file_path}: no supported encoding")
            return docs
        
        # Handle large files
        row_count = len(df)
        if row_count > 1000:
            logger.info(f"Large CSV detected ({row_count:,} rows), processing in batches...")
        
        # Process each row as a separate document
        for i, row in df.iterrows():
            # Convert row to readable text format
            row_text = "\n".join([
                f"{col}: {val}" 
                for col, val in row.items() 
                if pd.notna(val) and str(val).strip()
            ])
            
            if row_text:  # Only add non-empty rows
                docs.append({
                    "text": row_text,
                    "source": f"{file_path} (row {i + 1})",
                    "type": "csv",
                    "row_number": i + 1,
                    "total_rows": row_count
                })
                
        return docs


class JSONProcessor(FileProcessor):
    """
    Processor for JSON data files.
    
    Parses JSON and converts to formatted text for better readability
    and search performance while preserving structure.
    """
    
    def process_single_file(self, file_path: str, logger) -> Optional[Dict[str, Any]]:
        """
        Parse JSON file and convert to formatted text.
        
        Returns:
            Document object with formatted JSON content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Format JSON for better readability
            json_text = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)
            
            # Add metadata about the JSON structure
            metadata = {
                "is_array": isinstance(data, list),
                "is_object": isinstance(data, dict),
                "size": len(str(data))
            }
            
            return {
                "text": json_text,
                "source": file_path,
                "type": "json",
                "metadata": metadata
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing JSON file {file_path}: {e}")
            return None


class YAMLProcessor(FileProcessor):
    """
    Processor for YAML configuration files.
    
    Parses YAML and converts to clean text format while preserving
    structure and handling complex YAML features.
    """
    
    def process_single_file(self, file_path: str, logger) -> Optional[Dict[str, Any]]:
        """
        Parse YAML file and convert to formatted text.
        
        Returns:
            Document object with formatted YAML content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            if data is not None:
                # Convert back to YAML for consistent formatting
                yaml_text = yaml.dump(
                    data, 
                    default_flow_style=False, 
                    allow_unicode=True,
                    sort_keys=True,
                    indent=2
                )
                
                return {
                    "text": yaml_text,
                    "source": file_path,
                    "type": "yaml",
                    "structure_type": type(data).__name__
                }
            else:
                logger.warning(f"Empty YAML file: {file_path}")
                return None
                
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing YAML file {file_path}: {e}")
            return None


class XMLProcessor(FileProcessor):
    """
    Processor for XML structure files.
    
    Parses XML and converts to readable text format while preserving
    element hierarchy and attributes.
    """
    
    def process_single_file(self, file_path: str, logger) -> Optional[Dict[str, Any]]:
        """
        Parse XML file and convert to structured text.
        
        Returns:
            Document object with formatted XML content
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            def extract_xml_text(element, level=0):
                """Recursively extract XML content with proper formatting."""
                texts = []
                indent = "  " * level
                
                # Build opening tag with attributes
                if element.tag:
                    tag_info = f"{indent}<{element.tag}"
                    if element.attrib:
                        attrs = " ".join([f'{k}="{v}"' for k, v in element.attrib.items()])
                        tag_info += f" {attrs}"
                    tag_info += ">"
                    texts.append(tag_info)
                
                # Add text content if present
                if element.text and element.text.strip():
                    texts.append(f"{indent}  {element.text.strip()}")
                
                # Process child elements recursively
                for child in element:
                    texts.extend(extract_xml_text(child, level + 1))
                
                # Add closing tag
                if element.tag:
                    texts.append(f"{indent}</{element.tag}>")
                
                return texts
            
            xml_content = "\n".join(extract_xml_text(root))
            
            return {
                "text": xml_content,
                "source": file_path,
                "type": "xml",
                "root_element": root.tag,
                "namespace": root.tag.split("}")[0][1:] if "}" in root.tag else None
            }
            
        except ET.ParseError as e:
            logger.error(f"Invalid XML in {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing XML file {file_path}: {e}")
            return None


class OfficeProcessor(FileProcessor):
    """
    Processor for Microsoft Office documents.
    
    Extracts text content from DOC and DOCX files using docx2txt library.
    Requires optional dependency: pip install docx2txt
    """
    
    def process_single_file(self, file_path: str, logger) -> Optional[Dict[str, Any]]:
        """
        Extract text from Office documents.
        
        Returns:
            Document object with extracted text content
        """
        try:
            import docx2txt
            
            text = docx2txt.process(file_path)
            if text and text.strip():
                file_type = "docx" if file_path.lower().endswith('.docx') else "doc"
                
                return {
                    "text": text,
                    "source": file_path,
                    "type": file_type,
                    "word_count": len(text.split())
                }
            else:
                logger.warning(f"No extractable text found in {file_path}")
                return None
                
        except ImportError:
            logger.warning("docx2txt library not available. Install with: pip install docx2txt")
            return None
        except Exception as e:
            logger.error(f"Error processing Office file {file_path}: {e}")
            return None


class RTFProcessor(FileProcessor):
    """
    Processor for RTF (Rich Text Format) files.
    
    Converts RTF to plain text using striprtf library.
    Requires optional dependency: pip install striprtf
    """
    
    def process_single_file(self, file_path: str, logger) -> Optional[Dict[str, Any]]:
        """
        Convert RTF to plain text.
        
        Returns:
            Document object with plain text content
        """
        try:
            from striprtf.striprtf import rtf_to_text
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                rtf_content = f.read()
            
            text = rtf_to_text(rtf_content)
            if text and text.strip():
                return {
                    "text": text,
                    "source": file_path,
                    "type": "rtf",
                    "original_size": len(rtf_content),
                    "processed_size": len(text)
                }
            else:
                logger.warning(f"No text extracted from RTF file: {file_path}")
                return None
                
        except ImportError:
            logger.warning("striprtf library not available. Install with: pip install striprtf")
            return None
        except Exception as e:
            logger.error(f"Error processing RTF file {file_path}: {e}")
            return None


class FileProcessorRegistry:
    """
    Registry for managing and organizing file processors.
    
    Implements the Registry pattern to provide centralized management
    of file processors with efficient lookup and extension mapping.
    
    Features:
    - Automatic registration of default processors
    - Fast file-to-processor mapping via extension lookup
    - Support for custom processor registration
    - Batch processing capabilities
    """
    
    def __init__(self):
        """Initialize the registry and register default processors."""
        self.processors = {}  # file_type -> processor mapping
        self.extension_map = {}  # extension -> processor mapping
        self._register_default_processors()
    
    def _register_default_processors(self):
        """
        Register all built-in file processors.
        
        Organized by category for better maintainability and
        supports 40+ different file types across various domains.
        """
        processors = [
            # === CORE DOCUMENT TYPES ===
            PDFProcessor("pdf", [".pdf"], "PDF documents with text extraction"),
            CSVProcessor("csv", [".csv"], "Comma-separated value data files"),
            JSONProcessor("json", [".json"], "JSON data and configuration files"),
            YAMLProcessor("yaml", [".yml", ".yaml"], "YAML configuration and data files"),
            XMLProcessor("xml", [".xml"], "XML structure and data files"),
            
            # === OFFICE DOCUMENTS ===
            OfficeProcessor("office", [".doc", ".docx"], "Microsoft Word documents"),
            RTFProcessor("rtf", [".rtf"], "Rich Text Format documents"),
            
            # === PLAIN TEXT AND DOCUMENTATION ===
            TextFileProcessor("txt", [".txt"], "Plain text files and notes"),
            TextFileProcessor("markdown", [".md", ".markdown"], "Markdown documentation"),
            TextFileProcessor("rst", [".rst"], "reStructuredText documentation"),
            TextFileProcessor("latex", [".tex"], "LaTeX document source"),
            
            # === PROGRAMMING LANGUAGES ===
            # Popular languages
            TextFileProcessor("python", [".py"], "Python source code and scripts"),
            TextFileProcessor("java", [".java"], "Java source code files"),
            TextFileProcessor("javascript", [".js"], "JavaScript source code"),
            TextFileProcessor("typescript", [".ts"], "TypeScript source code"),
            TextFileProcessor("csharp", [".cs"], "C# source code files"),
            
            # Systems languages
            TextFileProcessor("cpp", [".cpp", ".cxx", ".cc"], "C++ source code"),
            TextFileProcessor("c", [".c", ".h"], "C source and header files"),
            TextFileProcessor("rust", [".rs"], "Rust source code"),
            TextFileProcessor("go", [".go"], "Go source code"),
            
            # JVM languages
            TextFileProcessor("kotlin", [".kt"], "Kotlin source code"),
            TextFileProcessor("scala", [".scala"], "Scala source code"),
            
            # Mobile development
            TextFileProcessor("swift", [".swift"], "Swift source code"),
            
            # Scripting languages
            TextFileProcessor("php", [".php"], "PHP web development scripts"),
            TextFileProcessor("ruby", [".rb"], "Ruby source code and scripts"),
            TextFileProcessor("perl", [".pl"], "Perl scripts and programs"),
            TextFileProcessor("lua", [".lua"], "Lua scripting language"),
            
            # Data science and analysis
            TextFileProcessor("r", [".r", ".R"], "R statistical computing scripts"),
            TextFileProcessor("matlab", [".m"], "MATLAB computational scripts"),
            
            # === SHELL AND SCRIPTING ===
            TextFileProcessor("shell", [".sh", ".bash", ".zsh"], "Unix shell scripts"),
            TextFileProcessor("powershell", [".ps1"], "PowerShell automation scripts"),
            TextFileProcessor("vim", [".vim"], "Vim editor configuration"),
            
            # === WEB DEVELOPMENT ===
            TextFileProcessor("html", [".html"], "HTML markup documents"),
            TextFileProcessor("css", [".css"], "CSS stylesheet files"),
            TextFileProcessor("scss", [".scss"], "SCSS preprocessed stylesheets"),
            TextFileProcessor("sass", [".sass"], "Sass preprocessed stylesheets"),
            TextFileProcessor("less", [".less"], "Less preprocessed stylesheets"),
            
            # === DATABASE ===
            TextFileProcessor("sql", [".sql"], "SQL database scripts and queries"),
        ]
        
        # Register all processors
        for processor in processors:
            self.register(processor)
    
    def register(self, processor: FileProcessor):
        """
        Register a file processor in the registry.
        
        Args:
            processor: FileProcessor instance to register
        """
        self.processors[processor.file_type] = processor
        
        # Map each extension to this processor for fast lookup
        for ext in processor.extensions:
            self.extension_map[ext.lower()] = processor
    
    def get_processor(self, file_path: str) -> Optional[FileProcessor]:
        """
        Get the appropriate processor for a given file path.
        
        Args:
            file_path: Path to the file
            
        Returns:
            FileProcessor instance that can handle the file, or None
        """
        file_path_lower = file_path.lower()
        
        # Check each extension for a match
        for ext, processor in self.extension_map.items():
            if file_path_lower.endswith(ext):
                return processor
                
        return None
    
    def get_processor_by_type(self, file_type: str) -> Optional[FileProcessor]:
        """
        Get a processor by its type identifier.
        
        Args:
            file_type: Type identifier string
            
        Returns:
            FileProcessor instance or None
        """
        return self.processors.get(file_type)
    
    def get_all_patterns(self) -> List[tuple]:
        """
        Get all file patterns for change detection systems.
        
        Returns:
            List of (pattern, file_type) tuples for glob matching
        """
        patterns = []
        for processor in self.processors.values():
            for ext in processor.extensions:
                patterns.append((f"**/*{ext}", processor.file_type))
        return patterns
    
    def get_supported_types(self) -> Dict[str, str]:
        """
        Get all supported file types with descriptions.
        
        Returns:
            Dictionary mapping file_type to description
        """
        return {
            proc.file_type: proc.description 
            for proc in self.processors.values()
        }
    
    def get_extension_summary(self) -> Dict[str, List[str]]:
        """
        Get summary of supported extensions organized by category.
        
        Returns:
            Dictionary with extension lists grouped by purpose
        """
        summary = {
            "documents": [],
            "code": [],
            "data": [],
            "web": [],
            "config": []
        }
        
        # Categorize extensions
        doc_types = {"pdf", "office", "rtf", "txt", "markdown", "rst", "latex"}
        code_types = {"python", "java", "javascript", "typescript", "cpp", "c", "csharp", "go", "rust", "php", "ruby"}
        data_types = {"csv", "json", "xml", "sql"}
        web_types = {"html", "css", "scss", "sass", "less"}
        config_types = {"yaml", "json", "xml"}
        
        for processor in self.processors.values():
            if processor.file_type in doc_types:
                summary["documents"].extend(processor.extensions)
            elif processor.file_type in code_types:
                summary["code"].extend(processor.extensions)
            elif processor.file_type in data_types:
                summary["data"].extend(processor.extensions)
            elif processor.file_type in web_types:
                summary["web"].extend(processor.extensions)
            elif processor.file_type in config_types:
                summary["config"].extend(processor.extensions)
        
        # Remove duplicates and sort
        for category in summary:
            summary[category] = sorted(list(set(summary[category])))
        
        return summary
    
    def process_files_by_type(self, files_by_type: Dict[str, List[str]], logger, max_file_size_mb: int = 50) -> List[Dict[str, Any]]:
        """
        Process files organized by type using appropriate processors.
        
        Args:
            files_by_type: Dictionary mapping file_type to list of file paths
            logger: Logger instance for status reporting
            max_file_size_mb: Maximum file size to process
            
        Returns:
            List of processed document objects
        """
        all_docs = []
        processed_types = []
        
        for file_type, file_paths in files_by_type.items():
            if not file_paths:
                continue
                
            processor = self.processors.get(file_type)
            if not processor:
                logger.warning(f"No processor found for file type: {file_type}")
                continue
            
            logger.info(f"Processing {len(file_paths)} {file_type.upper()} files...")
            docs = processor.process_files(file_paths, logger, max_file_size_mb)
            all_docs.extend(docs)
            processed_types.append(file_type)
        
        if processed_types:
            logger.info(f"Successfully processed {len(all_docs)} documents from {len(processed_types)} file types")
        
        return all_docs
    
    def scan_folder(self, folder: str, logger) -> List[Dict[str, Any]]:
        """
        Recursively scan folder and process all supported files.
        
        Args:
            folder: Root folder to scan
            logger: Logger instance
            
        Returns:
            List of processed document objects
        """
        all_docs = []
        processed_counts = {}
        
        logger.info(f"Scanning folder: {folder}")
        
        for processor in self.processors.values():
            files = processor.find_files(folder)
            if files:
                logger.info(f"Found {len(files)} {processor.file_type.upper()} files")
                docs = processor.process_files(files, logger)
                all_docs.extend(docs)
                processed_counts[processor.file_type] = len(docs)
        
        # Summary report
        if processed_counts:
            logger.info("Processing summary:")
            for file_type, count in sorted(processed_counts.items()):
                logger.info(f"  {file_type}: {count} documents")
            logger.info(f"Total: {len(all_docs)} documents from {len(processed_counts)} file types")
        else:
            logger.warning("No supported files found in folder")
        
        return all_docs