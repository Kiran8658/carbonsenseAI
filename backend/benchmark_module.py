"""
Comprehensive Benchmarking Module for CarbonSense ML Models
===========================================================
Tests performance, accuracy, and efficiency of all ML services
"""

import time
import json
import psutil
import os
from datetime import datetime
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from pathlib import Path

# Performance metrics tracker
class BenchmarkMetrics:
    def __init__(self, name: str):
        self.name = name
        self.timings = []
        self.memory_usage = []
        self.start_time = None
        self.start_memory = None
        
    def start(self):
        self.start_time = time.time()
        process = psutil.Process(os.getpid())
        self.start_memory = process.memory_info().rss / 1024 / 1024  # MB
        
    def end(self):
        elapsed = time.time() - self.start_time
        process = psutil.Process(os.getpid())
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_delta = end_memory - self.start_memory
        
        self.timings.append(elapsed)
        self.memory_usage.append(memory_delta)
        
        return {
            "elapsed_ms": elapsed * 1000,
            "memory_delta_mb": memory_delta
        }
    
    def summary(self) -> Dict[str, Any]:
        if not self.timings:
            return {}
        
        return {
            "name": self.name,
            "calls": len(self.timings),
            "avg_time_ms": np.mean(self.timings) * 1000,
            "min_time_ms": np.min(self.timings) * 1000,
            "max_time_ms": np.max(self.timings) * 1000,
            "total_time_ms": np.sum(self.timings) * 1000,
            "avg_memory_mb": np.mean(self.memory_usage),
            "peak_memory_mb": np.max(self.memory_usage),
        }


class MLBenchmark:
    """Benchmark suite for all ML services"""
    
    def __init__(self, output_dir: str = "./benchmark_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.metrics: Dict[str, BenchmarkMetrics] = {}
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "benchmarks": {},
            "summary": {}
        }
    
    def benchmark_model_loading(self) -> Dict[str, Any]:
        """Benchmark: Model loading and initialization times"""
        print("\n📊 BENCHMARK: Model Loading Times")
        print("=" * 60)
        
        from services.ml_service import initialize_models
        
        results = {}
        
        # Test 1: ML Service initialization
        metric = BenchmarkMetrics("ml_service_init")
        metric.start()
        try:
            initialize_models()
            result = metric.end()
            results["ml_service_init"] = {**result, "status": "✅ SUCCESS"}
            print(f"✅ Models Initialized: {result['elapsed_ms']:.2f}ms, Memory: {result['memory_delta_mb']:.2f}MB")
        except Exception as e:
            results["ml_service_init"] = {"status": "❌ FAILED", "error": str(e)}
            print(f"❌ Model Init Failed: {e}")
        
        self.metrics["model_loading"] = metric
        return results
    
    def benchmark_emissions_prediction(self) -> Dict[str, Any]:
        """Benchmark: Emissions prediction latency"""
        print("\n📊 BENCHMARK: Emissions Prediction (50 samples)")
        print("=" * 60)
        
        from services.ml_service import predict_emissions, initialize_models
        
        results = {}
        initialize_models()
        
        # Create sample data
        test_data = [
            {"electricity_kwh": 50.0, "fuel_litres": 25.0}
            for _ in range(50)
        ]
        
        metric = BenchmarkMetrics("emissions_prediction")
        
        for i, data in enumerate(test_data):
            metric.start()
            try:
                pred = predict_emissions(
                    electricity_kwh=data["electricity_kwh"],
                    fuel_litres=data["fuel_litres"]
                )
                result = metric.end()
                if i % 10 == 0:
                    print(f"  Sample {i+1}: {result['elapsed_ms']:.2f}ms")
            except Exception as e:
                print(f"❌ Prediction failed: {e}")
                break
        
        summary = metric.summary()
        results["emissions_prediction"] = summary
        if summary:
            print(f"\n📈 Summary:")
            print(f"   Avg: {summary['avg_time_ms']:.2f}ms")
            print(f"   Min: {summary['min_time_ms']:.2f}ms")
            print(f"   Max: {summary['max_time_ms']:.2f}ms")
            print(f"   Total: {summary['total_time_ms']:.0f}ms for {summary['calls']} calls")
        
        self.metrics["emissions_prediction"] = metric
        return results
    
    def benchmark_lstm_forecasting(self) -> Dict[str, Any]:
        """Benchmark: LSTM forecasting service"""
        print("\n📊 BENCHMARK: LSTM Time-Series Forecasting")
        print("=" * 60)
        
        try:
            from v2.services.lstm_service import LSTMService
            
            results = {}
            lstm = LSTMService()
            
            # Sample historical data
            dates = pd.date_range(start='2023-01-01', periods=60, freq='D')
            historical_data = {
                "dates": dates.strftime('%Y-%m-%d').tolist(),
                "values": np.random.uniform(20, 100, 60).tolist()
            }
            
            metric = BenchmarkMetrics("lstm_forecast")
            
            # Test forecasting
            metric.start()
            try:
                forecast = lstm.forecast_emissions(
                    historical_data=historical_data["values"],
                    periods=30
                )
                result = metric.end()
                results["lstm_forecast"] = {
                    **result,
                    "status": "✅ SUCCESS",
                    "forecast_points": len(forecast.get("forecast", []))
                }
                print(f"✅ LSTM Forecast (30 days): {result['elapsed_ms']:.2f}ms")
                print(f"   Forecast points: {len(forecast.get('forecast', []))}")
            except Exception as e:
                results["lstm_forecast"] = {"status": "❌ FAILED", "error": str(e)}
                print(f"❌ LSTM Forecast Failed: {e}")
            
            self.metrics["lstm_forecasting"] = metric
            return results
        except ImportError:
            print("⚠️  LSTM Service not fully configured")
            return {"lstm_forecast": {"status": "⚠️ SKIPPED", "reason": "Service not available"}}
    
    def benchmark_anomaly_detection(self) -> Dict[str, Any]:
        """Benchmark: Anomaly detection service"""
        print("\n📊 BENCHMARK: Anomaly Detection")
        print("=" * 60)
        
        try:
            from v2.services.anomaly_service import AnomalyService
            
            results = {}
            anomaly = AnomalyService()
            
            # Generate test data with anomalies
            normal_data = np.random.normal(50, 10, 95).tolist()
            anomaly_data = [150, 160, 155] + np.random.normal(50, 10, 2).tolist()
            test_data = normal_data + anomaly_data
            
            metric = BenchmarkMetrics("anomaly_detection")
            
            metric.start()
            try:
                result = anomaly.detect_anomalies(test_data)
                perf = metric.end()
                results["anomaly_detection"] = {
                    **perf,
                    "status": "✅ SUCCESS",
                    "anomalies_found": len(result.get("anomalies", []))
                }
                print(f"✅ Anomaly Detection (100 samples): {perf['elapsed_ms']:.2f}ms")
                print(f"   Anomalies detected: {len(result.get('anomalies', []))}")
            except Exception as e:
                results["anomaly_detection"] = {"status": "❌ FAILED", "error": str(e)}
                print(f"❌ Anomaly Detection Failed: {e}")
            
            self.metrics["anomaly_detection"] = metric
            return results
        except ImportError:
            print("⚠️  Anomaly Service not fully configured")
            return {"anomaly": {"status": "⚠️ SKIPPED"}}
    
    def benchmark_scenario_simulation(self) -> Dict[str, Any]:
        """Benchmark: Scenario simulation service"""
        print("\n📊 BENCHMARK: Scenario Simulation")
        print("=" * 60)
        
        try:
            from v2.services.simulation_service import SimulationService
            
            results = {}
            sim = SimulationService()
            
            test_scenario = {
                "baseline_emissions": 100,
                "changes": {
                    "energy_reduction": 0.20,
                    "renewable_adoption": 0.15
                }
            }
            
            metric = BenchmarkMetrics("scenario_simulation")
            
            metric.start()
            try:
                result = sim.simulate_scenario(test_scenario)
                perf = metric.end()
                results["scenario_simulation"] = {
                    **perf,
                    "status": "✅ SUCCESS",
                    "impact": result.get("projected_emissions", 0)
                }
                print(f"✅ Scenario Simulation: {perf['elapsed_ms']:.2f}ms")
                print(f"   Projected emissions: {result.get('projected_emissions', 0):.2f}")
            except Exception as e:
                results["scenario_simulation"] = {"status": "❌ FAILED", "error": str(e)}
                print(f"❌ Scenario Simulation Failed: {e}")
            
            self.metrics["scenario_simulation"] = metric
            return results
        except ImportError:
            print("⚠️  Simulation Service not fully configured")
            return {"simulation": {"status": "⚠️ SKIPPED"}}
    
    def benchmark_api_endpoints(self) -> Dict[str, Any]:
        """Benchmark: API endpoint response times"""
        print("\n📊 BENCHMARK: API Endpoint Response Times")
        print("=" * 60)
        
        try:
            import requests
            
            results = {}
            base_url = "http://localhost:8005"
            
            endpoints = [
                ("/health", "GET", {}),
                ("/api/sectors", "GET", {}),
                ("/api/calculate", "POST", {
                    "sector": "energy",
                    "consumption": 50,
                    "region": "us"
                }),
            ]
            
            for endpoint, method, data in endpoints:
                metric = BenchmarkMetrics(f"api_{method}_{endpoint}")
                
                for _ in range(5):
                    metric.start()
                    try:
                        if method == "GET":
                            requests.get(f"{base_url}{endpoint}", timeout=5)
                        else:
                            requests.post(f"{base_url}{endpoint}", json=data, timeout=5)
                        metric.end()
                    except Exception as e:
                        print(f"❌ {method} {endpoint}: {e}")
                        break
                
                summary = metric.summary()
                results[f"{method}_{endpoint}"] = summary
                print(f"✅ {method} {endpoint}: avg {summary['avg_time_ms']:.2f}ms")
            
            return results
        except ImportError:
            print("⚠️  Requests library not available")
            return {}
    
    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all benchmarks and generate report"""
        print("\n" + "="*70)
        print("🚀 CARBONSENSE ML BENCHMARKING SUITE")
        print("="*70)
        
        try:
            self.results["benchmarks"]["model_loading"] = self.benchmark_model_loading()
        except Exception as e:
            print(f"⚠️  Model loading benchmark failed: {e}")
        
        try:
            self.results["benchmarks"]["emissions_prediction"] = self.benchmark_emissions_prediction()
        except Exception as e:
            print(f"⚠️  Emissions prediction benchmark failed: {e}")
        
        try:
            self.results["benchmarks"]["lstm_forecasting"] = self.benchmark_lstm_forecasting()
        except Exception as e:
            print(f"⚠️  LSTM benchmark failed: {e}")
        
        try:
            self.results["benchmarks"]["anomaly_detection"] = self.benchmark_anomaly_detection()
        except Exception as e:
            print(f"⚠️  Anomaly detection benchmark failed: {e}")
        
        try:
            self.results["benchmarks"]["scenario_simulation"] = self.benchmark_scenario_simulation()
        except Exception as e:
            print(f"⚠️  Simulation benchmark failed: {e}")
        
        try:
            self.results["benchmarks"]["api_endpoints"] = self.benchmark_api_endpoints()
        except Exception as e:
            print(f"⚠️  API endpoint benchmark failed: {e}")
        
        # Generate summary
        self.generate_summary()
        
        # Save results
        self.save_results()
        
        return self.results
    
    def generate_summary(self):
        """Generate summary statistics"""
        print("\n" + "="*70)
        print("📊 BENCHMARK SUMMARY")
        print("="*70)
        
        summary_stats = []
        for metric_name, metric_obj in self.metrics.items():
            summary = metric_obj.summary()
            if summary:
                summary_stats.append(summary)
                print(f"\n{summary['name']}:")
                print(f"  Calls: {summary['calls']}")
                print(f"  Avg Time: {summary['avg_time_ms']:.2f}ms")
                print(f"  Min/Max: {summary['min_time_ms']:.2f}ms / {summary['max_time_ms']:.2f}ms")
                if summary.get('avg_memory_mb'):
                    print(f"  Memory: {summary['avg_memory_mb']:.2f}MB (peak: {summary['peak_memory_mb']:.2f}MB)")
        
        self.results["summary"] = summary_stats
    
    def save_results(self):
        """Save benchmark results to JSON"""
        output_file = self.output_dir / f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert numpy types to native Python types for JSON serialization
        def convert(o):
            if isinstance(o, (np.integer, np.floating)):
                return float(o)
            elif isinstance(o, np.ndarray):
                return o.tolist()
            return str(o)
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=convert)
        
        print(f"\n✅ Results saved to: {output_file}")


if __name__ == "__main__":
    benchmark = MLBenchmark()
    benchmark.run_all_benchmarks()
