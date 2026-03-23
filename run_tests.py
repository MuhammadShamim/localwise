#!/usr/bin/env python3
"""
LocalWise v1.0.0 - Test Suite Execution Script

This script provides a comprehensive test execution interface for running
LocalWise test suites with reporting and analysis capabilities.

Usage:
    python run_tests.py [options]

Examples:
    python run_tests.py --all                    # Run all tests
    python run_tests.py --unit                   # Run only unit tests
    python run_tests.py --integration            # Run only integration tests
    python run_tests.py --performance            # Run performance tests
    python run_tests.py --coverage               # Generate coverage report
    python run_tests.py --html                   # Generate HTML test report
"""

import argparse
import os
import subprocess
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Test configuration
TEST_CONFIG = {
    "test_dirs": {
        "unit": "tests/unit",
        "integration": "tests/integration", 
        "performance": "tests/performance",
        "fixtures": "tests/fixtures"
    },
    "coverage_threshold": 80,
    "performance_timeout": 300,  # 5 minutes
    "output_dir": "test_results",
    "html_dir": "test_results/html"
}

class TestRunner:
    """Comprehensive test execution and reporting."""
    
    def __init__(self):
        """Initialize test runner with configuration."""
        self.start_time = time.time()
        self.results = {
            "start_time": datetime.now().isoformat(),
            "test_runs": [],
            "summary": {},
            "coverage": None,
            "performance": {}
        }
        self.setup_output_directories()
    
    def setup_output_directories(self) -> None:
        """Create necessary output directories."""
        Path(TEST_CONFIG["output_dir"]).mkdir(exist_ok=True)
        Path(TEST_CONFIG["html_dir"]).mkdir(exist_ok=True)
    
    def run_command(self, command: List[str], description: str) -> Tuple[int, str, str]:
        """
        Execute a command and capture output.
        
        Args:
            command: Command to execute as list of strings
            description: Human-readable description of command
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        print(f"\n🔍 {description}")
        print(f"Command: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command,
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
                timeout=TEST_CONFIG.get("performance_timeout", 300)
            )
            
            if result.returncode == 0:
                print(f"✅ {description} - SUCCESS")
            else:
                print(f"❌ {description} - FAILED")
                if result.stderr:
                    print(f"Error: {result.stderr}")
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {description} - TIMEOUT")
            return 1, "", "Command timed out"
        except Exception as e:
            print(f"💥 {description} - ERROR: {str(e)}")
            return 1, "", str(e)
    
    def check_dependencies(self) -> bool:
        """Check if required testing dependencies are available."""
        required_packages = ["pytest", "pytest-cov", "pytest-html", "pytest-xvfb"]
        missing_packages = []
        
        print("🔍 Checking test dependencies...")
        
        for package in required_packages:
            returncode, _, _ = self.run_command(
                [sys.executable, "-c", f"import {package.replace('-', '_')}"],
                f"Checking {package}"
            )
            if returncode != 0:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing required packages: {', '.join(missing_packages)}")
            print("Install with: pip install " + " ".join(missing_packages))
            return False
        
        print("✅ All test dependencies available")
        return True
    
    def run_unit_tests(self, verbose: bool = False) -> Dict:
        """Run unit tests with coverage."""
        print("\n" + "="*60)
        print("🧪 RUNNING UNIT TESTS")
        print("="*60)
        
        command = [
            sys.executable, "-m", "pytest",
            TEST_CONFIG["test_dirs"]["unit"],
            "--cov=localwise",
            "--cov-report=term-missing",
            "--cov-report=json:test_results/coverage.json", 
            "--cov-report=html:test_results/html/coverage",
            "--junitxml=test_results/unit_tests.xml",
            "-v" if verbose else ""
        ]
        command = [cmd for cmd in command if cmd]  # Remove empty strings
        
        returncode, stdout, stderr = self.run_command(
            command, "Unit Tests with Coverage"
        )
        
        result = {
            "type": "unit",
            "returncode": returncode,
            "stdout": stdout,
            "stderr": stderr,
            "execution_time": time.time() - self.start_time
        }
        
        self.results["test_runs"].append(result)
        return result
    
    def run_integration_tests(self, verbose: bool = False) -> Dict:
        """Run integration tests."""
        print("\n" + "="*60)
        print("🔗 RUNNING INTEGRATION TESTS")
        print("="*60)
        
        command = [
            sys.executable, "-m", "pytest",
            TEST_CONFIG["test_dirs"]["integration"],
            "--junitxml=test_results/integration_tests.xml",
            "-v" if verbose else ""
        ]
        command = [cmd for cmd in command if cmd]
        
        returncode, stdout, stderr = self.run_command(
            command, "Integration Tests"
        )
        
        result = {
            "type": "integration", 
            "returncode": returncode,
            "stdout": stdout,
            "stderr": stderr,
            "execution_time": time.time() - self.start_time
        }
        
        self.results["test_runs"].append(result)
        return result
    
    def run_performance_tests(self) -> Dict:
        """Run performance tests with timing analysis."""
        print("\n" + "="*60)
        print("⚡ RUNNING PERFORMANCE TESTS")
        print("="*60)
        
        # Check if performance test directory exists
        perf_dir = Path(TEST_CONFIG["test_dirs"]["performance"])
        if not perf_dir.exists():
            print(f"⚠️  Performance test directory not found: {perf_dir}")
            return {"type": "performance", "returncode": 1, "error": "No performance tests"}
        
        command = [
            sys.executable, "-m", "pytest",
            str(perf_dir),
            "--benchmark-json=test_results/performance.json",
            "--junitxml=test_results/performance_tests.xml",
            "-v"
        ]
        
        returncode, stdout, stderr = self.run_command(
            command, "Performance Tests"
        )
        
        result = {
            "type": "performance",
            "returncode": returncode, 
            "stdout": stdout,
            "stderr": stderr,
            "execution_time": time.time() - self.start_time
        }
        
        self.results["test_runs"].append(result)
        return result
    
    def generate_html_report(self) -> Dict:
        """Generate comprehensive HTML test report."""
        print("\n" + "="*60)
        print("📊 GENERATING HTML TEST REPORT")
        print("="*60)
        
        # Run pytest with HTML report generation
        command = [
            sys.executable, "-m", "pytest",
            TEST_CONFIG["test_dirs"]["unit"],
            TEST_CONFIG["test_dirs"]["integration"],
            "--html=test_results/html/test_report.html",
            "--self-contained-html",
            "--cov=localwise",
            "--cov-report=html:test_results/html/coverage"
        ]
        
        returncode, stdout, stderr = self.run_command(
            command, "HTML Test Report Generation"
        )
        
        if returncode == 0:
            report_path = Path("test_results/html/test_report.html").absolute()
            print(f"📄 HTML Report: {report_path}")
            print(f"📊 Coverage Report: {Path('test_results/html/coverage/index.html').absolute()}")
        
        return {
            "type": "html_report",
            "returncode": returncode,
            "stdout": stdout,
            "stderr": stderr
        }
    
    def analyze_coverage(self) -> Optional[Dict]:
        """Analyze test coverage from coverage report."""
        coverage_file = Path("test_results/coverage.json")
        
        if not coverage_file.exists():
            return None
        
        try:
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
            
            summary = coverage_data.get('totals', {})
            coverage_percentage = summary.get('percent_covered', 0)
            
            coverage_analysis = {
                "total_percentage": round(coverage_percentage, 2),
                "total_lines": summary.get('num_statements', 0),
                "covered_lines": summary.get('covered_lines', 0),
                "missing_lines": summary.get('missing_lines', 0),
                "threshold_met": coverage_percentage >= TEST_CONFIG["coverage_threshold"],
                "threshold": TEST_CONFIG["coverage_threshold"]
            }
            
            self.results["coverage"] = coverage_analysis
            return coverage_analysis
            
        except Exception as e:
            print(f"⚠️  Could not analyze coverage: {str(e)}")
            return None
    
    def generate_summary_report(self) -> None:
        """Generate comprehensive test execution summary."""
        print("\n" + "="*80)
        print("📋 TEST EXECUTION SUMMARY")
        print("="*80)
        
        total_time = time.time() - self.start_time
        self.results["end_time"] = datetime.now().isoformat() 
        self.results["total_execution_time"] = total_time
        
        # Test execution summary
        passed_runs = [run for run in self.results["test_runs"] if run["returncode"] == 0]
        failed_runs = [run for run in self.results["test_runs"] if run["returncode"] != 0]
        
        print(f"⏱️  Total Execution Time: {total_time:.2f} seconds")
        print(f"✅ Passed Test Suites: {len(passed_runs)}")
        print(f"❌ Failed Test Suites: {len(failed_runs)}")
        
        # Individual test suite results
        for run in self.results["test_runs"]:
            status = "✅ PASSED" if run["returncode"] == 0 else "❌ FAILED"
            print(f"{run['type'].title()} Tests: {status}")
        
        # Coverage analysis
        if self.results.get("coverage"):
            cov = self.results["coverage"]
            status = "✅ PASSED" if cov["threshold_met"] else "❌ FAILED"
            print(f"📊 Coverage: {cov['total_percentage']}% {status}")
        
        # Overall status
        overall_success = len(failed_runs) == 0
        if self.results.get("coverage") and not self.results["coverage"]["threshold_met"]:
            overall_success = False
        
        print(f"\n🎯 OVERALL STATUS: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")
        
        # Save detailed results
        results_file = Path("test_results/test_execution_results.json")
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📄 Detailed results saved to: {results_file.absolute()}")
    
    def run_all_tests(self, verbose: bool = False, html_report: bool = False) -> bool:
        """Run complete test suite."""
        print("🚀 Starting LocalWise v1.0.0 Test Suite")
        print("="*60)
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Run test suites
        self.run_unit_tests(verbose)
        self.run_integration_tests(verbose)
        
        # Run performance tests if available
        perf_dir = Path(TEST_CONFIG["test_dirs"]["performance"])
        if perf_dir.exists():
            self.run_performance_tests()
        
        # Generate HTML report if requested
        if html_report:
            self.generate_html_report()
        
        # Analyze coverage
        self.analyze_coverage()
        
        # Generate summary
        self.generate_summary_report()
        
        # Return overall success status
        failed_runs = [run for run in self.results["test_runs"] if run["returncode"] != 0]
        coverage_ok = not self.results.get("coverage") or self.results["coverage"]["threshold_met"]
        
        return len(failed_runs) == 0 and coverage_ok

def main():
    """Main test execution entry point."""
    parser = argparse.ArgumentParser(
        description="LocalWise v1.0.0 Test Suite Execution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --all                 Run all test suites
  python run_tests.py --unit                Run only unit tests  
  python run_tests.py --integration         Run only integration tests
  python run_tests.py --performance         Run only performance tests
  python run_tests.py --coverage            Show coverage analysis
  python run_tests.py --html                Generate HTML reports
  python run_tests.py --all --verbose       Run all tests with verbose output
        """
    )
    
    # Test suite selection
    parser.add_argument("--all", action="store_true", help="Run all test suites")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    
    # Output options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose test output")
    parser.add_argument("--html", action="store_true", help="Generate HTML test report")
    parser.add_argument("--coverage", action="store_true", help="Show coverage analysis only")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.all, args.unit, args.integration, args.performance, args.coverage]):
        parser.print_help()
        print("\n❌ Error: Please specify which tests to run")
        return 1
    
    # Initialize test runner
    runner = TestRunner()
    
    try:
        # Execute requested tests
        if args.coverage:
            # Just show coverage analysis
            coverage = runner.analyze_coverage()
            if coverage:
                print("📊 Coverage Analysis:")
                print(f"Total Coverage: {coverage['total_percentage']}%")
                print(f"Threshold: {coverage['threshold']}%")
                print(f"Status: {'✅ PASSED' if coverage['threshold_met'] else '❌ FAILED'}")
            else:
                print("❌ No coverage data found. Run tests with coverage first.")
                return 1
        
        elif args.all:
            success = runner.run_all_tests(verbose=args.verbose, html_report=args.html)
            return 0 if success else 1
        
        else:
            # Run specific test suites
            if args.unit:
                result = runner.run_unit_tests(verbose=args.verbose)
                if result["returncode"] != 0:
                    return 1
            
            if args.integration:
                result = runner.run_integration_tests(verbose=args.verbose)
                if result["returncode"] != 0:
                    return 1
            
            if args.performance:
                result = runner.run_performance_tests()
                if result["returncode"] != 0:
                    return 1
            
            # Generate HTML report if requested
            if args.html:
                runner.generate_html_report()
            
            # Show coverage if unit tests were run
            if args.unit:
                runner.analyze_coverage()
            
            # Generate summary for multiple test runs
            runner.generate_summary_report()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Test execution failed with error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())