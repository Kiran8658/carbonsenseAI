import React, { useState, useEffect } from "react";
import axios from "axios";
import Sidebar from "../components/Sidebar";
import { 
  Activity, 
  Zap, 
  Fuel, 
  AlertCircle, 
  Lightbulb, 
  TrendingUp,
  TrendingDown,
  Calculator,
  BarChart3,
  Leaf,
  Sparkles
} from "lucide-react";

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

export default function DashboardPage() {
  const [electricity, setElectricity] = useState("");
  const [fuel, setFuel] = useState("");
  const [emissionData, setEmissionData] = useState<EmissionData | null>(null);
  const [modelStatus, setModelStatus] = useState<ModelStatus | null>(null);
  const [backendConnected, setBackendConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiInsights, setAiInsights] = useState<any>(null);
  const [aiSuggestions, setAiSuggestions] = useState<any[]>([]);

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
      const response = await axios.post("http://localhost:8000/api/calculate", {
        electricity_kwh: parseFloat(electricity),
        fuel_litres: parseFloat(fuel),
      });
      if (response.data?.data) {
        setEmissionData(response.data.data);
        fetchAISuggestions(response.data.data);
      }
    } catch (error) {
      console.error("Auto-refresh error:", error);
    }
  };

  const checkBackendStatus = async () => {
    try {
      const response = await axios.get("http://localhost:8000/health", { timeout: 3000 });
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
      alert("Backend is not connected! Please start the backend server on port 8000.");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post("http://localhost:8000/api/calculate", {
        electricity_kwh: parseFloat(electricity),
        fuel_litres: parseFloat(fuel),
      });
      
      if (response.data && response.data.data) {
        setEmissionData(response.data.data);
        // Automatically fetch AI suggestions after calculation
        fetchAISuggestions(response.data.data);
      }
    } catch (error) {
      console.error("Error calculating emissions:", error);
      alert("Failed to calculate. Please check backend connection.");
    } finally {
      setLoading(false);
    }
  };

  const fetchAISuggestions = async (data: EmissionData) => {
    try {
      const response = await axios.post("http://localhost:8000/api/ai-suggestions", {
        electricity_kwh: parseFloat(electricity),
        fuel_litres: parseFloat(fuel),
        total_co2: data.total_co2,
        business_type: "MSME"
      });
      
      if (response.data && response.data.suggestions) {
        setAiSuggestions(response.data.suggestions);
      }
    } catch (error) {
      console.error("Error fetching AI suggestions:", error);
    }
  };

  const generateAIInsights = async () => {
    if (!emissionData || !backendConnected) {
      alert("Please calculate emissions first and ensure backend is connected.");
      return;
    }
    
    try {
      setAiLoading(true);
      const response = await axios.post("http://localhost:8000/api/reports/ai-insights", {
        emission_data: emissionData,
        suggestions: aiSuggestions,
        history: [],
        forecast: [],
      });
      
      if (response.data.success) {
        setAiInsights(response.data);
      }
    } catch (error) {
      console.error("Error generating AI insights:", error);
    } finally {
      setAiLoading(false);
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

  const getModelStatusColor = (status: string) => {
    switch (status) {
      case "loaded": return "bg-green-500";
      case "loading": return "bg-yellow-500";
      case "error": return "bg-red-500";
      default: return "bg-gray-500";
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
              <h1 className="text-4xl font-bold text-white tracking-tight">Dashboard</h1>
              <div className="flex items-center gap-2 px-3 py-1 bg-[#c8f07a]/20 rounded-full border border-[#c8f07a]/30">
                <Sparkles size={14} className="text-[#c8f07a]" />
                <span className="text-xs font-semibold text-[#c8f07a]">3 AI Models</span>
              </div>
            </div>
            <p className="text-[#888888]">
              Real-time carbon emissions tracking with AI-powered insights
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${backendConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            <span className={`text-sm ${backendConnected ? 'text-green-400' : 'text-red-400'}`}>
              {backendConnected ? 'Backend Connected' : 'Backend Disconnected'}
            </span>
          </div>
        </div>

        {/* AI Model Status */}
        {modelStatus && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-[#111111] border border-[#222222] rounded-xl p-4 flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${getModelStatusColor(modelStatus.emissions_model)}`} />
              <div>
                <p className="text-white font-medium text-sm">Emissions Predictor</p>
                <p className="text-[#666666] text-xs">Model 1 • {modelStatus.emissions_model}</p>
              </div>
            </div>
            <div className="bg-[#111111] border border-[#222222] rounded-xl p-4 flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${getModelStatusColor(modelStatus.scorer_model)}`} />
              <div>
                <p className="text-white font-medium text-sm">Carbon Scorer</p>
                <p className="text-[#666666] text-xs">Model 2 • {modelStatus.scorer_model}</p>
              </div>
            </div>
            <div className="bg-[#111111] border border-[#222222] rounded-xl p-4 flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${getModelStatusColor(modelStatus.trend_model)}`} />
              <div>
                <p className="text-white font-medium text-sm">Trend Forecaster</p>
                <p className="text-[#666666] text-xs">Model 3 • {modelStatus.trend_model}</p>
              </div>
            </div>
          </div>
        )}

        {/* Input Form */}
        <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
          <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <Calculator size={20} className="text-[#c8f07a]" />
            Data Input
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
                    Processing...
                  </>
                ) : (
                  <>
                    <Calculator size={18} />
                    Calculate Emissions
                  </>
                )}
              </button>
            </div>
          </form>

          <div className="mt-6 p-4 bg-[#1a1a1a] rounded-lg border border-[#333333]">
            <p className="text-xs text-[#666666] font-mono">
              Formula: Electricity × 0.82 kg/kWh + Fuel × 2.3 kg/Litre
            </p>
          </div>
        </div>

        {/* Results */}
        {emissionData && (
          <>
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-[#c8f07a]/20 rounded-lg flex items-center justify-center">
                    <Activity size={20} className="text-[#c8f07a]" />
                  </div>
                  <span className="text-[#888888] text-sm">Total Emissions</span>
                </div>
                <p className="text-3xl font-bold text-white">{emissionData.total_co2.toFixed(1)} kg</p>
                <p className="text-[#666666] text-sm mt-2">CO₂ equivalent</p>
              </div>

              <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                    <Zap size={20} className="text-blue-400" />
                  </div>
                  <span className="text-[#888888] text-sm">Electricity</span>
                </div>
                <p className="text-3xl font-bold text-white">{emissionData.electricity_co2.toFixed(1)} kg</p>
                <p className="text-[#666666] text-sm mt-2">{emissionData.breakdown_percentage.electricity}% of total</p>
              </div>

              <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-orange-500/20 rounded-lg flex items-center justify-center">
                    <Fuel size={20} className="text-orange-400" />
                  </div>
                  <span className="text-[#888888] text-sm">Fuel</span>
                </div>
                <p className="text-3xl font-bold text-white">{emissionData.fuel_co2.toFixed(1)} kg</p>
                <p className="text-[#666666] text-sm mt-2">{emissionData.breakdown_percentage.fuel}% of total</p>
              </div>

              <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                    <Leaf size={20} className="text-purple-400" />
                  </div>
                  <span className="text-[#888888] text-sm">Carbon Score</span>
                </div>
                <p className="text-3xl font-bold" style={{ color: getScoreColor(emissionData.carbon_score) }}>
                  {emissionData.carbon_score}
                </p>
                <p className="text-[#666666] text-sm mt-2">{emissionData.carbon_score_value}/100</p>
              </div>
            </div>

            {/* AI Suggestions Section */}
            {aiSuggestions.length > 0 && (
              <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                    <BarChart3 size={20} className="text-blue-400" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-white">AI Suggestions</h2>
                    <p className="text-[#888888] text-sm">Personalized recommendations from AI Model 1</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {aiSuggestions.slice(0, 4).map((suggestion: any, index: number) => (
                    <div key={index} className="bg-[#1a1a1a] rounded-xl p-4 border border-[#333333]">
                      <div className="flex items-start gap-3">
                        <div className={`w-2 h-2 rounded-full mt-2 ${
                          suggestion.priority === "high" ? "bg-red-500" :
                          suggestion.priority === "medium" ? "bg-yellow-500" : "bg-green-500"
                        }`} />
                        <div className="flex-1">
                          <h3 className="text-white font-semibold mb-1">{suggestion.title}</h3>
                          <p className="text-[#888888] text-sm">{suggestion.description}</p>
                          <div className="flex items-center gap-2 mt-2">
                            <span className="text-xs text-[#c8f07a] font-mono">
                              Save {suggestion.savings_percentage}%
                            </span>
                            <span className="text-xs text-[#666666]">•</span>
                            <span className="text-xs text-[#888888]">{suggestion.category}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* AI Insights Button */}
            <div className="flex justify-end">
              <button
                onClick={generateAIInsights}
                disabled={aiLoading || !backendConnected}
                className="flex items-center gap-2 px-6 py-3 bg-[#c8f07a] text-black rounded-lg font-medium hover:bg-[#d4f5a0] transition-colors disabled:opacity-50"
              >
                {aiLoading ? (
                  <Activity className="animate-spin" size={18} />
                ) : (
                  <Lightbulb size={18} />
                )}
                {aiLoading ? "Generating AI Insights..." : "Generate AI Insights"}
              </button>
            </div>

            {/* AI Insights Section */}
            {aiInsights && (
              <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 bg-[#c8f07a]/20 rounded-lg flex items-center justify-center">
                    <Lightbulb size={20} className="text-[#c8f07a]" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-white">AI-Powered Insights</h2>
                    <p className="text-[#888888] text-sm">
                      Powered by {aiInsights.api_used === "gemini" ? "Gemini" : aiInsights.api_used === "openai" ? "OpenAI" : "AI Models"}
                      {aiInsights.fallback && " (Fallback)"}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {aiInsights.insights?.map((insight: any, index: number) => (
                    <div key={index} className="bg-[#1a1a1a] rounded-xl p-4 border border-[#333333]">
                      <div className="flex items-start gap-3">
                        <div className={`w-2 h-2 rounded-full mt-2 ${
                          insight.priority === "high" ? "bg-red-500" :
                          insight.priority === "medium" ? "bg-yellow-500" : "bg-green-500"
                        }`} />
                        <div className="flex-1">
                          <span className="text-xs text-[#c8f07a] font-mono">{insight.model}</span>
                          <h3 className="text-white font-semibold mb-1 mt-1">{insight.title}</h3>
                          <p className="text-[#888888] text-sm">{insight.content}</p>
                          {insight.action && (
                            <p className="text-[#c8f07a] text-sm mt-2">→ {insight.action}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Summary */}
                {aiInsights.summary && (
                  <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-[#1a1a1a] rounded-xl p-4 border border-[#333333]">
                      <span className="text-[#888888] text-sm">Total Emissions</span>
                      <p className="text-xl font-bold text-white">{aiInsights.summary.total_emissions?.toFixed(1)} kg</p>
                    </div>
                    <div className="bg-[#1a1a1a] rounded-xl p-4 border border-[#333333]">
                      <span className="text-[#888888] text-sm">Carbon Score</span>
                      <p className="text-xl font-bold text-white">{aiInsights.summary.carbon_score}</p>
                    </div>
                    <div className="bg-[#1a1a1a] rounded-xl p-4 border border-[#333333]">
                      <span className="text-[#888888] text-sm">Improvement</span>
                      <p className="text-xl font-bold text-[#c8f07a]">{aiInsights.summary.improvement_potential}</p>
                    </div>
                    <div className="bg-[#1a1a1a] rounded-xl p-4 border border-[#333333]">
                      <span className="text-[#888888] text-sm">Priority</span>
                      <p className={`text-xl font-bold ${
                        aiInsights.summary.priority_level === "Critical" ? "text-red-500" :
                        aiInsights.summary.priority_level === "High" ? "text-orange-500" :
                        aiInsights.summary.priority_level === "Medium" ? "text-yellow-500" : "text-green-500"
                      }`}>
                        {aiInsights.summary.priority_level}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
