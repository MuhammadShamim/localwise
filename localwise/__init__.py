"""
LocalWise v1.0.0 - Your AI Knowledge Assistant

A professional AI knowledge assistant that transforms your documents into an
intelligent, searchable knowledge base. Works entirely offline with no API keys
required, ensuring complete privacy and data security.

Key Features:
    - 40+ File Type Support: Process documents, code, spreadsheets, and more
    - Professional Architecture: Clean modular design with proper separation
    - 100% Private: No cloud dependencies or data sharing
    - Local AI: Powered by Ollama with health monitoring
    - Dual Interface: Both web UI and command-line interfaces
    - Smart Processing: Incremental updates and change detection
    - Enterprise Ready: Comprehensive documentation and error handling

Quick Start:
    >>> from localwise.core.query_engine import QueryEngine
    >>> from localwise.core.embedding_service import EmbeddingService
    >>> from localwise.data.data_manager import DataManager
    
    # Or use the CLI
    $ python -m localwise.cli process -d documents/
    $ python -m localwise.cli serve

Package Structure:
    localwise.core      - Core processing engines
    localwise.data      - Data management layer  
    localwise.ui        - User interface components
    localwise.cli       - Command-line interface

Author: LocalWise Development Team
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "LocalWise Development Team"
__email__ = "dev@localwise.ai"
__license__ = "MIT"

# Package metadata
__title__ = "LocalWise"
__description__ = "Your AI Knowledge Assistant - Transform documents into intelligent knowledge bases"
__url__ = "https://github.com/localwise/localwise"

# Version info tuple for programmatic access
VERSION_INFO = (1, 0, 0)

# Import core configuration for package-level access
try:
    from . import config
except ImportError:
    # Fallback for development mode
    import config

# Package-level convenience imports
try:
    from .core.query_engine import QueryEngine
    from .core.embedding_service import EmbeddingService
    from .data.data_manager import DataManager
    from .data.file_manifest import FileManifest
except ImportError:
    # Graceful handling for development or partial installations
    QueryEngine = None
    EmbeddingService = None
    DataManager = None
    FileManifest = None

# Public API exports
__all__ = [
    '__version__',
    '__author__',
    '__email__',
    '__license__',
    '__title__',
    '__description__',
    '__url__',
    'VERSION_INFO',
    'config',
    'QueryEngine',
    'EmbeddingService', 
    'DataManager',
    'FileManifest',
]


def get_version():
    """
    Get the current package version.
    
    Returns:
        str: The version string (e.g., "1.0.0")
    """
    return __version__


def get_version_info():
    """
    Get detailed version information.
    
    Returns:
        dict: Dictionary containing version details
    """
    return {
        'version': __version__,
        'version_info': VERSION_INFO,
        'title': __title__,
        'description': __description__,
        'author': __author__,
        'license': __license__,
        'url': __url__,
    }


def show_banner():
    """Display the LocalWise banner with version information."""
    banner = f"""
    ╭─────────────────────────────────────────────────────────────╮
    │                                                             │
    │  🧠 {__title__} v{__version__} - Your AI Knowledge Assistant        │
    │                                                             │
    │  Transform documents into intelligent, searchable           │
    │  knowledge bases. Works entirely offline with complete     │
    │  privacy and no API keys required.                         │
    │                                                             │
    │  📚 40+ File Types  🔒 100% Private  ⚡ 3-Min Setup        │
    │                                                             │
    ╰─────────────────────────────────────────────────────────────╯
    """
    print(banner)


# Development and debugging helpers
def check_installation():
    """
    Check if LocalWise is properly installed and configured.
    
    Returns:
        dict: Installation status information
    """
    status = {
        'package_version': __version__,
        'core_modules': {},
        'config_available': config is not None,
        'ollama_configured': False,
        'database_path': None,
    }
    
    # Check core modules
    core_modules = ['QueryEngine', 'EmbeddingService', 'DataManager', 'FileManifest']
    for module_name in core_modules:
        module = globals().get(module_name)
        status['core_modules'][module_name] = module is not None
    
    # Check configuration if available
    if config:
        try:
            status['ollama_configured'] = hasattr(config, 'OLLAMA_BASE_URL')
            status['database_path'] = getattr(config, 'DATABASE_PATH', None)
        except Exception:
            pass
    
    return status


if __name__ == "__main__":
    # When run directly, show package information
    show_banner()
    print("\nPackage Information:")
    info = get_version_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\nInstallation Check:")
    install_status = check_installation()
    for key, value in install_status.items():
        print(f"  {key}: {value}")