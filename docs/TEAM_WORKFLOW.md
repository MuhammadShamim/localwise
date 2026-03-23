# 🧠 LocalWise v1.0.0 - Team Workflow

## Simple 2-Step Process

LocalWise uses a clean **2-step workflow** that allows teams to work efficiently.

---

## 🎯 **Process Overview**

| Step | Description | Dependencies | Who |
|------|-------------|--------------|-----|
| **Step 1** | Extract text from documents | None | Document Team |
| **Step 2** | Create AI embeddings | Ollama + Step 1 | AI Team |
| **Launch** | Start the app | Steps 1 & 2 | Users |

---

## 📝 **Step 1: Document Processing**

**Team**: Document Management  
**Requirements**: None (no AI needed)

```bash
# Extract text from all documents
python ingest.py --step1
```

**What happens:**
- ✅ Scans `docs/` folder recursively
- ✅ Supports PDF, CSV, JSON, YAML, XML
- ✅ Extracts and cleans text content
- ✅ Splits into optimized chunks
- ✅ Saves to `db/processed_chunks.json`

**Output**: Ready-to-embed text chunks

---

## 🧠 **Step 2: AI Embeddings**

**Team**: AI/Infrastructure  
**Requirements**: Ollama running + Step 1 complete

```bash
# Create vector embeddings
python ingest.py --step2
```

**Prerequisites:**
```bash
# Start Ollama service
ollama serve

# Download AI model
ollama pull llama3.2:latest
```

**What happens:**
- ✅ Loads processed chunks from Step 1
- ✅ Creates vector embeddings via Ollama
- ✅ Builds ChromaDB database
- ✅ Validates database integrity

**Output**: Searchable vector database

---

## 🚀 **Launch Application**

**Team**: End Users  
**Requirements**: Steps 1 & 2 complete + Ollama running

```bash
# Start the web interface
streamlit run app.py
```

**Access**: http://localhost:8501

---

## 🔄 **Alternative Approaches**

### Traditional (All-in-One)
```bash
# Combine Steps 1 + 2
python ingest.py

# Launch app
streamlit run app.py
```

### Legacy Compatibility
```bash
# Same as Step 1 (backward compatible)
python ingest.py --data-only
```

---

## 💡 **Team Benefits**

- ✅ **Parallel Work**: Document team starts immediately
- ✅ **No Waiting**: No dependency on AI infrastructure setup
- ✅ **Clear Handoffs**: Each step produces validated output
- ✅ **Easy Debugging**: Isolate issues to specific stages
- ✅ **Fast Iteration**: Only rerun necessary steps

---

## 🚨 **Troubleshooting**

### Step 1 Issues
- **No files found**: Add supported docs to `docs/`
- **Files skipped**: Check `config.py` for size limits

### Step 2 Issues
- **Ollama failed**: Run `ollama serve` first
- **Model missing**: Run `ollama pull llama3.2:latest`
- **No processed data**: Complete Step 1 first

### Launch Issues
- **Database not found**: Complete Steps 1 & 2
- **App won't start**: Check Ollama is running

---

## 📊 **Status Checking**

```bash
python ingest.py --step1   # Shows next step when complete
python ingest.py --step2   # Shows launch command when ready
```

All steps provide clear guidance for what to do next!

---

**Simple. Efficient. Reliable.** 🚀