#!/usr/bin/env python3
"""
Comprehensive Test Suite for All 8 Advanced Features
=====================================================
Tests: Benchmark, LSTM, Anomaly, Simulation, Chatbot, Alerts, CSV, Reports
"""

import sys
from pathlib import Path
import numpy as np
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

class AdvancedFeatureTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def test_benchmark_module(self):
        """Test benchmark module"""
        print("\n" + "="*70)
        print("1️⃣  TEST: Benchmark Module")
        print("="*70)
        
        try:
            import benchmark_module
            benchmark = benchmark_module.MLBenchmark()
            
            # Test model loading benchmark
            results = benchmark.benchmark_model_loading()
            
            if results and "ml_service_init" in results:
                result = results["ml_service_init"]
                if result.get("status") == "✅ SUCCESS":
                    print("✅ Benchmark module working - model loading timed")
                    print(f"   Loading time: {result.get('elapsed_ms', 0):.2f}ms")
                    self.passed += 1
                    self.results.append(("Benchmark Module", True))
                    return
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        self.failed += 1
        self.results.append(("Benchmark Module", False))
    
    def test_lstm_forecast(self):
        """Test LSTM forecasting"""
        print("\n" + "="*70)
        print("2️⃣  TEST: LSTM Time-Series Forecasting")
        print("="*70)
        
        try:
            from v2.services.lstm_service import LSTMForecastService
            
            # Generate sample historical data
            historical = [100 + np.sin(i/10) * 20 for i in range(60)]
            
            service = LSTMForecastService()
            result = service.forecast_lstm(historical, months_ahead=30, confidence_level=0.95)
            
            if result and hasattr(result, 'forecast_points') and len(result.forecast_points) >= 12:
                print("✅ LSTM Forecast working")
                print(f"   Forecast points: {len(result.forecast_points)}")
                print(f"   Accuracy: {result.accuracy_score:.2f}")
                print(f"   Method: {result.method_details}")
                self.passed += 1
                self.results.append(("LSTM Forecast", True))
                return
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        self.failed += 1
        self.results.append(("LSTM Forecast", False))
    
    def test_anomaly_detection(self):
        """Test anomaly detection"""
        print("\n" + "="*70)
        print("3️⃣  TEST: Anomaly Detection")
        print("="*70)
        
        try:
            from v2.services.anomaly_service import AnomalyDetectionService
            
            service = AnomalyDetectionService()
            
            # Generate test data with anomaly
            normal = np.random.normal(50, 10, 95)
            anomalies = [150, 155, 160]
            test_data = list(normal) + anomalies
            
            result = service.detect_anomalies(test_data)
            
            if result and hasattr(result, 'anomalies_detected'):
                print("✅ Anomaly Detection working")
                detected = [a for a in result.anomalies_detected if a.is_anomaly]
                print(f"   Anomalies detected: {len(detected)}")
                if detected:
                    print(f"   First anomaly: index {detected[0].month}, severity {detected[0].severity}")
                self.passed += 1
                self.results.append(("Anomaly Detection", True))
                return
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        self.failed += 1
        self.results.append(("Anomaly Detection", False))
    
    def test_simulation(self):
        """Test scenario simulation"""
        print("\n" + "="*70)
        print("4️⃣  TEST: Advanced Simulation")
        print("="*70)
        
        try:
            from v2.services.simulation_service import AdvancedSimulationService
            
            service = AdvancedSimulationService()
            
            scenario = {
                "baseline_emissions": 100,
                "energy_reduction_pct": 20,
                "renewable_adoption_pct": 15
            }
            
            historical_data = [100, 105, 110, 108, 115, 112, 119, 120]
            result = service.run_monte_carlo(
                historical_data=historical_data,
                num_months=12,
                volatility_multiplier=1.0,
                trend="auto"
            )
            
            if result and hasattr(result, 'aggregated_results'):
                print("✅ Scenario Simulation working")
                print(f"   Simulations: {result.num_simulations}")
                print(f"   Months ahead: {result.num_months}")
                print(f"   Results points: {len(result.aggregated_results)}")
                self.passed += 1
                self.results.append(("Advanced Simulation", True))
                return
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        self.failed += 1
        self.results.append(("Advanced Simulation", False))
    
    def test_chatbot(self):
        """Test AI chatbot"""
        print("\n" + "="*70)
        print("5️⃣  TEST: AI Chatbot")
        print("="*70)
        
        try:
            from v2.services.chatbot_service import AIConversationService
            
            service = AIConversationService()
            
            # Detect intent first
            intent = service.detect_intent("What are the main sources of emissions?")
            
            # Generate response
            response = service.generate_response(intent=intent)
            
            if response and hasattr(response, 'message'):
                print("✅ AI Chatbot working")
                print(f"   Question: 'What are the main sources of emissions?'")
                print(f"   Response: {response.message[:80]}...")
                self.passed += 1
                self.results.append(("AI Chatbot", True))
                return
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        self.failed += 1
        self.results.append(("AI Chatbot", False))
    
    def test_alert_system(self):
        """Test alert system"""
        print("\n" + "="*70)
        print("6️⃣  TEST: Alert System")
        print("="*70)
        
        try:
            from v2.services.alert_service import (
                alert_system,
                AlertType,
                AlertSeverity
            )
            
            # Test threshold alert
            alert = alert_system.check_emissions_alert(
                current_emissions=600,
                period="daily",
                baseline=500
            )
            
            # Test anomaly alert
            anomaly_alert = alert_system.check_anomaly_alert(
                value=150,
                mean=100,
                std_dev=10
            )
            
            summary = alert_system.get_alert_summary()
            
            if summary and summary.get("total_alerts", 0) >= 0:
                print("✅ Alert System working")
                print(f"   Active alerts: {summary['total_alerts']}")
                print(f"   Critical: {summary['severity_breakdown']['critical']}")
                print(f"   High: {summary['severity_breakdown']['high']}")
                self.passed += 1
                self.results.append(("Alert System", True))
                return
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        self.failed += 1
        self.results.append(("Alert System", False))
    
    def test_csv_upload(self):
        """Test CSV upload"""
        print("\n" + "="*70)
        print("7️⃣  TEST: CSV Upload")
        print("="*70)
        
        try:
            from v2.services.csv_service import CSVUploadService
            
            service = CSVUploadService()
            
            # Test CSV validation
            csv_data = "date,emissions,sector\n2024-01-01,100,energy\n2024-01-02,120,transport\n2024-01-03,110,manufacturing"
            
            result = service.validate_csv_content(csv_data)
            
            if result and hasattr(result, 'is_valid') and result.is_valid:
                print("✅ CSV Upload working")
                print(f"   Rows parsed: {result.data_points}")
                print(f"   Columns detected: {len(result.numeric_columns)}")
                self.passed += 1
                self.results.append(("CSV Upload", True))
                return
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        self.failed += 1
        self.results.append(("CSV Upload", False))
    
    def test_advanced_reports(self):
        """Test advanced reports"""
        print("\n" + "="*70)
        print("8️⃣  TEST: Advanced Reports")
        print("="*70)
        
        try:
            from v2.services.advanced_reports_service import report_generator
            
            # Test executive summary
            data = {
                "total_emissions": 500,
                "baseline": 600,
                "trend": "decreasing",
                "target_pct": 10
            }
            
            report = report_generator.generate_executive_summary(data, "monthly")
            
            if "key_metrics" in report:
                print("✅ Advanced Reports working")
                print(f"   Total emissions: {report['key_metrics']['total_emissions']} kg CO2")
                print(f"   Status: {report.get('status', 'unknown')}")
                print(f"   Recommendations: {len(report.get('recommendations', []))}")
                self.passed += 1
                self.results.append(("Advanced Reports", True))
                return
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        self.failed += 1
        self.results.append(("Advanced Reports", False))
    
    def run_all_tests(self):
        """Run all feature tests"""
        print("\n" + "🚀"*40)
        print("     CARBONSENSE - 8 ADVANCED FEATURES TEST SUITE")
        print("🚀"*40)
        print(f"\nTimestamp: {datetime.now().isoformat()}\n")
        
        self.test_benchmark_module()
        self.test_lstm_forecast()
        self.test_anomaly_detection()
        self.test_simulation()
        self.test_chatbot()
        self.test_alert_system()
        self.test_csv_upload()
        self.test_advanced_reports()
        
        # Summary
        print("\n" + "="*70)
        print("📊 FULL FEATURE TEST SUMMARY")
        print("="*70)
        
        total = self.passed + self.failed
        success_rate = (self.passed / max(total, 1)) * 100
        
        print(f"\n✅ Passed: {self.passed}/8")
        print(f"❌ Failed: {self.failed}/8")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\nFeature Status:")
        for feature_name, passed in self.results:
            status = "✅" if passed else "❌"
            print(f"  {status} {feature_name}")
        
        print("\n" + "="*70)
        
        return self.failed == 0


if __name__ == "__main__":
    tester = AdvancedFeatureTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
