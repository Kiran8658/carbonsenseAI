import React, { useState, useEffect } from "react";
import axios from "axios";
import Sidebar from "../components/Sidebar";
import { 
  FileText, 
  Download, 
  Activity, 
  Zap, 
  Fuel, 
  Lightbulb,
  Calculator,
  BarChart3,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Sparkles,
  Bot
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

interface AIInsight {
  model: string;
  type: string;
  title: string;
  content: string;
  action?: string;
  priority: string;
}

export default function ReportsPage() {
  const [electricity, setElectricity] = useState("");
  const [fuel, setFuel] = useState("");
  const [emissionData, setEmissionData] = useState<EmissionData | null>(null);
  const [modelStatus, setModelStatus] = useState<ModelStatus | null>(null);
  const [backendConnected, setBackendConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiInsights, setAiInsights] = useState<any>(null);
  const [aiSuggestions, setAiSuggestions] = useState<any[]>([]);
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
      const response = await axios.post("http://localhost:8000/api/calculate", {
        electricity_kwh: parseFloat(electricity),
        fuel_litres: parseFloat(fuel),
      });
      if (response.data?.data) {
        setEmissionData(response.data.data);
        fetchAllAIData(response.data.data);
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
        // Automatically fetch all AI data
        fetchAllAIData(response.data.data);
      }
    } catch (error) {
      console.error("Error calculating emissions:", error);
      alert("Failed to calculate. Please check backend connection.");
    } finally {
      setLoading(false);
    }
  };

  const fetchAllAIData = async (data: EmissionData) => {
    try {
      // Fetch AI Suggestions
      const suggestionsResponse = await axios.post("http://localhost:8000/api/ai-suggestions", {
        electricity_kwh: parseFloat(electricity),
        fuel_litres: parseFloat(fuel),
        total_co2: data.total_co2,
        business_type: "MSME"
      });
      
      if (suggestionsResponse.data && suggestionsResponse.data.suggestions) {
        setAiSuggestions(suggestionsResponse.data.suggestions);
      }

      // Fetch AI Insights automatically
      const insightsResponse = await axios.post("http://localhost:8000/api/reports/ai-insights", {
        emission_data: data,
        suggestions: suggestionsResponse.data?.suggestions || [],
        history: [],
        forecast: [],
      });
      
      if (insightsResponse.data.success) {
        setAiInsights(insightsResponse.data);
      }
    } catch (error) {
      console.error("Error fetching AI data:", error);
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

  const downloadPDF = async () => {
    if (!emissionData || !backendConnected) {
      alert("Please calculate emissions first and ensure backend is connected.");
      return;
    }

    setReportGenerating(true);
    try {
      const response = await axios.post("http://localhost:8000/api/reports/generate", {
        emission_data: emissionData,
        ai_insights: aiInsights,
        suggestions: aiSuggestions,
      }, { responseType: 'blob' });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `carbon-report-${new Date().toISOString().split('T')[0]}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading PDF:", error);
      alert("Failed to download PDF. Please try again.");
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
                    <Sparkles size={18} />
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

            {/* Model 3: AI Suggestions Output */}
            {aiSuggestions.length > 0 && (
              <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                    <Bot size={20} className="text-green-400" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-white">Model 3: AI Suggestions Engine</h2>
                    <p className="text-[#888888] text-sm">Personalized reduction strategies</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {aiSuggestions.map((suggestion: any, index: number) => (
                    <div key={index} className="bg-[#1a1a1a] rounded-xl p-4 border border-[#333333]">
                      <div className="flex items-start gap-3">
                        <div className={`w-2 h-2 rounded-full mt-2 ${
                          suggestion.priority === "high" ? "bg-red-500" :
                          suggestion.priority === "medium" ? "bg-yellow-500" : "bg-green-500"
                        }`} />
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="text-white font-semibold">{suggestion.title}</h3>
                            <span className="text-xs px-2 py-0.5 bg-[#c8f07a]/20 text-[#c8f07a] rounded-full">
                              {suggestion.category}
                            </span>
                          </div>
                          <p className="text-[#888888] text-sm">{suggestion.description}</p>
                          <div className="flex items-center gap-3 mt-3">
                            <span className="text-xs text-[#c8f07a] font-mono bg-[#c8f07a]/10 px-2 py-1 rounded">
                              Save {suggestion.savings_percentage}%
                            </span>
                            <span className="text-xs text-[#666666]">
                              Impact: {suggestion.impact}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* AI Insights with Recommendations */}
            <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-[#c8f07a]/20 rounded-lg flex items-center justify-center">
                    <Lightbulb size={20} className="text-[#c8f07a]" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-white">AI-Powered Insights & Recommendations</h2>
                    <p className="text-[#888888] text-sm">
                      {aiInsights ? `Powered by ${aiInsights.api_used === "gemini" ? "Gemini" : aiInsights.api_used === "openai" ? "OpenAI" : "AI Models"}` : "Click to generate insights"}
                    </p>
                  </div>
                </div>
                <button
                  onClick={generateAIInsights}
                  disabled={aiLoading || !backendConnected}
                  className="flex items-center gap-2 px-4 py-2 bg-[#c8f07a] text-black rounded-lg font-medium hover:bg-[#d4f5a0] transition-colors disabled:opacity-50"
                >
                  {aiLoading ? (
                    <Activity className="animate-spin" size={16} />
                  ) : (
                    <Sparkles size={16} />
                  )}
                  {aiLoading ? "Generating..." : aiInsights ? "Regenerate Insights" : "Get Recommendations"}
                </button>
              </div>

              {aiInsights ? (
                <>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
                    {aiInsights.insights?.map((insight: AIInsight, index: number) => (
                      <div key={index} className="bg-[#1a1a1a] rounded-xl p-4 border border-[#333333]">
                        <div className="flex items-start gap-3">
                          <div className={`w-2 h-2 rounded-full mt-2 ${
                            insight.priority === "high" ? "bg-red-500" :
                            insight.priority === "medium" ? "bg-yellow-500" : "bg-green-500"
                          }`} />
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-xs text-[#c8f07a] font-mono">{insight.model}</span>
                              <span className="text-xs text-[#666666]">• {insight.type}</span>
                            </div>
                            <h3 className="text-white font-semibold mb-1">{insight.title}</h3>
                            <p className="text-[#888888] text-sm">{insight.content}</p>
                            {insight.action && (
                              <div className="mt-3 p-2 bg-[#c8f07a]/10 rounded-lg border border-[#c8f07a]/20">
                                <p className="text-[#c8f07a] text-sm">→ {insight.action}</p>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Summary */}
                  {aiInsights.summary && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
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
                </>
              ) : (
                <div className="text-center py-12 text-[#666666]">
                  <Lightbulb size={48} className="mx-auto mb-4 opacity-50" />
                  <p>Click "Get Recommendations" to generate AI insights from all 3 models</p>
                </div>
              )}
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
