"""
LocalWise CLI Module

This module provides a comprehensive command-line interface for LocalWise,
enabling users to control all aspects of document processing, system management,
and application lifecycle through intuitive terminal commands.

CLI Features:
- Intuitive step-by-step processing workflow
- Comprehensive system status monitoring and diagnostics  
- Advanced processing options (incremental updates, force refresh)
- File tracking and management capabilities
- Integrated help system with detailed examples
- Cross-platform compatibility and error handling

Command Categories:

1. **Processing Workflow**:
   - --step1: Document text extraction
   - --step2: AI embedding generation
   - --step3: Web application launch

2. **Processing Options**:
   - --incremental: Process only changed files
   - --force-refresh: Reprocess all files
   - --clean-start: Fresh start with cleanup

3. **System Management**:
   - --status: Comprehensive system status
   - --validate: System integrity checks
   - --list-files: File tracking information

4. **Information Commands**:
   - --examples: Detailed usage examples
   - --config-check: Configuration display
   - --help: Command reference

Design Philosophy:
- Clear, actionable feedback with visual indicators
- Progressive workflow guidance for new users
- Advanced options for power users
- Comprehensive error handling and troubleshooting
- Consistent interface patterns across all commands

Version: 1.0.0
Author: LocalWise Development Team
"""

from .cli_interface import (
    LocalWiseCLI,
    create_argument_parser,
    handle_clean_start,
    handle_status,
    handle_list_files,
    launch_streamlit_app,
    handle_command_line_args,
    show_help_text
)

__all__ = [
    # Main CLI Manager
    'LocalWiseCLI',
    
    # Convenience Functions
    'create_argument_parser',
    'handle_clean_start',
    'handle_status',
    'handle_list_files',
    'launch_streamlit_app',
    'handle_command_line_args',
    'show_help_text'
]