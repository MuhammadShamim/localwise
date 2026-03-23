# LocalWise v1.0.0 - Test Execution Guide

## 🚀 Quick Start Testing

### Prerequisites Checklist

Before running tests, ensure you have:

- [ ] **Python 3.8+** installed and available in PATH
- [ ] **LocalWise dependencies** installed (`pip install -r requirements.txt`)
- [ ] **Test dependencies** installed (`pip install pytest pytest-cov pytest-html pytest-benchmark`)
- [ ] **Ollama service** running locally (for integration tests)
- [ ] **ChromaDB dependencies** available
- [ ] **Sufficient disk space** (10GB+ recommended for full test suite)
- [ ] **Administrator/sudo privileges** (for some system tests)

### Quick Test Commands

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-html pytest-benchmark

# Run all tests with coverage
python run_tests.py --all --verbose

# Run specific test suites
python run_tests.py --unit                    # Unit tests only
python run_tests.py --integration             # Integration tests only
python run_tests.py --performance             # Performance tests only

# Generate HTML reports
python run_tests.py --all --html

# Check current coverage
python run_tests.py --coverage
```

## 📋 Test Suite Structure

### Test Organization

```
tests/
├── conftest.py                    # Pytest configuration and fixtures
├── unit/                         # Unit tests (fast, isolated)
│   ├── test_file_processors.py   # File processing logic
│   └── test_data_management.py   # Data management components  
├── integration/                  # Integration tests (slower, end-to-end)
│   └── test_end_to_end.py        # Complete workflow tests
├── performance/                  # Performance and benchmark tests
│   └── test_performance.py       # Speed and memory tests
└── fixtures/                     # Test data and utilities
    ├── README.md                  # Fixture documentation
    └── sample_documents/          # Sample files for testing
        ├── README.md
        ├── config.json
        ├── employees.csv
        ├── app_config.yaml
        ├── sample_code.py
        ├── library.xml
        └── sample_text.txt
```

### Test Categories

| Category | Purpose | Execution Time | Coverage |
|----------|---------|---------------|----------|
| **Unit Tests** | Component isolation testing | ~30 seconds | Core logic |
| **Integration Tests** | End-to-end workflow testing | ~2-5 minutes | Complete flows |
| **Performance Tests** | Speed and memory validation | ~5-10 minutes | System limits |
| **Benchmark Tests** | Performance tracking | ~2-3 minutes | Critical paths |

## 🎯 Detailed Test Execution

### 1. Unit Test Execution

**Purpose**: Validate individual components work correctly in isolation

```bash
# Run unit tests only
python run_tests.py --unit --verbose

# Run specific unit test file
python -m pytest tests/unit/test_file_processors.py -v

# Run with coverage details
python -m pytest tests/unit/ --cov=localwise --cov-report=term-missing -v
```

**Expected Results**:
- ✅ All file processors handle their target formats correctly
- ✅ Data management components manage state properly
- ✅ Error cases are handled gracefully
- ✅ Mocked dependencies behave as expected

**Typical Output**:
```
tests/unit/test_file_processors.py::TestPDFProcessor::test_process_pdf PASSED
tests/unit/test_file_processors.py::TestCSVProcessor::test_process_csv PASSED
tests/unit/test_data_management.py::TestDataManager::test_ingest_files PASSED
...
========================= X passed in Y.YYs =========================
```

### 2. Integration Test Execution

**Purpose**: Verify complete workflows function correctly when components interact

```bash
# Run integration tests only
python run_tests.py --integration --verbose

# Run specific integration test
python -m pytest tests/integration/test_end_to_end.py::test_complete_workflow -v

# Run with service validation
python -m pytest tests/integration/ -v --tb=short
```

**Expected Results**:
- ✅ Documents processed completely from file to database
- ✅ Query engine returns accurate responses
- ✅ All components integrate smoothly
- ✅ Error propagation works correctly

**Typical Output**:
```
tests/integration/test_end_to_end.py::test_complete_workflow PASSED
tests/integration/test_end_to_end.py::test_query_functionality PASSED
tests/integration/test_end_to_end.py::test_incremental_updates PASSED
...
========================= X passed in Y.YYs =========================
```

### 3. Performance Test Execution

**Purpose**: Validate system performance meets requirements

```bash
# Run performance tests only
python run_tests.py --performance

# Run with detailed performance metrics
python -m pytest tests/performance/ -v --tb=short

# Run benchmarks only (if pytest-benchmark installed)
python -m pytest tests/performance/ -k benchmark -v
```

**Expected Results**:
- ✅ File processing within time limits
- ✅ Memory usage within acceptable bounds
- ✅ Query response times meet targets
- ✅ System stable under load

**Performance Targets**:
```
📊 Performance Targets:
   Small files (< 1MB): < 2 seconds
   Large files (< 10MB): < 30 seconds  
   Query responses: < 3 seconds
   Memory usage: < 500MB
   Batch processing: < 5 minutes (100 files)
```

### 4. Complete Test Suite Execution

**Purpose**: Run comprehensive testing with all validations

```bash
# Complete test suite with reports
python run_tests.py --all --html --verbose

# Alternative comprehensive run
python -m pytest tests/ --cov=localwise --cov-report=html --html=test_results/report.html
```

**Expected Artifacts**:
- 📄 **HTML Test Report**: `test_results/html/test_report.html`
- 📊 **Coverage Report**: `test_results/html/coverage/index.html`
- 📋 **JUnit XML**: `test_results/unit_tests.xml`, `test_results/integration_tests.xml`
- 📈 **Performance Data**: `test_results/performance.json`
- 📝 **Execution Summary**: `test_results/test_execution_results.json`

## 🛠️ Troubleshooting Guide

### Common Issues and Solutions

#### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'localwise'`

**Solution**:
```bash
# Ensure LocalWise is installed in development mode
pip install -e .

# Or run tests from the correct directory
cd /path/to/LocalWise
python run_tests.py --all
```

#### 2. Service Dependencies

**Problem**: `ConnectionError: Could not connect to Ollama service`

**Solutions**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Start Ollama if not running
ollama serve

# Run tests without integration tests if Ollama unavailable
python run_tests.py --unit --performance
```

#### 3. Permission Errors

**Problem**: `PermissionError: [Errno 13] Permission denied`

**Solutions**:
```bash
# Run with appropriate permissions (Windows)
runas /user:Administrator "python run_tests.py --all"

# Run with sudo (Linux/macOS)  
sudo python run_tests.py --all

# Or use a virtual environment with user permissions
python -m venv test_env
source test_env/bin/activate  # Linux/macOS
test_env\Scripts\activate     # Windows
pip install -e .
python run_tests.py --all
```

#### 4. Memory Issues

**Problem**: Tests failing due to insufficient memory

**Solutions**:
```bash
# Run tests individually to reduce memory usage
python run_tests.py --unit
python run_tests.py --integration
python run_tests.py --performance

# Skip memory-intensive performance tests
python -m pytest tests/ -k "not stress" -v

# Monitor memory usage during tests
python -c "import psutil; print(f'Available memory: {psutil.virtual_memory().available / 1024**3:.1f}GB')"
```

#### 5. Test Data Issues

**Problem**: Missing or corrupted test fixtures

**Solution**:
```bash
# Regenerate test fixtures
cd tests/fixtures/sample_documents
python generate_samples.py

# Verify fixtures exist
ls -la tests/fixtures/sample_documents/

# Check fixture content
head tests/fixtures/sample_documents/README.md
```

#### 6. Slow Test Execution

**Problem**: Tests running slower than expected

**Solutions**:
```bash
# Run tests in parallel (if using pytest-xdist)
pip install pytest-xdist
python -m pytest tests/ -n auto

# Skip slow performance tests during development
python -m pytest tests/ -k "not performance" -v

# Use fast test subset during development
python -m pytest tests/unit/ -x -v  # Stop on first failure
```

### Test Environment Validation

Use this checklist to validate your test environment:

```bash
# 1. Check Python version
python --version  # Should be 3.8+

# 2. Validate LocalWise installation
python -c "import localwise; print('LocalWise imported successfully')"

# 3. Check test dependencies
python -c "import pytest, coverage; print('Test dependencies available')"

# 4. Verify Ollama connection (if needed)
curl -s http://localhost:11434/api/version || echo "Ollama not available"

# 5. Check available disk space
df -h . || dir  # Should have 10GB+ available

# 6. Validate test data
ls tests/fixtures/sample_documents/ | wc -l  # Should show 7+ files

# 7. Test basic functionality
python -c "from localwise.core.file_processors import get_processor_for_file; print('Core modules working')"
```

## 📊 Test Metrics and Quality Gates

### Coverage Requirements

| Component | Minimum Coverage | Target Coverage |
|-----------|------------------|-----------------|
| **Core Modules** | 80% | 90% |
| **File Processors** | 85% | 95% |
| **Data Management** | 80% | 90% |
| **UI Components** | 70% | 80% |
| **Overall Project** | 80% | 85% |

### Performance Benchmarks

| Operation | Maximum Time | Target Time |
|-----------|--------------|-------------|
| Small file processing | 2.0 seconds | 1.0 seconds |
| Large file processing | 30.0 seconds | 15.0 seconds |
| Query response | 3.0 seconds | 1.5 seconds |
| Batch processing | 5.0 minutes | 3.0 minutes |

### Quality Gates

Before release, all of the following must pass:

- [ ] **100%** of critical test cases pass
- [ ] **≥95%** of high priority test cases pass  
- [ ] **≥80%** code coverage achieved
- [ ] **0** critical or high severity bugs
- [ ] **All** performance targets met
- [ ] **All** security validations pass
- [ ] **Complete** documentation validation

## 📈 Continuous Testing

### Pre-commit Testing

Add this to your development workflow:

```bash
# Quick validation before commits
python -m pytest tests/unit/ -x --tb=short

# Full validation before pushes  
python run_tests.py --all
```

### Automated Testing Scripts

Create automated testing scripts for different scenarios:

**Daily Development Testing**:
```bash
#!/bin/bash
# dev_test.sh
echo "Running daily development tests..."
python run_tests.py --unit --verbose
python run_tests.py --integration
echo "Daily tests completed"
```

**Release Testing**:
```bash
#!/bin/bash
# release_test.sh
echo "Running comprehensive release tests..."
python run_tests.py --all --html --verbose
echo "Release tests completed - check test_results/ for reports"
```

**Performance Monitoring**:
```bash
#!/bin/bash
# perf_test.sh
echo "Running performance validation..."
python run_tests.py --performance
echo "Performance validation completed"
```

## 🎯 Test Success Criteria

### Minimum Success Requirements

For a test run to be considered successful:

1. **Zero test failures** in critical test categories
2. **≥95% pass rate** for all test categories combined
3. **Coverage threshold met** (≥80% overall)
4. **Performance targets achieved** for all benchmarks
5. **No memory leaks detected** during stress tests
6. **Clean test environment** (no side effects between tests)

### Quality Validation

Each test execution should produce:

- **Detailed pass/fail report** for all test cases
- **Coverage analysis** with line-by-line breakdown
- **Performance metrics** comparing against targets
- **Resource usage statistics** (memory, CPU, disk)
- **Error analysis** for any failures or warnings

---

**This guide ensures comprehensive testing of LocalWise v1.0.0 across all critical functionality and performance requirements.** 🧠✨