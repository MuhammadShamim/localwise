"""
LocalWise Command Line Interface Module

This module provides a comprehensive command-line interface for LocalWise,
enabling users to control document processing, system management, and application
lifecycle through intuitive commands and workflows.

Key Features:
- Intuitive command structure with step-by-step processing
- Comprehensive status monitoring and system diagnostics
- Advanced processing options (incremental, force refresh, clean start)
- File management and tracking capabilities
- Integrated help system with usage examples

CLI Architecture:
- ArgumentParser-based command structure for clarity
- Modular command handlers for maintainability
- Integration with LocalWise core services
- Comprehensive error handling and user feedback
- Cross-platform compatibility

Command Categories:
1. Processing Commands: Step-by-step document processing workflow
2. Management Commands: System status, file tracking, cleanup
3. Advanced Options: Incremental updates, force refresh, diagnostics
4. Information Commands: Status reporting, file listing, help

Version: 1.0.0
Author: LocalWise Development Team
"""

import argparse
import sys
import subprocess
import os
import shutil
from typing import Optional, Dict, Any, List
from pathlib import Path

import config
from ..data.data_manager import DataManager
from ..data.file_manifest import FileManifest
from ..core.embedding_service import EmbeddingService


class LocalWiseCLI:
    """
    Comprehensive command-line interface for LocalWise operations.
    
    This class provides a unified interface for document processing,
    system management, and application control through command-line
    operations with clear feedback and error handling.
    
    Features:
    - Step-by-step processing workflow
    - System health monitoring and diagnostics
    - Advanced processing options and configurations
    - File tracking and manifest management
    - Integrated help and documentation
    
    Attributes:
        data_manager (DataManager): Data management service
        file_manifest (FileManifest): File tracking service  
        embedding_service (EmbeddingService): Embedding management service
    """
    
    def __init__(self):
        """Initialize CLI with service integrations."""
        self.data_manager = DataManager()
        self.file_manifest = FileManifest()
        self.embedding_service = EmbeddingService()
    
    def create_argument_parser(self) -> argparse.ArgumentParser:
        """
        Create and configure the comprehensive argument parser.
        
        Returns:
            Configured ArgumentParser with all LocalWise commands
        """
        parser = argparse.ArgumentParser(
            description="LocalWise v1.0.0 - AI-Powered Document Knowledge Assistant",
            epilog="For detailed usage examples, run: python ingest.py --examples",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Processing workflow commands
        workflow_group = parser.add_argument_group("Processing Workflow")
        step_group = workflow_group.add_mutually_exclusive_group()
        
        step_group.add_argument(
            "--step1", action="store_true",
            help="Step 1: Extract text from documents (no AI required)"
        )
        step_group.add_argument(
            "--step2", action="store_true", 
            help="Step 2: Generate AI embeddings from text (requires Ollama)"
        )
        step_group.add_argument(
            "--step3", action="store_true",
            help="Step 3: Launch interactive web application"
        )
        
        # Processing options
        options_group = parser.add_argument_group("Processing Options")
        options_group.add_argument(
            "--incremental", action="store_true",
            help="Process only new or modified files (faster updates)"
        )
        options_group.add_argument(
            "--force-refresh", action="store_true",
            help="Force reprocessing of all files (ignore change detection)"
        )
        
        # Management commands
        mgmt_group = parser.add_argument_group("Management Commands")
        mgmt_group.add_argument(
            "--clean-start", action="store_true",
            help="Remove all processed data and start fresh"
        )
        mgmt_group.add_argument(
            "--status", action="store_true",
            help="Display comprehensive system status"
        )
        mgmt_group.add_argument(
            "--list-files", action="store_true",
            help="List all tracked files with processing information"
        )
        mgmt_group.add_argument(
            "--validate", action="store_true",
            help="Validate system integrity and configuration"
        )
        
        # Information commands
        info_group = parser.add_argument_group("Information Commands")
        info_group.add_argument(
            "--examples", action="store_true",
            help="Show detailed usage examples and workflows"
        )
        info_group.add_argument(
            "--version", action="version", 
            version="LocalWise v1.0.0",
            help="Show version information"
        )
        
        # Advanced options
        advanced_group = parser.add_argument_group("Advanced Options")
        advanced_group.add_argument(
            "--config-check", action="store_true",
            help="Display current configuration settings"
        )
        advanced_group.add_argument(
            "--benchmark", action="store_true",
            help="Run system performance benchmarks"
        )
        
        return parser
    
    def handle_clean_start(self, logger) -> bool:
        """
        Handle the clean start operation with comprehensive cleanup.
        
        Args:
            logger: Logger instance for status reporting
            
        Returns:
            True if cleanup successful, False otherwise
        """
        logger.info("Performing clean start operation...")
        print("🧹 Clean Start: Removing all processed data...")
        print("=" * 50)
        
        success = True
        
        try:
            # Clear processed data
            if self.data_manager.clear_processed_data():
                print("✅ Cleared processed text data")
            else:
                print("⚠️  No processed data to clear")
            
            # Clear vector database
            if self.embedding_service.clear_embeddings():
                print("✅ Cleared vector database")
            else:
                print("⚠️  No vector database to clear")
            
            # Clear file manifest
            manifest_file = self.file_manifest.manifest_file
            if os.path.exists(manifest_file):
                os.remove(manifest_file)
                print("✅ Cleared file tracking manifest")
            else:
                print("⚠️  No manifest file to clear")
            
            # Remove entire database directory if empty
            if os.path.exists(config.DB_FOLDER):
                try:
                    if not os.listdir(config.DB_FOLDER):  # Directory is empty
                        os.rmdir(config.DB_FOLDER)
                        print("✅ Removed empty database directory")
                    else:
                        print("ℹ️  Database directory contains other files")
                except OSError:
                    pass  # Directory not empty or other OS issue
            
            print("\\n🎉 Clean start completed successfully!")
            print("You can now run Step 1 to begin fresh processing.")
            
        except Exception as e:
            logger.error(f"Error during clean start: {e}")
            print(f"❌ Error during cleanup: {e}")
            success = False
        
        return success
    
    def handle_status(self) -> Dict[str, Any]:
        """
        Handle comprehensive system status reporting.
        
        Returns:
            Dictionary with detailed status information
        """
        print("📊 LocalWise System Status")
        print("=" * 50)
        
        status = {}
        
        # Directory validation
        try:
            is_valid, dir_msg = config.validate_directories()
            if is_valid:
                print("✅ **Directories**: All required directories ready")
                status["directories"] = {"status": "ready", "message": dir_msg}
            else:
                print(f"❌ **Directories**: {dir_msg}")
                status["directories"] = {"status": "error", "message": dir_msg}
        except Exception as e:
            print(f"❌ **Directories**: Error checking - {e}")
            status["directories"] = {"status": "error", "message": str(e)}
        
        # Ollama service status
        try:
            is_available, error_msg = config.validate_ollama_connection()
            if is_available:
                print(f"✅ **Ollama**: Connected and ready ({config.OLLAMA_MODEL})")
                status["ollama"] = {"status": "ready", "model": config.OLLAMA_MODEL}
            else:
                print(f"❌ **Ollama**: {error_msg}")
                status["ollama"] = {"status": "error", "message": error_msg}
        except Exception as e:
            print(f"❌ **Ollama**: Connection error - {e}")
            status["ollama"] = {"status": "error", "message": str(e)}
        
        # Database status
        try:
            db_exists, db_error = config.validate_database_exists()
            if db_exists:
                print("✅ **Database**: Vector database ready")
                
                # Get database statistics
                embedding_stats = self.embedding_service.get_embedding_stats()
                if embedding_stats:
                    doc_count = embedding_stats.get("document_count", "Unknown")
                    print(f"   📊 Contains {doc_count:,} document vectors")
                    status["database"] = {"status": "ready", "document_count": doc_count}
                else:
                    status["database"] = {"status": "ready", "document_count": 0}
            else:
                print(f"❌ **Database**: {db_error}")
                status["database"] = {"status": "error", "message": db_error}
        except Exception as e:
            print(f"❌ **Database**: Error checking - {e}")
            status["database"] = {"status": "error", "message": str(e)}
        
        # Processed data status
        try:
            processed_info = self.data_manager.get_processed_data_info()
            if processed_info:
                chunk_count = processed_info.get("chunk_count", 0)
                file_size = processed_info.get("file_size_mb", 0)
                print(f"✅ **Processed Data**: {chunk_count:,} text chunks ({file_size:.1f} MB)")
                
                if processed_info.get("incremental"):
                    new_chunks = processed_info.get("new_chunks", 0)
                    print(f"   🔄 Last update: {new_chunks:,} new chunks")
                
                status["processed"] = {
                    "status": "ready",
                    "chunk_count": chunk_count,
                    "size_mb": file_size,
                    "incremental": processed_info.get("incremental", False)
                }
            else:
                print("❌ **Processed Data**: No processed documents found")
                status["processed"] = {"status": "missing"}
        except Exception as e:
            print(f"❌ **Processed Data**: Error checking - {e}")
            status["processed"] = {"status": "error", "message": str(e)}
        
        # File manifest status
        try:
            manifest_stats = self.file_manifest.get_manifest_statistics()
            if manifest_stats.get("file_count", 0) > 0:
                file_count = manifest_stats["file_count"]
                total_size = manifest_stats.get("total_size_mb", 0)
                print(f"✅ **File Tracking**: {file_count:,} files tracked ({total_size:.1f} MB)")
                
                file_types = manifest_stats.get("file_types", {})
                if file_types:
                    print("   📋 File types:", ", ".join([f"{k}({v})" for k, v in file_types.items()]))
                
                status["manifest"] = {
                    "status": "ready",
                    "file_count": file_count,
                    "total_size_mb": total_size,
                    "file_types": file_types
                }
            else:
                print("❌ **File Tracking**: No files tracked yet")
                status["manifest"] = {"status": "empty"}
        except Exception as e:
            print(f"❌ **File Tracking**: Error checking - {e}")
            status["manifest"] = {"status": "error", "message": str(e)}
        
        # Overall system readiness
        print("\\n" + "=" * 50)
        ready_components = sum([
            status.get("directories", {}).get("status") == "ready",
            status.get("ollama", {}).get("status") == "ready", 
            status.get("database", {}).get("status") == "ready",
            status.get("processed", {}).get("status") == "ready"
        ])
        
        if ready_components == 4:
            print("🎉 **System Status**: All components ready! You can ask questions.")
        elif ready_components >= 2:
            print(f"⚠️  **System Status**: {ready_components}/4 components ready. Review issues above.")
        else:
            print(f"❌ **System Status**: {ready_components}/4 components ready. Setup required.")
        
        status["overall"] = {"ready_components": ready_components, "total_components": 4}
        
        return status
    
    def handle_list_files(self) -> Dict[str, List[str]]:
        """
        Handle comprehensive file listing with organization.
        
        Returns:
            Dictionary organizing files by type
        """
        print("📁 Tracked Files & Processing History")
        print("=" * 50)
        
        manifest = self.file_manifest.load_file_manifest()
        
        if not manifest or len(manifest) <= 1:  # Account for metadata entry
            print("No files are currently being tracked.")
            print("\\nRun Step 1 processing to begin tracking files:")
            print("   python ingest.py --step1")
            return {}
        
        # Extract file entries (exclude metadata)
        file_entries = {k: v for k, v in manifest.items() if k != "_manifest_info"}
        
        # Organize files by type
        by_type = {}
        for file_path, file_info in file_entries.items():
            file_type = file_info.get('type', 'unknown')
            if file_type not in by_type:
                by_type[file_type] = []
            by_type[file_type].append((file_path, file_info))
        
        # Display organized file listing
        total_files = 0
        total_size = 0
        
        for file_type, files in sorted(by_type.items()):
            print(f"\\n📂 **{file_type.upper()}** ({len(files)} files)")
            print("   " + "-" * 60)
            
            type_size = 0
            for file_path, file_info in sorted(files):
                file_size = file_info.get('size', 0)
                last_processed = file_info.get('last_processed', 'Never')
                processing_count = file_info.get('processing_count', 0)
                
                # Format file size
                if file_size > 1024 * 1024:
                    size_str = f"{file_size / (1024 * 1024):.1f}MB"
                elif file_size > 1024:
                    size_str = f"{file_size / 1024:.1f}KB"
                else:
                    size_str = f"{file_size}B"
                
                # Display file info
                print(f"   📄 {os.path.basename(file_path)}")
                print(f"      Path: {file_path}")
                print(f"      Size: {size_str} | Processed: {processing_count}x | Last: {last_processed}")
                
                type_size += file_size
                
            total_files += len(files)
            total_size += type_size
            
            # Type summary
            type_size_mb = type_size / (1024 * 1024)
            print(f"   📊 Subtotal: {len(files)} files, {type_size_mb:.1f}MB")
        
        # Overall summary
        print("\\n" + "=" * 50)
        total_size_mb = total_size / (1024 * 1024)
        print(f"📈 **Summary**: {total_files:,} files tracked, {total_size_mb:.1f}MB total")
        
        # Return organized data
        return {file_type: [path for path, _ in files] for file_type, files in by_type.items()}
    
    def handle_validate(self) -> Dict[str, Any]:
        """
        Handle comprehensive system validation.
        
        Returns:
            Dictionary with validation results and recommendations
        """
        print("🔍 LocalWise System Validation")
        print("=" * 50)
        
        validation_results = {}
        issues_found = 0
        
        # Validate data integrity
        print("\\n📊 **Data Integrity Check**")
        is_valid, data_issues = self.data_manager.validate_data_integrity()
        
        if is_valid:
            print("   ✅ Processed data integrity verified")
            validation_results["data_integrity"] = {"status": "valid"}
        else:
            print("   ❌ Data integrity issues found:")
            for issue in data_issues:
                print(f"      • {issue}")
            validation_results["data_integrity"] = {"status": "invalid", "issues": data_issues}
            issues_found += len(data_issues)
        
        # Validate file manifest
        print("\\n📁 **File Manifest Validation**")
        manifest_stats = self.file_manifest.get_manifest_statistics()
        
        if manifest_stats.get("health") == "good":
            print("   ✅ File manifest is healthy")
            validation_results["manifest"] = {"status": "healthy"}
        else:
            missing_files = manifest_stats.get("missing_files", 0)
            if missing_files > 0:
                print(f"   ⚠️  {missing_files} tracked files no longer exist")
                validation_results["manifest"] = {"status": "needs_cleanup", "missing_files": missing_files}
                issues_found += 1
        
        # Validate system configuration
        print("\\n⚙️  **Configuration Validation**")
        config_issues = []
        
        if not os.path.exists(config.DOCS_FOLDER):
            config_issues.append(f"Documents folder missing: {config.DOCS_FOLDER}")
        
        if not hasattr(config, 'OLLAMA_MODEL') or not config.OLLAMA_MODEL:
            config_issues.append("Ollama model not configured")
        
        if config_issues:
            print("   ❌ Configuration issues found:")
            for issue in config_issues:
                print(f"      • {issue}")
            validation_results["configuration"] = {"status": "invalid", "issues": config_issues}
            issues_found += len(config_issues)
        else:
            print("   ✅ Configuration is valid")
            validation_results["configuration"] = {"status": "valid"}
        
        # Summary and recommendations
        print("\\n" + "=" * 50)
        if issues_found == 0:
            print("🎉 **Validation Summary**: No issues found! System is healthy.")
            validation_results["overall"] = {"status": "healthy", "issues": 0}
        else:
            print(f"⚠️  **Validation Summary**: {issues_found} issues found.")
            print("\\n💡 **Recommendations**:")
            
            if validation_results.get("data_integrity", {}).get("status") == "invalid":
                print("   • Consider reprocessing documents: python ingest.py --clean-start")
            
            if validation_results.get("manifest", {}).get("missing_files", 0) > 0:
                print("   • Clean up file tracking: Restart processing to refresh manifest")
            
            validation_results["overall"] = {"status": "issues_found", "issues": issues_found}
        
        return validation_results
    
    def handle_examples(self):
        """Display comprehensive usage examples and workflows."""
        examples_text = """
🧠 LocalWise v1.0.0 - Usage Examples & Workflows

==================================================
BASIC WORKFLOWS
==================================================

🚀 Quick Start (Full Processing):
   python ingest.py                 # Process all documents + create embeddings
   python ingest.py --step3         # Launch web interface

📋 Step-by-Step Processing:
   python ingest.py --step1         # Extract text from documents
   python ingest.py --step2         # Generate AI embeddings  
   python ingest.py --step3         # Start web application

==================================================
INCREMENTAL UPDATES
==================================================

🔄 Process Only Changed Files:
   python ingest.py --incremental   # Smart update (recommended)

🔁 Force Complete Refresh:
   python ingest.py --force-refresh # Reprocess everything

==================================================
SYSTEM MANAGEMENT
==================================================

📊 Check System Status:
   python ingest.py --status        # Comprehensive status report

📁 View Tracked Files:
   python ingest.py --list-files    # Show all processed files

🔍 Validate System:
   python ingest.py --validate      # Check for issues

🧹 Fresh Start:
   python ingest.py --clean-start   # Remove all data, start over

==================================================
TROUBLESHOOTING WORKFLOWS
==================================================

❌ If Ollama isn't working:
   1. ollama serve                  # Start Ollama service
   2. ollama pull {config.OLLAMA_MODEL}    # Install model
   3. python ingest.py --status     # Verify connection

❌ If documents aren't processing:
   1. python ingest.py --validate   # Check for issues
   2. python ingest.py --list-files # See what's tracked
   3. python ingest.py --step1      # Reprocess documents

❌ If embeddings fail:
   1. python ingest.py --status     # Check Ollama status
   2. python ingest.py --step2      # Retry embedding creation

==================================================
ADVANCED USAGE
==================================================

📈 Performance Monitoring:
   python ingest.py --benchmark     # Run performance tests

⚙️  Configuration Check:
   python ingest.py --config-check  # View current settings

🔧 Development Workflow:
   python ingest.py --clean-start   # Clear all data
   # ... add test documents ...
   python ingest.py --step1         # Test processing
   python ingest.py --step2         # Test embeddings
   python ingest.py --step3         # Test app

==================================================
SUPPORTED FILE TYPES
==================================================

📄 Documents: PDF, DOC, DOCX, TXT, RTF, Markdown
📊 Data: CSV, JSON, YAML, XML
💻 Code: Python, Java, JavaScript, TypeScript, SQL, C/C++, C#
🌐 Web: HTML, CSS, SCSS, Less
📋 Scripts: Shell, PowerShell, R, MATLAB
📝 Other: Plain text, configuration files

==================================================
DIRECTORY STRUCTURE
==================================================

LocalWise/
├── documents/      # 📁 Place your documents here
├── db/             # 💾 Vector database storage (auto-created)
├── app.py          # 🌐 Web application
├── ingest.py       # ⚙️  Processing pipeline
└── config.py       # 📋 Configuration settings

==================================================
GET HELP
==================================================

📖 Documentation: https://github.com/localwise/localwise/wiki
🐛 Issues: https://github.com/localwise/localwise/issues  
💬 Support: Run 'python ingest.py --status' for diagnostics

Happy knowledge discovery with LocalWise! 🚀
"""
        print(examples_text)
    
    def launch_streamlit_app(self, logger) -> bool:
        """
        Launch the Streamlit web application with prerequisite validation.
        
        Args:
            logger: Logger instance for status reporting
            
        Returns:
            True if launch successful, False otherwise
        """
        print("🚀 Step 3: Launching LocalWise Web Application")
        print("=" * 50)
        
        # Comprehensive prerequisite validation
        print("🔍 Validating prerequisites...")
        
        # Check database
        db_exists, db_error = config.validate_database_exists()
        if not db_exists:
            logger.error(f"Database validation failed: {db_error}")
            print(f"❌ **Database Error**: {db_error}")
            print("\\n🔧 **Solution**: Complete the processing pipeline first")
            print("   Step 1: python ingest.py --step1")
            print("   Step 2: python ingest.py --step2")
            return False
        
        # Check Ollama
        is_available, error_msg = config.validate_ollama_connection()
        if not is_available:
            logger.error(f"Ollama validation failed: {error_msg}")
            print(f"❌ **Ollama Error**: {error_msg}")
            print("\\n🔧 **Solution**: Start Ollama service")
            print("   1. ollama serve")
            print(f"   2. ollama pull {config.OLLAMA_MODEL}")
            return False
        
        print("✅ All prerequisites validated successfully!")
        print("\\n🌐 Starting Streamlit web server...")
        
        # Launch Streamlit with error handling
        try:
            app_path = os.path.join(os.path.dirname(__file__), "..", "..", "app.py")
            app_path = os.path.abspath(app_path)
            
            if not os.path.exists(app_path):
                # Try alternative path
                app_path = "app.py"
            
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", app_path,
                "--server.headless", "false",
                "--server.port", "8501",
                "--server.address", "localhost"
            ], check=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Streamlit launch failed: {e}")
            print("❌ Failed to launch Streamlit automatically.")
            print("\\n💡 **Manual Launch**:")
            print("   streamlit run app.py")
            return False
            
        except FileNotFoundError:
            logger.error("Streamlit not found in environment")
            print("❌ Streamlit is not installed.")
            print("\\n💡 **Installation**:")
            print("   pip install streamlit")
            print("   # Then try: streamlit run app.py")
            return False
        
        except KeyboardInterrupt:
            print("\\n🛑 Application stopped by user.")
            return True
    
    def handle_command_line_args(self) -> Optional[argparse.Namespace]:
        """
        Parse and validate command line arguments.
        
        Returns:
            Parsed arguments namespace or None if help should be shown
        """
        parser = self.create_argument_parser()
        
        # Handle no arguments case
        if len(sys.argv) == 1:
            parser.print_help()
            print("\\n" + "=" * 60)
            print("💡 **Quick Start**: python ingest.py --examples")
            print("📊 **Status Check**: python ingest.py --status")
            return None
        
        args = parser.parse_args()
        
        # Handle examples command
        if getattr(args, 'examples', False):
            self.handle_examples()
            return None
        
        return args


# Convenience functions for backward compatibility and easy access
def create_argument_parser() -> argparse.ArgumentParser:
    """Convenience function for creating argument parser."""
    cli = LocalWiseCLI()
    return cli.create_argument_parser()


def handle_clean_start(logger) -> bool:
    """Convenience function for clean start operation."""
    cli = LocalWiseCLI()
    return cli.handle_clean_start(logger)


def handle_status() -> Dict[str, Any]:
    """Convenience function for status reporting."""
    cli = LocalWiseCLI()
    return cli.handle_status()


def handle_list_files() -> Dict[str, List[str]]:
    """Convenience function for file listing."""
    cli = LocalWiseCLI()
    return cli.handle_list_files()


def launch_streamlit_app(logger) -> bool:
    """Convenience function for launching Streamlit app."""
    cli = LocalWiseCLI()
    return cli.launch_streamlit_app(logger)


def handle_command_line_args() -> Optional[argparse.Namespace]:
    """Convenience function for command line argument handling."""
    cli = LocalWiseCLI()
    return cli.handle_command_line_args()


def show_help_text():
    """Convenience function for showing help text."""
    cli = LocalWiseCLI()
    cli.handle_examples()