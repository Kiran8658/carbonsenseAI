import React, { useState, useEffect } from "react";
import axios from "axios";
import Sidebar from "../components/Sidebar";
import PieBreakdown from "../components/charts/PieBreakdown";
import TrendChart from "../components/charts/TrendChart";
import { 
  FileText, 
  Download, 
  Activity, 
  Zap, 
  Fuel, 
  Calculator,
  BarChart3,
  TrendingUp,
  AlertCircle,
  CheckCircle
} from "lucide-react";

const API_URL = typeof window !== "undefined"
  ? `http://${window.location.hostname}:8005`
  : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8005");

interface EmissionData {
  total_co2: number;
  electricity_co2: number;
  fuel_co2: number;
  carbon_score: string;
  carbon_score_value: number;
  breakdown_percentage: {
    electricity: number;
    fuel: number;
  };
}

interface ModelStatus {
  emissions_model: string;
  scorer_model: string;
  trend_model: string;
}

export default function ReportsPage() {
  const [electricity, setElectricity] = useState("");
  const [fuel, setFuel] = useState("");
  const [emissionData, setEmissionData] = useState<EmissionData | null>(null);
  const [modelStatus, setModelStatus] = useState<ModelStatus | null>(null);
  const [backendConnected, setBackendConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [reportGenerating, setReportGenerating] = useState(false);

  useEffect(() => {
    checkBackendStatus();
    const interval = setInterval(checkBackendStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  // Auto-refresh data every 4 seconds when backend is connected and data exists
  useEffect(() => {
    if (!backendConnected || !electricity || !fuel) return;
    
    const refreshInterval = setInterval(() => {
      refreshData();
    }, 4000);
    
    return () => clearInterval(refreshInterval);
  }, [backendConnected, electricity, fuel]);

  const refreshData = async () => {
    if (!electricity || !fuel) return;
    try {
      const response = await axios.post("http://localhost:8005/api/calculate", {
        electricity_kwh: parseFloat(electricity),
        fuel_litres: parseFloat(fuel),
      });
      if (response.data?.data) {
        setEmissionData(response.data.data);
      }
    } catch (error) {
      console.error("Auto-refresh error:", error);
    }
  };

  const checkBackendStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/health`, { timeout: 3000 });
      if (response.data) {
        setBackendConnected(true);
        setModelStatus(response.data.models);
      }
    } catch (error) {
      setBackendConnected(false);
      setModelStatus(null);
    }
  };

  const handleCalculate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!electricity || !fuel) return;

    if (!backendConnected) {
      alert("Backend is not connected! Please start the backend server on port 8005.");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/calculate`, {
        electricity_kwh: parseFloat(electricity),
        fuel_litres: parseFloat(fuel),
      });
      
      if (response.data && response.data.data) {
        setEmissionData(response.data.data);
      }
    } catch (error) {
      console.error("Error calculating emissions:", error);
      alert("Failed to calculate. Please check backend connection.");
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = async () => {
    if (!emissionData || !backendConnected) {
      alert("Please calculate emissions first and ensure backend is connected.");
      return;
    }

    setReportGenerating(true);
    try {
      const response = await axios.post(`${API_URL}/api/reports/generate-download`, {
        emission_data: emissionData,
        history: [],
        forecast: [],
        models_used: {},
      }, { 
        responseType: 'blob',
        timeout: 30000 
      });

      // response.data is already a Blob when using responseType: 'blob'
      const blob = response.data;
      
      if (!blob || blob.size === 0) {
        throw new Error("Received empty PDF. Check backend logs.");
      }

      // Check if it's actually a PDF
      if (!blob.type.includes('application/pdf') && !blob.type.includes('octet-stream')) {
        const text = await blob.text();
        if (text.includes('error') || text.includes('Error')) {
          throw new Error(`Backend error: ${text.substring(0, 200)}`);
        }
      }

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `CarbonSense_Report_${new Date().toISOString().split('T')[0]}.pdf`);
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      setTimeout(() => {
        link.remove();
        window.URL.revokeObjectURL(url);
      }, 100);

      alert("✅ Report downloaded successfully!");
    } catch (error: any) {
      console.error("Error downloading PDF:", error);
      const errorMsg = error?.response?.data?.detail || error?.message || "Unknown error";
      alert(`❌ Failed to download PDF: ${errorMsg}`);
    } finally {
      setReportGenerating(false);
    }
  };

  const getScoreColor = (score: string) => {
    switch (score) {
      case "Excellent": return "#22c55e";
      case "Good": return "#84cc16";
      case "Average": return "#eab308";
      case "Poor": return "#f97316";
      default: return "#ef4444";
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      <Sidebar />

      <main className="ml-64 p-8 space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-4xl font-bold text-white tracking-tight">Reports</h1>
              <div className="flex items-center gap-2 px-3 py-1 bg-[#c8f07a]/20 rounded-full border border-[#c8f07a]/30">
                <FileText size={14} className="text-[#c8f07a]" />
                <span className="text-xs font-semibold text-[#c8f07a]">PDF Export</span>
              </div>
            </div>
            <p className="text-[#888888]">
              Generate comprehensive AI-powered carbon emission reports with all model outputs
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${backendConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            <span className={`text-sm ${backendConnected ? 'text-green-400' : 'text-red-400'}`}>
              {backendConnected ? 'Backend Connected' : 'Backend Disconnected'}
            </span>
          </div>
        </div>

        {/* Input Form */}
        <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
          <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <Calculator size={20} className="text-[#c8f07a]" />
            Data Input for Report Generation
          </h2>
          
          <form onSubmit={handleCalculate} className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-[#888888] mb-2">
                <Zap size={16} className="text-blue-400" />
                Electricity Usage (kWh/month)
              </label>
              <input
                type="number"
                value={electricity}
                onChange={(e) => setElectricity(e.target.value)}
                placeholder="e.g., 500"
                className="w-full bg-[#1a1a1a] border border-[#333333] rounded-lg px-4 py-3 text-white placeholder-[#666666] focus:outline-none focus:border-[#c8f07a]"
                required
                min="0"
                step="0.1"
              />
              {electricity && (
                <p className="text-xs text-blue-400 mt-2">
                  ≈ {(parseFloat(electricity) * 0.82).toFixed(1)} kg CO₂
                </p>
              )}
            </div>

            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-[#888888] mb-2">
                <Fuel size={16} className="text-orange-400" />
                Fuel Consumption (Litres/month)
              </label>
              <input
                type="number"
                value={fuel}
                onChange={(e) => setFuel(e.target.value)}
                placeholder="e.g., 100"
                className="w-full bg-[#1a1a1a] border border-[#333333] rounded-lg px-4 py-3 text-white placeholder-[#666666] focus:outline-none focus:border-[#c8f07a]"
                required
                min="0"
                step="0.1"
              />
              {fuel && (
                <p className="text-xs text-orange-400 mt-2">
                  ≈ {(parseFloat(fuel) * 2.3).toFixed(1)} kg CO₂
                </p>
              )}
            </div>

            <div className="flex items-end">
              <button
                type="submit"
                disabled={loading || !electricity || !fuel || !backendConnected}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-[#c8f07a] text-black rounded-lg font-medium hover:bg-[#d4f5a0] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <Activity className="animate-spin" size={18} />
                    Processing All Models...
                  </>
                ) : (
                  <>
                    <FileText size={18} />
                    Generate Full Report
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Results */}
        {emissionData && (
          <>
            {/* Model 1: Emissions Predictor Output */}
            <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                  <BarChart3 size={20} className="text-blue-400" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">Model 1: Emissions Predictor Output</h2>
                  <p className="text-[#888888] text-sm">AI-calculated carbon emissions breakdown</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-[#1a1a1a] rounded-xl p-4 border border-[#333333]">
                  <span className="text-[#888888] text-sm">Total CO₂ Emissions</span>
                  <p className="text-2xl font-bold text-white">{emissionData.total_co2.toFixed(2)} kg</p>
                </div>
                <div className="bg-[#1a1a1a] rounded-xl p-4 border border-[#333333]">
                  <span className="text-[#888888] text-sm">Electricity CO₂</span>
                  <p className="text-2xl font-bold text-blue-400">{emissionData.electricity_co2.toFixed(2)} kg</p>
                </div>
                <div className="bg-[#1a1a1a] rounded-xl p-4 border border-[#333333]">
                  <span className="text-[#888888] text-sm">Fuel CO₂</span>
                  <p className="text-2xl font-bold text-orange-400">{emissionData.fuel_co2.toFixed(2)} kg</p>
                </div>
                <div className="bg-[#1a1a1a] rounded-xl p-4 border border-[#333333]">
                  <span className="text-[#888888] text-sm">Emission Factor</span>
                  <p className="text-2xl font-bold text-[#c8f07a]">0.82 + 2.3</p>
                </div>
              </div>

              <div className="mt-6 grid grid-cols-2 gap-4">
                <div className="bg-[#1a1a1a] rounded-xl p-4 border border-[#333333]">
                  <div className="flex items-center gap-2 mb-2">
                    <Zap size={16} className="text-blue-400" />
                    <span className="text-[#888888] text-sm">Electricity Breakdown</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-[#333333] rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-blue-400 rounded-full"
                        style={{ width: `${emissionData.breakdown_percentage.electricity}%` }}
                      />
                    </div>
                    <span className="text-white font-bold">{emissionData.breakdown_percentage.electricity}%</span>
                  </div>
                </div>
                <div className="bg-[#1a1a1a] rounded-xl p-4 border border-[#333333]">
                  <div className="flex items-center gap-2 mb-2">
                    <Fuel size={16} className="text-orange-400" />
                    <span className="text-[#888888] text-sm">Fuel Breakdown</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-[#333333] rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-orange-400 rounded-full"
                        style={{ width: `${emissionData.breakdown_percentage.fuel}%` }}
                      />
                    </div>
                    <span className="text-white font-bold">{emissionData.breakdown_percentage.fuel}%</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Model 2: Carbon Scorer Output */}
            <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                  <AlertCircle size={20} className="text-purple-400" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">Model 2: Carbon Scorer Output</h2>
                  <p className="text-[#888888] text-sm">AI-generated sustainability grade</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-[#1a1a1a] rounded-xl p-6 border border-[#333333] text-center">
                  <span className="text-[#888888] text-sm">Carbon Grade</span>
                  <p 
                    className="text-5xl font-bold mt-2"
                    style={{ color: getScoreColor(emissionData.carbon_score) }}
                  >
                    {emissionData.carbon_score}
                  </p>
                  <p className="text-[#666666] text-sm mt-2">Rating</p>
                </div>
                <div className="bg-[#1a1a1a] rounded-xl p-6 border border-[#333333] text-center">
                  <span className="text-[#888888] text-sm">Score Value</span>
                  <p className="text-5xl font-bold text-white mt-2">
                    {emissionData.carbon_score_value}
                  </p>
                  <p className="text-[#666666] text-sm mt-2">out of 100</p>
                </div>
                <div className="bg-[#1a1a1a] rounded-xl p-6 border border-[#333333] text-center">
                  <span className="text-[#888888] text-sm">Status</span>
                  <div className="mt-2">
                    {emissionData.carbon_score_value >= 80 ? (
                      <CheckCircle size={48} className="text-green-500 mx-auto" />
                    ) : emissionData.carbon_score_value >= 60 ? (
                      <AlertCircle size={48} className="text-yellow-500 mx-auto" />
                    ) : (
                      <AlertCircle size={48} className="text-red-500 mx-auto" />
                    )}
                  </div>
                  <p className="text-[#666666] text-sm mt-2">
                    {emissionData.carbon_score_value >= 80 ? "Excellent" : 
                     emissionData.carbon_score_value >= 60 ? "Average" : "Needs Improvement"}
                  </p>
                </div>
              </div>
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Pie Breakdown Chart - Model 1 */}
              <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
                <PieBreakdown 
                  data={emissionData}
                  model1Status={(modelStatus?.emissions_model as any) || "disconnected"}
                />
              </div>

              {/* Trend Chart - Model 3 */}
              <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
                <TrendChart
                  history={[]}
                  forecast={[]}
                  modelUsed="Model 3"
                  currentMonth={{
                    electricity_co2: emissionData.electricity_co2,
                    fuel_co2: emissionData.fuel_co2,
                    total_co2: emissionData.total_co2
                  }}
                  model3Status={(modelStatus?.trend_model as any) || "disconnected"}
                />
              </div>
            </div>

            {/* Download PDF Button */}
            <div className="flex justify-center">
              <button
                onClick={downloadPDF}
                disabled={reportGenerating || !backendConnected}
                className="flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-[#c8f07a] to-[#a8d05a] text-black rounded-xl font-bold text-lg hover:shadow-lg hover:shadow-[#c8f07a]/20 transition-all disabled:opacity-50"
              >
                {reportGenerating ? (
                  <>
                    <Activity className="animate-spin" size={20} />
                    Generating PDF...
                  </>
                ) : (
                  <>
                    <Download size={20} />
                    Download Complete Report (PDF)
                  </>
                )}
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
