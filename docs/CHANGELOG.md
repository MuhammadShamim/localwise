# LocalWise Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-03-26

### ✨ **Extended File Format Support**

#### 🗂️ **XML Family Support**
- **Extended XMLProcessor** to handle XML-adjacent formats in addition to `.xml`:
  - `.xsd` — XML Schema Definition files
  - `.xsl` / `.xslt` — XSLT transformation stylesheets
  - `.wsdl` — Web Services Description Language descriptors
  - `.plist` — Apple Property List files
- All new extensions reuse the existing recursive XML parser with attribute and namespace preservation

#### 🔄 **DataWeave Support (New)**
- **New `DataWeaveProcessor`** for MuleSoft DataWeave transformation scripts (`.dwl`, `.dw`)
- Parses the DataWeave header/body structure split on the `---` separator
- Extracts and surfaces structured metadata:
  - `output_type` — declared output MIME type (e.g. `application/json`)
  - `input_types` — list of declared input variable types
  - `var_declarations` — top-level variable declarations
- Multi-encoding support: UTF-8, UTF-8-sig, Latin-1, CP1252
- Registered in `FileProcessorRegistry` under the `dataweave` type

---

## [1.0.0] - 2024-12-21

### 🎉 **Initial Release - Professional Package Architecture**

#### ✨ **New Features**
- **🏗️ Professional Package Structure**: Organized modular architecture with localwise/ package
- **🧠 Smart Document Processing**: 40+ file types with extensible processor registry
- **🔒 100% Private**: No API keys, runs entirely offline with local Ollama integration
- **⚡ Fast Setup**: 3-minute installation process with comprehensive validation
- **🖥️ Modern Interface**: Professional Streamlit UI with responsive components
- **📁 Recursive Scanning**: Intelligent file discovery with change detection
- **🤖 Local AI**: Powered by Ollama with health monitoring and fallback support
- **💬 Natural Language**: Advanced RAG pipeline with source attribution
- **📚 Source Citations**: Every answer includes detailed source references
- **🛠️ CLI Interface**: Comprehensive command-line tools for power users

#### 🏗️ **Package Architecture**
- **localwise/**: Main package with clean separation of concerns
  - **core/**: Core processing engines (file_processors, embedding_service, query_engine)
  - **data/**: Data management layer (data_manager, file_manifest, change_detector)
  - **ui/**: User interface components (streamlit components with consistent styling)
  - **cli/**: Command-line interface (comprehensive CLI with help system)

#### 🛠️ **Core Components**
- **FileProcessorRegistry**: Extensible 40+ file type support with plugin architecture
- **EmbeddingService**: AI-powered vector embeddings with batch processing
- **QueryEngine**: Advanced RAG pipeline with LLM integration and validation
- **DataManager**: Atomic data operations with integrity validation
- **FileManifest**: Hash-based change detection for incremental processing
- **LocalWiseUI**: Professional UI components with error handling
- **LocalWiseCLI**: Full-featured command-line interface with examples

#### 📋 **Supported File Types**
- **Text**: .txt, .md, .rtf, .csv, .tsv
- **Documents**: .pdf, .docx, .odt, .epub
- **Code**: .py, .js, .html, .css, .json, .xml, .yaml, .sql, .sh
- **Office**: .xlsx, .pptx, .odp, .ods
- **Data**: .jsonl, .log, .ini, .cfg, .conf
- **And 25+ more formats with extensible processor registry**

#### 🚀 **Quick Start Guide**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup Ollama
ollama serve
ollama pull llama3.2:latest

# 3. Add documents to docs/ folder

# 4. Process documents (CLI or Python)
python -m localwise.cli process -d docs/
# OR
python ingest.py --step1 && python ingest.py --step2

# 5. Launch interface
streamlit run app.py
# OR
python -m localwise.cli serve
```

#### 🔧 **Technical Stack**
- **Python 3.8+**: Core language with type hints throughout
- **LangChain**: Advanced RAG framework with custom chains
- **Ollama**: Local AI models with health monitoring
- **ChromaDB**: High-performance vector database
- **Streamlit**: Modern web interface with component library
- **Comprehensive Dependencies**: 15+ specialized libraries for file processing

#### 🎯 **Design Principles**
- **Professional Architecture**: Clean package structure with proper separation
- **Comprehensive Documentation**: Every module has detailed docstrings and type hints
- **Error Handling**: Robust exception handling throughout the codebase
- **Privacy First**: No cloud dependencies, tracking, or data collection
- **User Experience**: Both GUI and CLI interfaces for different workflows
- **Extensibility**: Plugin architecture for easy customization
- **Reliability**: Comprehensive validation and health checking

#### 📚 **Documentation**
- **Code Documentation**: Comprehensive docstrings and inline comments
- **Type Safety**: Full type hints for better IDE support
- **Examples**: CLI help system with detailed usage examples
- **Architecture**: Clean modular design with clear dependency flow

#### 🧪 **Quality Assurance**
- **Error Handling**: Comprehensive exception handling and user feedback
- **Validation**: Input validation and system health checks
- **Health Monitoring**: Ollama service monitoring and automatic recovery
- **Progress Tracking**: Real-time feedback during long operations

---

**🧠 LocalWise v1.0.0 - Professional AI Knowledge Assistant with Enterprise-Grade Architecture!** ✨