#!/usr/bin/env python3
"""
Comprehensive Test & Benchmark Runner
Executes all unit tests and performance benchmarks
"""

import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime
import os

class TestBenchmarkRunner:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "benchmarks": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        }
        self.backend_dir = Path(__file__).parent
        os.chdir(self.backend_dir)
    
    def run_test_file(self, test_file: str) -> dict:
        """Run a single test file with pytest"""
        print(f"\n{'='*70}")
        print(f"🧪 Running: {test_file}")
        print(f"{'='*70}")
        
        result = {
            "file": test_file,
            "status": "unknown",
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
        try:
            output = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            print(output.stdout)
            if output.stderr:
                print(output.stderr)
            
            # Parse output
            if "passed" in output.stdout:
                result["status"] = "✅ PASSED"
                # Extract numbers like "7 passed"
                for line in output.stdout.split('\n'):
                    if "passed" in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == "passed":
                                result["passed"] = int(parts[i-1])
            
            if "failed" in output.stdout:
                result["status"] = "❌ FAILED"
                for line in output.stdout.split('\n'):
                    if "FAILED" in line:
                        result["errors"].append(line)
            
            if output.returncode == 0:
                result["status"] = "✅ PASSED"
            else:
                if result["status"] == "unknown":
                    result["status"] = "❌ FAILED"
            
            return result
        
        except subprocess.TimeoutExpired:
            result["status"] = "⏱️ TIMEOUT"
            result["errors"].append("Test timed out after 60 seconds")
            return result
        except Exception as e:
            result["status"] = "❌ ERROR"
            result["errors"].append(str(e))
            return result
    
    def run_all_tests(self):
        """Run all test files in order"""
        test_files = [
            "test_models.py",
            "test_phase3_lstm.py",
            "test_phase3_direct.py",
            "test_phase4_direct.py",
            "test_phase5_direct.py",
            "test_phase6_direct.py",
        ]
        
        print("\n" + "🔥"*35)
        print("    CARBONSENSE TEST & BENCHMARK SUITE")
        print("🔥"*35)
        
        for test_file in test_files:
            test_path = self.backend_dir / test_file
            if test_path.exists():
                result = self.run_test_file(test_file)
                self.results["tests"][test_file] = result
                
                # Update summary
                self.results["summary"]["total_tests"] += result["passed"] + result["failed"]
                self.results["summary"]["passed"] += result["passed"]
                self.results["summary"]["failed"] += result["failed"]
            else:
                print(f"⚠️  Test file not found: {test_file}")
    
    def run_benchmarks(self):
        """Run the benchmark module"""
        print(f"\n{'='*70}")
        print("🚀 Running: Benchmark Module")
        print(f"{'='*70}")
        
        try:
            output = subprocess.run(
                [sys.executable, "benchmark_module.py"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes for benchmarks
            )
            
            print(output.stdout)
            if output.stderr:
                print(output.stderr)
            
            self.results["benchmarks"]["status"] = "✅ COMPLETED" if output.returncode == 0 else "❌ FAILED"
            
            # Try to find benchmark JSON results
            results_dir = self.backend_dir / "benchmark_results"
            if results_dir.exists():
                latest_file = max(results_dir.glob("*.json"))
                with open(latest_file) as f:
                    bench_data = json.load(f)
                    self.results["benchmarks"]["data"] = bench_data
            
            return output.returncode == 0
        
        except subprocess.TimeoutExpired:
            print("⏱️  Benchmarks timed out after 5 minutes")
            self.results["benchmarks"]["status"] = "⏱️ TIMEOUT"
            return False
        except Exception as e:
            print(f"❌ Benchmark error: {e}")
            self.results["benchmarks"]["status"] = "❌ ERROR"
            return False
    
    def generate_report(self):
        """Generate final report"""
        print("\n" + "="*70)
        print("📋 TEST & BENCHMARK REPORT")
        print("="*70)
        
        summary = self.results["summary"]
        
        print(f"\n✅ TESTS SUMMARY")
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  Passed: {summary['passed']} ✅")
        print(f"  Failed: {summary['failed']} ❌")
        print(f"  Success Rate: {(summary['passed']/max(summary['total_tests'], 1)*100):.1f}%")
        
        print(f"\n📊 INDIVIDUAL TEST FILES")
        for test_file, result in self.results["tests"].items():
            print(f"\n  {test_file}")
            print(f"    Status: {result['status']}")
            print(f"    Passed: {result['passed']}")
            if result['errors']:
                for error in result['errors'][:3]:  # Show first 3 errors
                    print(f"    Error: {error}")
        
        print(f"\n🚀 BENCHMARKS")
        bench_status = self.results["benchmarks"].get("status", "unknown")
        print(f"  Status: {bench_status}")
        
        if "data" in self.results["benchmarks"]:
            summaries = self.results["benchmarks"]["data"].get("summary", [])
            if summaries:
                print(f"  Performance Metrics:")
                for s in summaries:
                    print(f"    - {s['name']}: {s['avg_time_ms']:.2f}ms avg")
        
        # Save report
        report_file = self.backend_dir / f"test_benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n✅ Report saved to: {report_file}")
        
        return self.results
    
    def run_all(self):
        """Execute complete test and benchmark suite"""
        self.run_all_tests()
        self.run_benchmarks()
        return self.generate_report()


if __name__ == "__main__":
    runner = TestBenchmarkRunner()
    results = runner.run_all()
    
    # Exit with appropriate code
    if results["summary"]["failed"] > 0:
        sys.exit(1)
    sys.exit(0)
