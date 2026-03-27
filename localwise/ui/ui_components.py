"""
LocalWise UI Components Module

This module provides reusable Streamlit UI components for the LocalWise application.
It implements a clean separation between presentation logic and business logic,
making the interface modular, maintainable, and consistent.

Key Components:
- Page configuration and layout management
- System status displays and health monitoring
- Interactive chat interface components
- Setup and troubleshooting guidance
- Processing status and statistics displays

Architecture:
- Functional component design for reusability
- Consistent styling and theming
- Error handling and user feedback
- Integration with LocalWise core services
- Responsive design principles

UI Philosophy:
- Clean, professional interface design
- Clear status communication with visual indicators
- Progressive disclosure of technical details
- Helpful guidance for users at all levels
- Accessibility and usability focus

Version: 1.0.0
Author: LocalWise Development Team
"""

import streamlit as st
import os
from typing import Optional, Dict, Any, Tuple

from localwise import config
from ..data.data_manager import DataManager
from ..core.embedding_service import EmbeddingService


class LocalWiseUI:
    """
    Main UI component manager for LocalWise Streamlit application.
    
    This class provides centralized management of UI components with
    consistent styling, theming, and interaction patterns.
    
    Features:
    - Centralized component management
    - Consistent styling and branding
    - Status monitoring and health checks
    - Interactive guidance and setup assistance
    - Responsive layout management
    """
    
    def __init__(self):
        """Initialize the UI manager with service integrations."""
        self.data_manager = DataManager()
        self.embedding_service = EmbeddingService()
    
    def configure_page(self):
        """
        Configure Streamlit page settings with LocalWise branding.
        
        Sets up page metadata, layout, and initial configuration
        for optimal user experience.
        """
        st.set_page_config(
            page_title="LocalWise - AI Knowledge Assistant",
            page_icon="🧠",
            layout="centered",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': 'https://github.com/localwise/localwise/wiki',
                'Report a Bug': 'https://github.com/localwise/localwise/issues',
                'About': '''
                # LocalWise v1.0.0
                
                Your AI-powered document knowledge assistant.
                
                **Features:**
                - Process 40+ file types
                - Natural language querying
                - Local AI processing with Ollama
                - Incremental document updates
                
                **Privacy:** All processing happens locally on your machine.
                '''
            }
        )
    
    def display_header(self, show_version: bool = True):
        """
        Display the main application header with professional branding.
        
        Args:
            show_version: Whether to display version information
        """
        version_text = " v1.0.0" if show_version else ""
        
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #2E86C1;">🧠 LocalWise{version_text}</h1>
            <h3 style="color: #5D6D7E; font-weight: 400;">AI-Powered Knowledge Assistant</h3>
            <p style="color: #85929E; font-style: italic; font-size: 1.1em;">
                Ask questions about your documents in natural language
            </p>
            <div style="border-bottom: 2px solid #E8F8F5; margin: 1rem auto; width: 60%;"></div>
        </div>
        """, unsafe_allow_html=True)
    
    def display_sidebar(self):
        """
        Display comprehensive system status and configuration in sidebar.
        
        Provides real-time monitoring of all LocalWise components with
        actionable status information and quick configuration overview.
        """
        st.sidebar.markdown("### 🔧 System Status")
        
        # Component health checks
        status = self._get_system_status()
        
        # Ollama Status
        if status["ollama"]["available"]:
            st.sidebar.success(f"🟢 **Ollama**: {config.OLLAMA_MODEL}")
            st.sidebar.caption(f"Model: {config.OLLAMA_MODEL}")
        else:
            st.sidebar.error(f"🔴 **Ollama**: {status['ollama']['message']}")
            with st.sidebar.expander("🔧 Ollama Setup"):
                st.code(f"""# Start Ollama service\\nollama serve\\n\\n# Install model\\nollama pull {config.OLLAMA_MODEL}""")
        
        # Database Status
        if status["database"]["ready"]:
            st.sidebar.success("🟢 **Database**: Ready")
            
            # Database statistics
            with st.sidebar.expander("📊 Database Stats"):
                if status["embeddings"]["stats"]:
                    stats = status["embeddings"]["stats"]
                    st.write(f"📄 Documents: {stats.get('document_count', 'N/A'):,}")
                
                if status["processed"]["info"]:
                    info = status["processed"]["info"]
                    st.write(f"📝 Text Chunks: {info.get('chunk_count', 0):,}")
                    st.write(f"💾 Data Size: {info.get('file_size_mb', 0):.1f} MB")
                    if info.get('incremental'):
                        st.write(f"🔄 New Chunks: {info.get('new_chunks', 0):,}")
        else:
            st.sidebar.error(f"🔴 **Database**: {status['database']['message']}")
            with st.sidebar.expander("🔧 Database Setup"):
                st.code("# Process your documents\\npython ingest.py --step1\\npython ingest.py --step2")
        
        # Configuration Information
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ⚙️ Configuration")
        
        config_info = [
            ("📁 Documents", config.DOCS_FOLDER.replace(os.path.expanduser("~"), "~")),
            ("💾 Database", config.DB_FOLDER.replace(os.path.expanduser("~"), "~")),
            ("🤖 AI Model", config.OLLAMA_MODEL),
            ("📊 Chunk Size", f"{config.CHUNK_SIZE:,} chars"),
            ("🔍 Search Results", f"{getattr(config, 'NUM_RETRIEVED_DOCS', 5)} docs")
        ]
        
        for label, value in config_info:
            st.sidebar.text(f"{label}: {value}")
        
        # Quick Start Guide
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📖 Quick Start")
        
        steps = [
            "📁 Add documents to `documents/` folder",
            "⚙️ Run `python ingest.py --step1`",
            "🧠 Run `python ingest.py --step2`",
            "💬 Ask questions here!"
        ]
        
        for i, step in enumerate(steps, 1):
            icon = "✅" if self._is_step_complete(i, status) else "⭕"
            st.sidebar.markdown(f"{icon} **{i}.** {step}")
        
        # Supported file types
        with st.sidebar.expander("📋 Supported Files"):
            file_types = [
                "**Documents**: PDF, DOCX, TXT, RTF, MD",
                "**Data**: JSON, YAML, XML, CSV",
                "**Code**: Python, Java, JavaScript, SQL",
                "**Web**: HTML, CSS, TypeScript"
            ]
            for file_type in file_types:
                st.markdown(f"• {file_type}")
    
    def display_status_dashboard(self):
        """
        Display a comprehensive system status dashboard.
        
        Provides detailed overview of processing status, database health,
        and system readiness with actionable information.
        """
        st.subheader("📊 System Dashboard")
        
        status = self._get_system_status()
        
        # Overall system health
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if status["ollama"]["available"]:
                st.metric("🤖 AI Service", "Online", border=True)
            else:
                st.metric("🤖 AI Service", "Offline", border=True)
        
        with col2:
            if status["database"]["ready"]:
                st.metric("💾 Database", "Ready", border=True)
            else:
                st.metric("💾 Database", "Not Ready", border=True)
        
        with col3:
            ready_count = sum([
                status["ollama"]["available"],
                status["database"]["ready"]
            ])
            st.metric("✅ System Health", f"{ready_count}/2 Ready", border=True)
        
        # Detailed status information
        if status["processed"]["info"]:
            st.markdown("#### 📈 Processing Statistics")
            info = status["processed"]["info"]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "📄 Text Chunks",
                    f"{info.get('chunk_count', 0):,}",
                    help="Number of processed text segments"
                )
            
            with col2:
                st.metric(
                    "💾 Data Size",
                    f"{info.get('file_size_mb', 0):.1f} MB",
                    help="Size of processed data storage"
                )
            
            with col3:
                last_process = "Incremental" if info.get('incremental') else "Full"
                st.metric(
                    "🔄 Last Process",
                    last_process,
                    help="Type of most recent processing"
                )
            
            with col4:
                if info.get('incremental') and info.get('new_chunks'):
                    st.metric(
                        "🆕 New Chunks",
                        f"{info.get('new_chunks', 0):,}",
                        help="Chunks added in last incremental update"
                    )
                else:
                    st.metric(
                        "📅 Last Updated",
                        "Today",  # Could be made more specific with timestamp parsing
                        help="When documents were last processed"
                    )
        
        # Vector database information
        if status["embeddings"]["exists"]:
            st.success("✅ **Vector Database Ready** - You can ask questions about your documents")
            if status["embeddings"]["stats"]:
                stats = status["embeddings"]["stats"]
                doc_count = stats.get('document_count', 'Unknown')
                st.info(f"🔍 **{doc_count:,} document vectors** available for semantic search")
        else:
            st.warning("⚠️ **Vector Database Not Found** - Process your documents first")
    
    def display_setup_instructions(self):
        """
        Display comprehensive setup instructions based on current system state.
        
        Provides step-by-step guidance tailored to what components
        are missing or misconfigured.
        """
        st.subheader("🚀 LocalWise Setup")
        
        status = self._get_system_status()
        
        # Step 1: Ollama Setup
        st.markdown("#### Step 1: AI Service (Ollama)")
        if status["ollama"]["available"]:
            st.success("✅ **Ollama is running and ready**")
            st.info(f"Using model: **{config.OLLAMA_MODEL}**")
        else:
            st.error(f"❌ **Ollama Issue**: {status['ollama']['message']}")
            
            with st.expander("🔧 Fix Ollama Setup"):
                st.markdown("""
                **Option A: Install Ollama**
                1. Download from [ollama.ai](https://ollama.ai)
                2. Install following the platform instructions
                3. Restart your terminal/command prompt
                
                **Option B: Start Ollama Service**
                """)
                st.code("ollama serve")
                
                st.markdown("**Option C: Install Required Model**")
                st.code(f"ollama pull {config.OLLAMA_MODEL}")
        
        # Step 2: Document Processing
        st.markdown("#### Step 2: Document Processing")
        if status["processed"]["exists"]:
            if status["embeddings"]["exists"]:
                st.success("✅ **Documents processed and embeddings created**")
                st.info("🎯 **Ready to answer questions!**")
            else:
                st.warning("⚠️ **Documents processed but embeddings missing**")
                st.code("python ingest.py --step2")
        else:
            st.warning("⚠️ **No processed documents found**")
            
            with st.expander("📁 Process Your Documents"):
                st.markdown(f"""
                **1. Add Documents**
                - Place your files in: `{config.DOCS_FOLDER}/`
                - Supports 40+ file types (PDF, DOCX, code files, etc.)
                
                **2. Process Documents**
                """)
                st.code("""python ingest.py --step1  # Extract text from documents
python ingest.py --step2  # Create AI embeddings""")
                
                st.markdown("""
                **3. Alternative: Full Pipeline**
                """)
                st.code("python ingest.py  # Complete processing")
    
    def display_chat_message(self, 
                           role: str, 
                           content: str, 
                           avatar: Optional[str] = None):
        """
        Display a chat message with consistent styling and avatars.
        
        Args:
            role: Message role ('user', 'assistant', or 'system')
            content: Message content to display
            avatar: Optional custom avatar (defaults based on role)
        """
        if avatar is None:
            avatars = {
                "assistant": "🧠",
                "user": "👤",
                "system": "⚙️"
            }
            avatar = avatars.get(role, "💬")
        
        with st.chat_message(role, avatar=avatar):
            st.markdown(content)
    
    def display_error_panel(self, 
                          title: str, 
                          message: str, 
                          solution: Optional[str] = None,
                          show_expander: bool = True):
        """
        Display a comprehensive error panel with solution guidance.
        
        Args:
            title: Error title
            message: Detailed error message
            solution: Optional solution steps
            show_expander: Whether to show solution in expandable section
        """
        st.error(f"**{title}**")
        st.markdown(message)
        
        if solution:
            if show_expander:
                with st.expander("🔧 Solution"):
                    st.markdown(solution)
            else:
                st.info(f"**💡 Solution**: {solution}")
    
    def display_loading_status(self, 
                             operation: str, 
                             progress: Optional[float] = None):
        """
        Display loading status with optional progress indication.
        
        Args:
            operation: Description of current operation
            progress: Optional progress value (0.0 to 1.0)
        """
        if progress is not None:
            st.progress(progress, text=f"🔄 {operation}")
        else:
            st.info(f"🔄 {operation}")
    
    def _get_system_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get comprehensive system status for all components.
        
        Returns:
            Dictionary with detailed status for each system component
        """
        # Ollama status
        ollama_available, ollama_msg = config.validate_ollama_connection()
        
        # Database status
        db_exists, db_msg = config.validate_database_exists()
        
        # Processed data status
        processed_info = self.data_manager.get_processed_data_info()
        processed_exists = processed_info is not None
        
        # Embedding status
        embeddings_exist = self.embedding_service.check_embeddings_exist()
        embedding_stats = self.embedding_service.get_embedding_stats()
        
        return {
            "ollama": {
                "available": ollama_available,
                "message": ollama_msg
            },
            "database": {
                "ready": db_exists,
                "message": db_msg
            },
            "processed": {
                "exists": processed_exists,
                "info": processed_info
            },
            "embeddings": {
                "exists": embeddings_exist,
                "stats": embedding_stats
            }
        }
    
    def _is_step_complete(self, step: int, status: Dict[str, Dict[str, Any]]) -> bool:
        """
        Check if a setup step is complete.
        
        Args:
            step: Step number (1-4)
            status: System status dictionary
            
        Returns:
            True if step is complete, False otherwise
        """
        if step == 1:  # Documents added
            return True  # We can't easily check this without scanning
        elif step == 2:  # Step 1 processing
            return status["processed"]["exists"]
        elif step == 3:  # Step 2 processing
            return status["embeddings"]["exists"]
        elif step == 4:  # Ready to ask questions
            return (status["ollama"]["available"] and 
                   status["embeddings"]["exists"])
        
        return False


# Convenience functions for backward compatibility and easy access
def configure_page():
    """Convenience function for page configuration."""
    ui = LocalWiseUI()
    ui.configure_page()


def display_header():
    """Convenience function for header display."""
    ui = LocalWiseUI()
    ui.display_header()


def display_sidebar():
    """Convenience function for sidebar display."""
    ui = LocalWiseUI()
    ui.display_sidebar()


def display_chat_message(role: str, content: str, avatar: Optional[str] = None):
    """Convenience function for chat message display."""
    ui = LocalWiseUI()
    ui.display_chat_message(role, content, avatar)


def display_processing_status():
    """Convenience function for processing status display."""
    ui = LocalWiseUI()
    ui.display_status_dashboard()


def display_setup_instructions():
    """Convenience function for setup instructions display."""
    ui = LocalWiseUI()
    ui.display_setup_instructions()


def display_error_message(title: str, 
                         message: str, 
                         solution: Optional[str] = None):
    """Convenience function for error message display."""
    ui = LocalWiseUI()
    ui.display_error_panel(title, message, solution)


def display_success_message(title: str, message: str):
    """Convenience function for success message display."""
    st.success(f"**{title}**")
    st.markdown(message)


def display_info_message(title: str, message: str):
    """Convenience function for info message display."""
    st.info(f"**{title}**")
    st.markdown(message)