"""
Performance tests for LocalWise v1.0.0

This module contains performance and benchmark tests to ensure LocalWise
meets its performance requirements and maintains acceptable response times
under various load conditions.

Test Categories:
- File Processing Performance: Individual and batch file processing times
- Query Performance: Response times for different query complexities  
- Memory Usage: Memory consumption under normal and stress conditions
- Concurrent Operations: Performance under multiple simultaneous operations
- Large File Handling: Performance with large documents
"""

import pytest
import time
import psutil
import os
import tempfile
from pathlib import Path
import concurrent.futures
from typing import List, Dict, Any
import json

# Import LocalWise components for testing
from localwise.core.file_processors import get_processor_for_file
from localwise.core.embeddings import EmbeddingService
from localwise.core.query_engine import QueryEngine
from localwise.data.data_manager import DataManager
from localwise.data.file_manifest import FileManifest

# Performance test configuration
PERFORMANCE_CONFIG = {
    "max_processing_time_small": 2.0,    # seconds for files < 1MB
    "max_processing_time_large": 30.0,   # seconds for files < 10MB
    "max_query_time": 3.0,               # seconds for query responses
    "max_memory_usage": 500 * 1024 * 1024,  # 500MB
    "batch_size_limit": 100,             # files in batch
    "concurrent_users": 5,               # simultaneous operations
    "stress_iterations": 1000,           # stress test iterations
}

class PerformanceMonitor:
    """Monitor system performance during tests."""
    
    def __init__(self):
        """Initialize performance monitoring."""
        self.process = psutil.Process()
        self.start_memory = 0
        self.start_time = 0
    
    def start_monitoring(self):
        """Start performance monitoring."""
        self.start_memory = self.process.memory_info().rss
        self.start_time = time.time()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        current_memory = self.process.memory_info().rss
        elapsed_time = time.time() - self.start_time
        
        return {
            "elapsed_time": elapsed_time,
            "start_memory_mb": self.start_memory / (1024 * 1024),
            "current_memory_mb": current_memory / (1024 * 1024), 
            "memory_delta_mb": (current_memory - self.start_memory) / (1024 * 1024),
            "cpu_percent": self.process.cpu_percent(),
            "threads": self.process.num_threads()
        }

@pytest.fixture
def performance_monitor():
    """Provide performance monitoring fixture."""
    return PerformanceMonitor()

@pytest.fixture  
def temp_workspace():
    """Create temporary workspace for performance tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace_path = Path(temp_dir)
        # Create subdirectories
        (workspace_path / "documents").mkdir()
        (workspace_path / "db").mkdir()
        yield workspace_path

@pytest.fixture
def sample_files(temp_workspace):
    """Create sample files of various sizes for performance testing."""
    documents_dir = temp_workspace / "documents"
    files = {}
    
    # Small text file (< 1KB)
    small_file = documents_dir / "small.txt"
    small_file.write_text("This is a small test document. " * 10)
    files["small"] = small_file
    
    # Medium text file (~ 100KB)
    medium_file = documents_dir / "medium.txt"
    medium_content = "This is a medium test document with more content. " * 1000
    medium_file.write_text(medium_content)
    files["medium"] = medium_file
    
    # Large text file (~ 1MB)
    large_file = documents_dir / "large.txt"
    large_content = "This is a large test document with substantial content for performance testing. " * 10000
    large_file.write_text(large_content)
    files["large"] = large_file
    
    # JSON file
    json_file = documents_dir / "data.json"
    json_data = {
        "users": [f"user_{i}" for i in range(1000)],
        "configuration": {"setting_" + str(i): f"value_{i}" for i in range(100)},
        "metadata": {"description": "Performance test JSON data"}
    }
    json_file.write_text(json.dumps(json_data, indent=2))
    files["json"] = json_file
    
    # CSV file
    csv_file = documents_dir / "data.csv"
    csv_content = "id,name,email,department,salary\n"
    for i in range(1000):
        csv_content += f"{i},User {i},user{i}@example.com,Department {i % 5},{30000 + i * 10}\n"
    csv_file.write_text(csv_content)
    files["csv"] = csv_file
    
    return files

@pytest.fixture
def data_manager(temp_workspace):
    """Provide configured DataManager for performance tests."""
    return DataManager(workspace_path=temp_workspace)

class TestFileProcessingPerformance:
    """Test file processing performance."""
    
    def test_small_file_processing_time(self, sample_files, performance_monitor):
        """Test small file processing meets time requirements."""
        performance_monitor.start_monitoring()
        
        # Process small file
        processor = get_processor_for_file(sample_files["small"])
        result = processor.process()
        
        metrics = performance_monitor.get_metrics()
        
        # Assertions
        assert metrics["elapsed_time"] < PERFORMANCE_CONFIG["max_processing_time_small"], \
               f"Small file processing took {metrics['elapsed_time']:.2f}s, expected < {PERFORMANCE_CONFIG['max_processing_time_small']}s"
        
        assert len(result.chunks) > 0, "Should produce text chunks"
        
        # Log performance metrics
        print(f"\n📊 Small File Performance:")
        print(f"   Processing Time: {metrics['elapsed_time']:.3f}s")
        print(f"   Memory Used: {metrics['memory_delta_mb']:.2f}MB")
        print(f"   Chunks Generated: {len(result.chunks)}")
    
    def test_medium_file_processing_time(self, sample_files, performance_monitor):
        """Test medium file processing performance."""
        performance_monitor.start_monitoring()
        
        # Process medium file
        processor = get_processor_for_file(sample_files["medium"])
        result = processor.process()
        
        metrics = performance_monitor.get_metrics()
        
        # Assertions
        assert metrics["elapsed_time"] < PERFORMANCE_CONFIG["max_processing_time_small"], \
               f"Medium file processing took {metrics['elapsed_time']:.2f}s, expected < {PERFORMANCE_CONFIG['max_processing_time_small']}s"
        
        assert len(result.chunks) > 0, "Should produce text chunks"
        
        # Log performance metrics
        print(f"\n📊 Medium File Performance:")
        print(f"   Processing Time: {metrics['elapsed_time']:.3f}s")
        print(f"   Memory Used: {metrics['memory_delta_mb']:.2f}MB")
        print(f"   Chunks Generated: {len(result.chunks)}")
    
    def test_large_file_processing_time(self, sample_files, performance_monitor):
        """Test large file processing performance."""
        performance_monitor.start_monitoring()
        
        # Process large file
        processor = get_processor_for_file(sample_files["large"])
        result = processor.process()
        
        metrics = performance_monitor.get_metrics()
        
        # Assertions
        assert metrics["elapsed_time"] < PERFORMANCE_CONFIG["max_processing_time_large"], \
               f"Large file processing took {metrics['elapsed_time']:.2f}s, expected < {PERFORMANCE_CONFIG['max_processing_time_large']}s"
        
        assert len(result.chunks) > 0, "Should produce text chunks"
        
        # Log performance metrics  
        print(f"\n📊 Large File Performance:")
        print(f"   Processing Time: {metrics['elapsed_time']:.3f}s")
        print(f"   Memory Used: {metrics['memory_delta_mb']:.2f}MB")
        print(f"   Chunks Generated: {len(result.chunks)}")
    
    def test_json_file_processing_performance(self, sample_files, performance_monitor):
        """Test JSON file processing performance."""
        performance_monitor.start_monitoring()
        
        # Process JSON file
        processor = get_processor_for_file(sample_files["json"])
        result = processor.process()
        
        metrics = performance_monitor.get_metrics()
        
        # Assertions
        assert metrics["elapsed_time"] < PERFORMANCE_CONFIG["max_processing_time_small"], \
               f"JSON processing took {metrics['elapsed_time']:.2f}s, expected < {PERFORMANCE_CONFIG['max_processing_time_small']}s"
        
        assert len(result.chunks) > 0, "Should produce chunks from JSON data"
        
        # Log performance metrics
        print(f"\n📊 JSON File Performance:")
        print(f"   Processing Time: {metrics['elapsed_time']:.3f}s")
        print(f"   Memory Used: {metrics['memory_delta_mb']:.2f}MB")
        print(f"   Chunks Generated: {len(result.chunks)}")
    
    def test_csv_file_processing_performance(self, sample_files, performance_monitor):
        """Test CSV file processing performance."""
        performance_monitor.start_monitoring()
        
        # Process CSV file
        processor = get_processor_for_file(sample_files["csv"])
        result = processor.process()
        
        metrics = performance_monitor.get_metrics()
        
        # Assertions
        assert metrics["elapsed_time"] < PERFORMANCE_CONFIG["max_processing_time_small"], \
               f"CSV processing took {metrics['elapsed_time']:.2f}s, expected < {PERFORMANCE_CONFIG['max_processing_time_small']}s"
        
        assert len(result.chunks) > 0, "Should produce chunks from CSV data"
        
        # Log performance metrics
        print(f"\n📊 CSV File Performance:")
        print(f"   Processing Time: {metrics['elapsed_time']:.3f}s")
        print(f"   Memory Used: {metrics['memory_delta_mb']:.2f}MB")
        print(f"   Chunks Generated: {len(result.chunks)}")

class TestBatchProcessingPerformance:
    """Test batch file processing performance."""
    
    def test_batch_processing_performance(self, sample_files, data_manager, performance_monitor):
        """Test batch processing of multiple files."""
        performance_monitor.start_monitoring()
        
        # Process multiple files
        file_paths = list(sample_files.values())
        result = data_manager.ingest_files(file_paths)
        
        metrics = performance_monitor.get_metrics()
        
        # Assertions
        expected_max_time = len(file_paths) * PERFORMANCE_CONFIG["max_processing_time_small"]
        assert metrics["elapsed_time"] < expected_max_time, \
               f"Batch processing took {metrics['elapsed_time']:.2f}s, expected < {expected_max_time}s"
        
        assert result.successful_files > 0, "Should process some files successfully"
        
        # Log performance metrics
        print(f"\n📊 Batch Processing Performance:")
        print(f"   Files Processed: {result.successful_files}")
        print(f"   Processing Rate: {result.successful_files / metrics['elapsed_time']:.1f} files/sec")
        print(f"   Total Time: {metrics['elapsed_time']:.3f}s")
        print(f"   Memory Used: {metrics['memory_delta_mb']:.2f}MB")

class TestMemoryUsage:
    """Test memory usage under various conditions."""
    
    def test_memory_usage_within_limits(self, sample_files, performance_monitor):
        """Test memory usage stays within acceptable limits."""
        performance_monitor.start_monitoring()
        
        # Process all sample files
        for file_path in sample_files.values():
            processor = get_processor_for_file(file_path)
            result = processor.process()
            
            # Check memory after each file
            metrics = performance_monitor.get_metrics()
            current_memory = metrics["current_memory_mb"] * 1024 * 1024  # Convert to bytes
            
            assert current_memory < PERFORMANCE_CONFIG["max_memory_usage"], \
                   f"Memory usage {current_memory / (1024*1024):.1f}MB exceeds limit {PERFORMANCE_CONFIG['max_memory_usage'] / (1024*1024):.1f}MB"
    
    def test_memory_leak_detection(self, sample_files, performance_monitor):
        """Test for memory leaks during repeated processing."""
        initial_metrics = None
        
        # Process files multiple times to detect leaks
        for iteration in range(10):
            performance_monitor.start_monitoring()
            
            for file_path in sample_files.values():
                processor = get_processor_for_file(file_path)
                result = processor.process()
            
            current_metrics = performance_monitor.get_metrics()
            
            if initial_metrics is None:
                initial_metrics = current_metrics
            else:
                # Check for excessive memory growth
                memory_growth = current_metrics["current_memory_mb"] - initial_metrics["current_memory_mb"]
                assert memory_growth < 50, f"Potential memory leak: {memory_growth:.1f}MB growth after {iteration + 1} iterations"
        
        print(f"\n📊 Memory Leak Test:")
        print(f"   Initial Memory: {initial_metrics['current_memory_mb']:.1f}MB")
        print(f"   Final Memory: {current_metrics['current_memory_mb']:.1f}MB")
        print(f"   Memory Growth: {current_metrics['current_memory_mb'] - initial_metrics['current_memory_mb']:.1f}MB")

class TestConcurrentPerformance:
    """Test performance under concurrent operations."""
    
    def test_concurrent_file_processing(self, sample_files, performance_monitor):
        """Test concurrent file processing performance."""
        performance_monitor.start_monitoring()
        
        def process_file(file_path):
            """Process a single file and return timing."""
            start_time = time.time()
            processor = get_processor_for_file(file_path)
            result = processor.process()
            return {
                "file": file_path.name,
                "time": time.time() - start_time,
                "chunks": len(result.chunks)
            }
        
        # Process files concurrently
        file_paths = list(sample_files.values())
        with concurrent.futures.ThreadPoolExecutor(max_workers=PERFORMANCE_CONFIG["concurrent_users"]) as executor:
            future_to_file = {executor.submit(process_file, path): path for path in file_paths}
            results = []
            
            for future in concurrent.futures.as_completed(future_to_file):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    pytest.fail(f"Concurrent processing failed: {str(e)}")
        
        metrics = performance_monitor.get_metrics()
        
        # Assertions
        assert len(results) == len(file_paths), "All files should be processed"
        
        max_individual_time = max(r["time"] for r in results)
        assert max_individual_time < PERFORMANCE_CONFIG["max_processing_time_small"] * 2, \
               f"Concurrent processing too slow: {max_individual_time:.2f}s"
        
        # Log performance metrics
        print(f"\n📊 Concurrent Processing Performance:")
        print(f"   Files Processed: {len(results)}")
        print(f"   Total Time: {metrics['elapsed_time']:.3f}s")
        print(f"   Average Time per File: {sum(r['time'] for r in results) / len(results):.3f}s")
        print(f"   Memory Used: {metrics['memory_delta_mb']:.2f}MB")

class TestStressPerformance:
    """Stress tests for performance under heavy load."""
    
    def test_repeated_processing_stress(self, sample_files, performance_monitor):
        """Test stress performance with repeated processing."""
        performance_monitor.start_monitoring()
        
        small_file = sample_files["small"]
        processor = get_processor_for_file(small_file)
        
        # Repeat processing many times
        iterations = 100
        for i in range(iterations):
            result = processor.process()
            
            # Check periodically
            if i % 20 == 0:
                metrics = performance_monitor.get_metrics()
                avg_time_per_iteration = metrics["elapsed_time"] / (i + 1)
                
                assert avg_time_per_iteration < PERFORMANCE_CONFIG["max_processing_time_small"], \
                       f"Performance degrading: {avg_time_per_iteration:.3f}s per iteration"
        
        final_metrics = performance_monitor.get_metrics()
        avg_time = final_metrics["elapsed_time"] / iterations
        
        # Log stress test results
        print(f"\n📊 Stress Test Performance:")
        print(f"   Iterations: {iterations}")
        print(f"   Total Time: {final_metrics['elapsed_time']:.3f}s")
        print(f"   Average Time per Iteration: {avg_time:.4f}s")
        print(f"   Memory Used: {final_metrics['memory_delta_mb']:.2f}MB")
        
        assert avg_time < PERFORMANCE_CONFIG["max_processing_time_small"] / 10, \
               f"Stress test performance too slow: {avg_time:.4f}s per iteration"

# Performance benchmark fixtures
@pytest.mark.benchmark
class TestBenchmarks:
    """Benchmark tests for performance tracking."""
    
    def test_benchmark_small_file_processing(self, benchmark, sample_files):
        """Benchmark small file processing."""
        small_file = sample_files["small"]
        processor = get_processor_for_file(small_file)
        
        result = benchmark(processor.process)
        
        assert len(result.chunks) > 0, "Should produce chunks"
        print(f"\n📈 Small File Benchmark: {benchmark.stats['mean']:.4f}s mean time")
    
    def test_benchmark_json_processing(self, benchmark, sample_files):
        """Benchmark JSON file processing."""
        json_file = sample_files["json"]
        processor = get_processor_for_file(json_file)
        
        result = benchmark(processor.process)
        
        assert len(result.chunks) > 0, "Should produce chunks"
        print(f"\n📈 JSON Processing Benchmark: {benchmark.stats['mean']:.4f}s mean time")
    
    def test_benchmark_csv_processing(self, benchmark, sample_files):
        """Benchmark CSV file processing."""
        csv_file = sample_files["csv"]
        processor = get_processor_for_file(csv_file)
        
        result = benchmark(processor.process)
        
        assert len(result.chunks) > 0, "Should produce chunks"
        print(f"\n📈 CSV Processing Benchmark: {benchmark.stats['mean']:.4f}s mean time")

# Additional utility functions for performance testing
def measure_operation_time(operation, *args, **kwargs):
    """Measure the execution time of an operation."""
    start_time = time.time()
    result = operation(*args, **kwargs)
    end_time = time.time()
    
    return result, end_time - start_time

def get_memory_usage():
    """Get current memory usage in MB."""
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)

def create_large_test_file(file_path: Path, size_mb: int):
    """Create a large test file for performance testing."""
    content = "This is test content for performance testing. " * 100
    
    with open(file_path, 'w') as f:
        bytes_written = 0
        target_bytes = size_mb * 1024 * 1024
        
        while bytes_written < target_bytes:
            f.write(content)
            bytes_written += len(content.encode('utf-8'))

# Test configuration validation
def test_performance_config():
    """Validate performance test configuration."""
    required_keys = [
        "max_processing_time_small",
        "max_processing_time_large", 
        "max_query_time",
        "max_memory_usage",
        "batch_size_limit"
    ]
    
    for key in required_keys:
        assert key in PERFORMANCE_CONFIG, f"Missing performance config key: {key}"
        assert isinstance(PERFORMANCE_CONFIG[key], (int, float)), f"Invalid type for config key: {key}"
        assert PERFORMANCE_CONFIG[key] > 0, f"Invalid value for config key: {key}"
    
    print("✅ Performance test configuration validated")