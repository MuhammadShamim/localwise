# 🧠 LocalWise v1.1.0

**Your Professional AI Knowledge Assistant**

A sophisticated yet simple AI application that transforms your documents into an intelligent, searchable knowledge base. Ask questions in natural language and get instant answers with source citations from your private document collection.

**🔒 100% Private** • **🚫 No API Keys** • **💻 Runs Entirely Offline** • **⚡ Professional Architecture** • **🛠️ Enterprise Ready**

---

## 🌟 What is LocalWise?

LocalWise is a professional-grade AI knowledge assistant with enterprise architecture that turns any document collection into an intelligent, searchable knowledge base. Unlike cloud-based solutions, LocalWise runs entirely on your machine, ensuring complete privacy and data security.

**🏗️ Professional Package Architecture:**
- **localwise.core**: Core processing engines (file processors, embeddings, query engine)
- **localwise.data**: Data management layer (data manager, file manifest, change detection)
- **localwise.ui**: Professional user interface components
- **localwise.cli**: Comprehensive command-line interface

**📋 40+ Supported File Types:**
- 📄 **Documents**: PDF, TXT, RTF, DOC, DOCX, ODT, EPUB
- 📊 **Data**: CSV, TSV, JSON, JSONL, YAML, XML, XSD, XSL/XSLT, WSDL, PLIST, DataWeave (DWL, DW)
- 🔧 **Code**: Python, JavaScript, TypeScript, Java, C/C++, C#, Go, PHP, Ruby, Rust, Kotlin, Swift, Scala, Perl, SQL, Shell scripts (bash, sh, zsh), PowerShell, R, MATLAB, Lua
- 📝 **Markup**: HTML, CSS, SCSS, Sass, Less, Markdown, reStructuredText, LaTeX
- 🏢 **Office**: XLSX, PPTX, ODP, ODS
- ⚙️ **Config**: INI, CFG, CONF, LOG

**Perfect for:**
- 📚 Research institutions and academic workflows
- 🏢 Enterprise knowledge management systems
- 🔧 Technical documentation and API references
- 📊 Business intelligence and data analysis
- 🏛️ Legal document review and compliance
- 🩺 Medical research and clinical documentation

---

## 🚀 Quick Start (3 Minutes)

### 1. **Environment Setup**
```bash
# Clone LocalWise
cd LocalWise

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# OR install as package
pip install -e .
```

### 2. **AI Model Setup**
```bash
# Install and start Ollama
ollama serve

# Download the AI model
ollama pull llama3.2:latest
```

### 3. **Add Your Documents**
```bash
# Create document structure
documents/
├── research_papers/
│   ├── ai_paper_2023.pdf
│   ├── methodology.docx
│   └── data_analysis.xlsx
├── business_reports/
│   ├── quarterly_review.pdf
│   ├── financial_data.csv
│   └── market_analysis.json
├── technical_docs/
│   ├── api_documentation.md
│   ├── system_architecture.yaml
│   └── configuration.xml
└── code_documentation/
    ├── main.py
    ├── database_schema.sql
    └── deployment_scripts.sh
```

### 4. **Process Documents**

#### Option A: Full Pipeline (All Three Steps)
```bash
# Step 1: Extract text from documents and split into chunks
python ingest.py --step1

# Step 2: Generate vector embeddings and store in ChromaDB
python ingest.py --step2

# Step 3: Launch the Streamlit web interface
python ingest.py --step3
```

#### Option B: Run Steps 1 & 2 Together (No UI Launch)
```bash
python ingest.py --step1 && python ingest.py --step2
```

#### Option C: Professional CLI Interface
```bash
# Process with comprehensive CLI
python -m localwise.cli process -d documents/ --incremental

# Check system status
python -m localwise.cli status

# List processed files
python -m localwise.cli list-files
```

#### Option D: Incremental Processing (Recommended for Large Collections)
```bash
# Step 1: Extract text — only new/modified files
python ingest.py --step1 --incremental

# Step 2: Create embeddings for new/modified files only
python ingest.py --step2 --incremental

# Step 3: Launch interface
python ingest.py --step3
```

### 5. **Launch Interface**

#### Via ingest.py (Step 3)
```bash
python ingest.py --step3
# Open: http://localhost:8501
```

#### Directly via Streamlit
```bash
streamlit run app.py
# Open: http://localhost:8501
```

#### CLI Interface
```bash
python -m localwise.cli serve
```

**🎉 Start asking questions about your documents!**

---

## 🏗️ Professional Architecture

### Package Structure
```
LocalWise/
│
├── 🏗️ localwise/                    ← Main package
│   ├── 🔧 core/                     ← Core processing engines
│   │   ├── file_processors.py       ← 40+ file type processors
│   │   ├── embedding_service.py     ← AI embedding generation
│   │   └── query_engine.py          ← RAG query processing  
│   │
│   ├── 💾 data/                     ← Data management layer
│   │   ├── data_manager.py          ← Atomic data operations
│   │   ├── file_manifest.py         ← Change detection
│   │   └── change_detector.py       ← Incremental processing
│   │
│   ├── 🖥️ ui/                       ← User interface
│   │   └── ui_components.py         ← Streamlit components
│   │
│   ├── 💻 cli/                      ← Command-line interface
│   │   └── cli_interface.py         ← Full CLI with examples
│   │
│   ├── ⚙️ config.py                 ← Configuration and validation
│   └── 📋 __init__.py               ← Package exports
│
├── 📂 documents/                    ← Your documents go here
├── 🗄️ db/                          ← Processed data (auto-created)
├── 🎯 my_vectordb/                  ← Vector embeddings (auto-created)
│
├── 🖥️ app.py                       ← Web interface entry point
├── 🔄 ingest.py                    ← Processing entry point
├── 📦 setup.py                     ← Package installation
├── 📋 requirements.txt             ← Dependencies
├── 📰 CHANGELOG.md                 ← Release notes
└── 📖 README.md                    ← This file
```

### Core Components

#### 🔧 File Processing Engine
- **FileProcessorRegistry**: Extensible 40+ file type support
- **Specialized Processors**: Optimized for each file format
- **Health Monitoring**: Real-time processing status and error handling
- **Batch Processing**: Efficient handling of large document collections

#### 🧠 AI & Embedding Service
- **EmbeddingService**: GPU-accelerated vector generation
- **Ollama Integration**: Local AI with health monitoring and fallback
- **Batch Processing**: Progress tracking for large document sets
- **Cache Management**: Intelligent caching for performance optimization

#### 🔍 Query Engine
- **RAG Pipeline**: Advanced Retrieval-Augmented Generation
- **Source Attribution**: Detailed citations with confidence scores
- **Context Optimization**: Smart chunk retrieval and ranking
- **Validation System**: Input sanitization and response verification

#### 💾 Data Management
- **DataManager**: Atomic operations with integrity validation
- **FileManifest**: Hash-based change detection for incremental updates
- **ChangeDetector**: Intelligent file monitoring with optimization
- **Statistics Tracking**: Comprehensive processing metrics

---

## 🛠️ Professional Usage

### Command Line Interface
```bash
# Full help system
python -m localwise.cli --help

# Process documents with options
python -m localwise.cli process \
  --directory documents/ \
  --recursive \
  --incremental \
  --max-file-size 100MB \
  --batch-size 50

# System validation
python -m localwise.cli validate

# Performance monitoring
python -m localwise.cli stats

# Health checks
python -m localwise.cli health-check
```

### Configuration Management
```python
# localwise/config.py
DOCS_FOLDER = "docs"
DB_FOLDER = "db"
OLLAMA_MODEL = "llama3.2:latest"
OLLAMA_BASE_URL = "http://localhost:11434"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
MAX_FILE_SIZE_MB = 50
CHUNK_BATCH_SIZE = 100
REQUEST_TIMEOUT = 30
```

### API Usage
```python
from localwise.core.query_engine import QueryEngine
from localwise.core.embedding_service import EmbeddingService
from localwise.data.data_manager import DataManager

# Initialize components
query_engine = QueryEngine()
embedding_service = EmbeddingService()
data_manager = DataManager()

# Query documents
response = query_engine.query_documents(
    "What are the key findings in the research papers?",
    vectorstore
)

# Process new documents
embeddings = embedding_service.create_embeddings_from_texts(texts)
```

---

## 🔧 Advanced Features

### Incremental Processing
```bash
# Only process new/modified files (recommended for large collections)
python ingest.py --step1 --incremental
python ingest.py --step2 --incremental
python ingest.py --step3

# Force refresh all files
python ingest.py --step1 --force-refresh
python ingest.py --step2 --force-refresh
```

### Batch Processing
```bash
# Process large document collections efficiently
python -m localwise.cli process --batch-size 100 --parallel
```

### Health Monitoring
```bash
# System diagnostics
python -m localwise.cli health-check

# Performance metrics
python -m localwise.cli stats --detailed
```

### Professional Integration
```python
# Package-level imports
from localwise import QueryEngine, EmbeddingService, DataManager
from localwise import config

# Version information
import localwise
print(localwise.get_version_info())

# Installation check
status = localwise.check_installation()
```

---

## 🎯 File Type Support Matrix

| Category | Formats | Processor | Features |
|----------|---------|-----------|----------|
| **Documents** | PDF, DOCX, ODT, RTF, EPUB | Advanced text extraction | Metadata, structure preservation |
| **Data** | CSV, TSV, JSON, JSONL, YAML | Smart parsing | Schema detection, nested structures |
| **XML Family** | XML, XSD, XSL, XSLT, WSDL, PLIST | Recursive XML parser | Attribute preservation, namespace detection |
| **DataWeave** | DWL, DW | DataWeave parser | Header directives, output/input type extraction |
| **Code** | 25+ languages | Syntax-aware | Comment extraction, structure analysis |
| **Office** | XLSX, PPTX, ODP, ODS | Native support | Multi-sheet, presentation content |
| **Markup** | HTML, CSS, MD, LaTeX | Structured parsing | Link preservation, formatting |
| **Config** | INI, CFG, CONF, LOG | Key-value extraction | Hierarchical structures |

**✨ Extensible Architecture**: Easy to add custom processors for specialized formats

---

## 🚨 Professional Troubleshooting

### System Validation
```bash
# Complete system check
python -m localwise.cli validate

# Check specific components
python -c "from localwise import config; print(config.validate_ollama_connection())"
python -c "from localwise import config; print(config.validate_database_exists())"
```

### Common Issues

#### Ollama Service Issues
```bash
# Start Ollama service
ollama serve

# Verify model availability
ollama list

# Download required model
ollama pull llama3.2:latest

# Test connection
curl http://localhost:11434/api/tags
```

#### Performance Optimization
```bash
# Use incremental processing for large collections
python ingest.py --step1 --incremental

# Adjust batch sizes in config.py
CHUNK_BATCH_SIZE = 50  # Reduce for memory constraints

# Monitor processing
tail -f localwise.log
```

#### Database Issues
```bash
# Reset and rebuild database
rm -rf db/ my_vectordb/
python ingest.py --step1 && python ingest.py --step2

# Check database integrity
python -m localwise.cli validate --database
```

### Logging and Diagnostics
```python
from localwise import config

# Setup detailed logging
logger = config.setup_logging()
logger.setLevel(logging.DEBUG)

# Check system status
status = config.validate_ollama_connection()
db_status = config.validate_database_exists()
```

---

## 🎉 What's New in v1.1.0

### 🗂️ **Extended XML Support**
- **XMLProcessor** now handles the full XML family: `.xsd`, `.xsl`, `.xslt`, `.wsdl`, `.plist` in addition to `.xml`
- Recursive parser preserves element hierarchy, attributes, and namespace information across all XML-based formats

### 🔄 **DataWeave Support**
- New **DataWeaveProcessor** for MuleSoft DataWeave scripts (`.dwl`, `.dw`)
- Splits and labels header directives and transformation body for better searchability
- Extracts `output`, `input`, and `var` directive metadata into queryable fields

---

## ✨ What Was New in v1.0.0

### 🏗️ **Professional Architecture**
- **Modular Package Structure**: Clean separation with localwise.core, localwise.data, localwise.ui, localwise.cli
- **Enterprise Documentation**: Comprehensive docstrings, type hints, and inline documentation
- **Error Handling**: Robust exception handling throughout the codebase
- **Health Monitoring**: System validation and performance tracking

### ✨ **Enhanced Features**
- **40+ File Types**: Extended support including Office documents, code files, and configuration formats
- **CLI Interface**: Professional command-line tools with comprehensive help system
- **Incremental Processing**: Smart change detection for large document collections
- **Batch Processing**: Optimized handling for enterprise-scale document processing

### 🚀 **Performance Improvements**
- **Smart Caching**: Intelligent caching for better performance
- **Progress Tracking**: Real-time feedback during long operations
- **Memory Optimization**: Efficient handling of large document collections
- **Parallel Processing**: Multi-threaded operations where beneficial

### 🔧 **Developer Experience**
- **Package Installation**: Pip installable with entry points
- **Type Safety**: Full type hints for better IDE support
- **Examples**: CLI help system with detailed usage examples
- **Testing**: Comprehensive validation and health checking

---

## 📋 Installation Options

### Development Installation
```bash
git clone https://github.com/localwise/localwise.git
cd localwise
pip install -e .
```

### Package Installation
```bash
pip install localwise
```

### Requirements
- **Python**: 3.8+
- **Memory**: 4GB RAM minimum, 8GB+ recommended
- **Storage**: 2GB free space for models and data
- **OS**: Windows, macOS, Linux

---

## 📝 License & Credits

**License**: MIT
**Author**: LocalWise Development Team
**Version**: 1.1.0
**Release Date**: March 26, 2026

**Technology Stack**:
- **Core**: Python 3.8+ with comprehensive type hints
- **AI**: Ollama with Llama 3.2 for local processing
- **Vector DB**: ChromaDB for high-performance similarity search
- **UI**: Streamlit with professional component library
- **Framework**: LangChain for advanced RAG implementation
- **Processing**: 15+ specialized libraries for file format support

**Privacy Promise**: No telemetry, no tracking, no cloud dependencies. Your data remains private and secure on your machine.

---

## 🤝 Support & Community

### Getting Help
1. **Documentation**: Read this comprehensive guide
2. **System Validation**: Run `python -m localwise.cli validate`
3. **Logs**: Check `localwise.log` for detailed error information
4. **CLI Help**: Use `python -m localwise.cli --help` for command examples

### Professional Support
- **Enterprise**: Contact for enterprise deployment and customization
- **Training**: Available for team onboarding and best practices
- **Integration**: Custom development for specialized use cases

**Transform your documents into intelligent knowledge with LocalWise v1.1.0!** 🧠✨