"""
LocalWise UI Module

This module provides comprehensive user interface components for LocalWise,
implementing a clean and professional Streamlit-based web application.

UI Components:
- ui_components: Reusable UI components with consistent styling and behavior
- System status monitoring and health indicators
- Interactive setup guidance and troubleshooting
- Chat interface for natural language interactions
- Responsive design with professional theming

Key Features:
- Modular component architecture for easy maintenance
- Consistent branding and visual identity
- Real-time system status monitoring
- Progressive user guidance and onboarding
- Accessibility and usability optimizations
- Error handling with clear user feedback

Design Philosophy:
- Clean, professional interface design
- User-centered experience with clear navigation
- Helpful guidance for users at all technical levels
- Visual status communication with meaningful icons
- Responsive layout that works on different screen sizes

Usage:
The UI module integrates with LocalWise core services to provide:
- Document processing status and statistics
- System health monitoring and diagnostics
- Interactive chat interface for document queries
- Setup guidance and troubleshooting assistance

Version: 1.0.0
Author: LocalWise Development Team
"""

from .ui_components import (
    LocalWiseUI,
    configure_page,
    display_header,
    display_sidebar,
    display_chat_message,
    display_processing_status,
    display_setup_instructions,
    display_error_message,
    display_success_message,
    display_info_message
)

__all__ = [
    # Main UI Manager
    'LocalWiseUI',
    
    # Convenience Functions
    'configure_page',
    'display_header',
    'display_sidebar',
    'display_chat_message',
    'display_processing_status',
    'display_setup_instructions',
    'display_error_message',
    'display_success_message', 
    'display_info_message'
]