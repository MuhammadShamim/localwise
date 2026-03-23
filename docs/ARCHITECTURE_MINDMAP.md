# LocalWise File Interaction Mindmap

This Mermaid mindmap diagram shows the complete file structure and interactions within the LocalWise v1.0.0 project.

## Diagram

```mermaid
mindmap
  root((LocalWise v1.0.0))
    
    Entry Points
      app.py
        ::icon(fa fa-desktop)
        Streamlit Interface
          Imports localwise.ui
          Imports localwise.core
          Imports localwise config
      ingest.py
        ::icon(fa fa-cog)
        Document Processing
          Imports localwise.core
          Imports localwise.data
          Imports localwise.cli
    
    Package Structure
      localwise/
        ::icon(fa fa-cube)
        Core Package
          __init__.py
            ::icon(fa fa-file-code)
            Package Entry
              Exports QueryEngine
              Exports EmbeddingService 
              Exports DataManager
              Version Management
          config.py
            ::icon(fa fa-wrench)
            Configuration
              Database Paths
              Ollama Settings
              Validation Functions
        
        core/
          ::icon(fa fa-microchip)
          Processing Engines
            file_processors.py
              ::icon(fa fa-file-archive)
              40+ File Types
                PDF Processor
                CSV Processor
                Code Processors
                Registry Pattern
            embedding_service.py
              ::icon(fa fa-brain)
              AI Embeddings
                ChromaDB Integration
                Ollama Connection
                Batch Processing
            query_engine.py
              ::icon(fa fa-search)
              RAG Pipeline
                Document Search
                LLM Integration
                Context Preparation
        
        data/
          ::icon(fa fa-database)
          Data Management
            data_manager.py
              ::icon(fa fa-save)
              Data Operations
                Atomic Saves
                Integrity Validation
                Statistics Tracking
            file_manifest.py
              ::icon(fa fa-list)
              Change Detection
                MD5 Hashing
                File Tracking
                Bulk Operations
            change_detector.py
              ::icon(fa fa-eye)
              Incremental Updates
                Manifest Comparison
                Quick Scanning
                Performance Stats
        
        ui/
          ::icon(fa fa-paint-brush)
          Interface Components
            ui_components.py
              ::icon(fa fa-window-maximize)
              Streamlit Components
                Status Dashboard
                Error Handling
                Chat Interface
        
        cli/
          ::icon(fa fa-terminal)
          Command Line
            cli_interface.py
              ::icon(fa fa-keyboard)
              CLI Commands
                Process Documents
                System Validation
                Health Checks
                Help System
    
    Configuration Files
      setup.py
        ::icon(fa fa-box)
        Package Installation
          Dependencies
          Entry Points
          Metadata
      requirements.txt
        ::icon(fa fa-list-alt)
        Dependencies
          LangChain Stack
          Streamlit
          ChromaDB
          Ollama Integration
      setup.cfg
        ::icon(fa fa-cogs)
        Build Configuration
          Package Metadata
          Development Tools
          Testing Setup
      MANIFEST.in
        ::icon(fa fa-archive)
        Distribution Rules
          Include Patterns
          Exclude Patterns
          Package Data
    
    Documentation
      README.md
        ::icon(fa fa-book-open)
        Main Documentation
          Installation Guide
          Quick Start
          Architecture Overview
      docs/
        ::icon(fa fa-folder-open)
        Project Documentation
          CHANGELOG.md
            ::icon(fa fa-history)
            Release Notes
          TEAM_WORKFLOW.md
            ::icon(fa fa-users)
            Development Process
          DOCUMENTATION_INDEX.md
            ::icon(fa fa-sitemap)
            Navigation Hub
    
    User Data
      documents/
        ::icon(fa fa-file-import)
        Input Documents
          Test Files
            LocalWiseTest.java
            test_python_processing.py
            localwise_test_queries.sql
            plain_text_test.txt
            TEXT_PROCESSING_TEST.md
      
      Generated Data
        db/
          ::icon(fa fa-hdd)
          Processed Data
            processed_chunks.json
            File Metadata
        my_vectordb/
          ::icon(fa fa-vector-square)
          Vector Database
            ChromaDB Files
            Embeddings Storage
        localwise.log
          ::icon(fa fa-file-text)
          Application Logs
```

## Key Interactions

### Entry Points Flow
1. **app.py** → Streamlit web interface → imports `localwise.ui`, `localwise.core`
2. **ingest.py** → Document processing → imports `localwise.core`, `localwise.data`, `localwise.cli`

### Core Package Dependencies
- **localwise/__init__.py** → Central package entry, exports main classes
- **localwise/config.py** → Configuration used by all modules
- **Core engines** process documents and handle AI operations
- **Data layer** manages persistence and change detection
- **UI/CLI** provide user interfaces

### Data Flow
1. **documents/** → **file_processors.py** → **data_manager.py** → **db/**
2. **db/** → **embedding_service.py** → **my_vectordb/**
3. **User query** → **query_engine.py** → **my_vectordb/** → **Response**

### Configuration Management
- **setup.py, requirements.txt** → Package installation and dependencies
- **MANIFEST.in** → Distribution rules
- **setup.cfg** → Build configuration

This mindmap provides a comprehensive view of how all LocalWise components interact and depend on each other.