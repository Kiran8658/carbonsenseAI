import React, { useState, useEffect } from "react";
import axios from "axios";
import Sidebar from "../components/Sidebar";
import { BarChart3, TrendingUp, TrendingDown, Activity, Lightbulb, Zap, Fuel, Calculator } from "lucide-react";

interface EmissionData {
  total_co2: number;
  electricity_co2: number;
  fuel_co2: number;
  carbon_score: string;
  carbon_score_value: number;
  breakdown_percentage: { electricity: number; fuel: number };
}

interface TrendData { month: string; emissions: number; forecast?: number; }

export default function AnalyticsPage() {
  const [electricity, setElectricity] = useState("");
  const [fuel, setFuel] = useState("");
  const [emissionData, setEmissionData] = useState<EmissionData | null>(null);
  const [trendData, setTrendData] = useState<TrendData[]>([]);
  const [backendConnected, setBackendConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiInsights, setAiInsights] = useState<any>(null);

  useEffect(() => {
    checkBackendStatus();
    fetchTrendData();
    const interval = setInterval(checkBackendStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const checkBackendStatus = async () => {
    try {
      const response = await axios.get("http://localhost:8000/health", { timeout: 3000 });
      setBackendConnected(!!response.data);
    } catch (error) { setBackendConnected(false); }
  };

  const fetchTrendData = async () => {
    try {
      const response = await axios.get("http://localhost:8000/api/calculator/history");
      if (response.data?.history) {
        setTrendData(response.data.history.map((h: any) => ({ month: h.date.slice(0, 7), emissions: h.total_co2 })));
      }
    } catch (error) {
      setTrendData([
        { month: "Jan", emissions: 1200, forecast: 1180 }, { month: "Feb", emissions: 1150, forecast: 1130 },
        { month: "Mar", emissions: 1300, forecast: 1250 }, { month: "Apr", emissions: 1250, forecast: 1200 },
        { month: "May", emissions: 1100, forecast: 1080 }, { month: "Jun", emissions: 1050, forecast: 1000 },
      ]);
    }
  };

  const handleCalculate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!electricity || !fuel) return;
    if (!backendConnected) { alert("Backend not connected! Start server on port 8000."); return; }

    setLoading(true);
    try {
      const response = await axios.post("http://localhost:8000/api/calculate", {
        electricity_kwh: parseFloat(electricity), fuel_litres: parseFloat(fuel),
      });
      if (response.data?.data) setEmissionData(response.data.data);
    } catch (error) { alert("Failed to calculate. Check backend connection."); }
    finally { setLoading(false); }
  };

  const generateAIInsights = async () => {
    if (!emissionData || !backendConnected) return;
    setAiLoading(true);
    try {
      const response = await axios.post("http://localhost:8000/api/reports/ai-insights", {
        emission_data: emissionData, suggestions: [],
        history: trendData.map(t => ({ date: t.month, total_co2: t.emissions })),
        forecast: trendData.map(t => t.forecast || t.emissions),
      });
      if (response.data.success) setAiInsights(response.data);
    } catch (error) { console.error(error); }
    finally { setAiLoading(false); }
  };

  const trendPercentage = trendData.length >= 2
    ? ((trendData[trendData.length - 1].emissions - trendData[0].emissions) / trendData[0].emissions * 100) : 0;
  const isImproving = trendPercentage < 0;

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      <Sidebar />
      <main className="ml-64 p-8 space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white tracking-tight mb-2">Analytics</h1>
            <p className="text-[#888888]">AI-powered trend forecasting and emission analytics</p>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${backendConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            <span className={`text-sm ${backendConnected ? 'text-green-400' : 'text-red-400'}`}>
              {backendConnected ? 'Backend Connected' : 'Backend Disconnected'}
            </span>
          </div>
        </div>

        <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
          <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <Calculator size={20} className="text-[#c8f07a]" /> Data Input
          </h2>
          <form onSubmit={handleCalculate} className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-[#888888] mb-2">
                <Zap size={16} className="text-blue-400" /> Electricity (kWh/month)
              </label>
              <input type="number" value={electricity} onChange={(e) => setElectricity(e.target.value)}
                placeholder="e.g., 500" className="w-full bg-[#1a1a1a] border border-[#333333] rounded-lg px-4 py-3 text-white placeholder-[#666666] focus:outline-none focus:border-[#c8f07a]" required min="0" step="0.1" />
            </div>
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-[#888888] mb-2">
                <Fuel size={16} className="text-orange-400" /> Fuel (Litres/month)
              </label>
              <input type="number" value={fuel} onChange={(e) => setFuel(e.target.value)}
                placeholder="e.g., 100" className="w-full bg-[#1a1a1a] border border-[#333333] rounded-lg px-4 py-3 text-white placeholder-[#666666] focus:outline-none focus:border-[#c8f07a]" required min="0" step="0.1" />
            </div>
            <div className="flex items-end">
              <button type="submit" disabled={loading || !electricity || !fuel || !backendConnected}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-[#c8f07a] text-black rounded-lg font-medium hover:bg-[#d4f5a0] transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                {loading ? <><Activity className="animate-spin" size={18} /> Processing...</> : <><Calculator size={18} /> Calculate & Analyze</>}
              </button>
            </div>
          </form>
        </div>

        {emissionData && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-[#c8f07a]/20 rounded-lg flex items-center justify-center"><BarChart3 size={20} className="text-[#c8f07a]" /></div>
                  <span className="text-[#888888] text-sm">Current Emissions</span>
                </div>
                <p className="text-3xl font-bold text-white">{emissionData.total_co2.toFixed(1)} kg</p>
                <p className="text-[#666666] text-sm mt-2">Monthly CO₂</p>
              </div>
              <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className={`w-10 h-10 ${isImproving ? "bg-green-500/20" : "bg-red-500/20"} rounded-lg flex items-center justify-center`}>
                    {isImproving ? <TrendingDown size={20} className="text-green-400" /> : <TrendingUp size={20} className="text-red-400" />}
                  </div>
                  <span className="text-[#888888] text-sm">6-Month Trend</span>
                </div>
                <p className={`text-3xl font-bold ${isImproving ? "text-green-400" : "text-red-400"}`}>{Math.abs(trendPercentage).toFixed(1)}%</p>
                <p className="text-[#666666] text-sm mt-2">{isImproving ? "Improving" : "Increasing"}</p>
              </div>
              <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center"><Activity size={20} className="text-blue-400" /></div>
                  <span className="text-[#888888] text-sm">AI Score</span>
                </div>
                <p className="text-3xl font-bold text-white">{emissionData.carbon_score_value}/100</p>
                <p className="text-[#666666] text-sm mt-2">{emissionData.carbon_score}</p>
              </div>
              <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center"><TrendingUp size={20} className="text-purple-400" /></div>
                  <span className="text-[#888888] text-sm">Forecast</span>
                </div>
                <p className="text-3xl font-bold text-white">{trendData.length > 0 ? trendData[trendData.length - 1].forecast?.toFixed(0) || "--" : "--"} kg</p>
                <p className="text-[#666666] text-sm mt-2">AI Prediction</p>
              </div>
            </div>

            <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4">Emission Trends</h3>
              <div className="h-64 flex items-end gap-2">
                {trendData.map((data, index) => {
                  const maxEmissions = Math.max(...trendData.map(d => d.emissions));
                  const height = (data.emissions / maxEmissions) * 100;
                  return (
                    <div key={index} className="flex-1 flex flex-col items-center gap-1">
                      <div className="w-full bg-[#c8f07a]/80 rounded-t-sm min-h-[4px]" style={{ height: `${height}%` }} />
                      <span className="text-xs text-[#666666]">{data.month}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="flex justify-end">
              <button onClick={generateAIInsights} disabled={aiLoading || !backendConnected}
                className="flex items-center gap-2 px-6 py-3 bg-[#c8f07a] text-black rounded-lg font-medium hover:bg-[#d4f5a0] transition-colors disabled:opacity-50">
                {aiLoading ? <Activity className="animate-spin" size={18} /> : <Lightbulb size={18} />}
                {aiLoading ? "Generating..." : "Generate AI Insights"}
              </button>
            </div>

            {aiInsights && (
              <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 bg-[#c8f07a]/20 rounded-lg flex items-center justify-center"><Lightbulb size={20} className="text-[#c8f07a]" /></div>
                  <div>
                    <h2 className="text-xl font-bold text-white">AI-Powered Insights</h2>
                    <p className="text-[#888888] text-sm">Powered by {aiInsights.api_used === "gemini" ? "Gemini" : aiInsights.api_used === "openai" ? "OpenAI" : "AI Models"}{aiInsights.fallback && " (Fallback)"}</p>
                  </div>
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {aiInsights.insights?.map((insight: any, index: number) => (
                    <div key={index} className="bg-[#1a1a1a] rounded-xl p-4 border border-[#333333]">
                      <div className="flex items-start gap-3">
                        <div className={`w-2 h-2 rounded-full mt-2 ${insight.priority === "high" ? "bg-red-500" : insight.priority === "medium" ? "bg-yellow-500" : "bg-green-500"}`} />
                        <div className="flex-1">
                          <span className="text-xs text-[#c8f07a] font-mono">{insight.model}</span>
                          <h3 className="text-white font-semibold mb-1 mt-1">{insight.title}</h3>
                          <p className="text-[#888888] text-sm">{insight.content}</p>
                          {insight.action && <p className="text-[#c8f07a] text-sm mt-2">→ {insight.action}</p>}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                {aiInsights.summary && (
                  <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-[#1a1a1a] rounded-xl p-4 border border-[#333333]"><span className="text-[#888888] text-sm">Total Emissions</span><p className="text-xl font-bold text-white">{aiInsights.summary.total_emissions?.toFixed(1)} kg</p></div>
                    <div className="bg-[#1a1a1a] rounded-xl p-4 border border-[#333333]"><span className="text-[#888888] text-sm">Carbon Score</span><p className="text-xl font-bold text-white">{aiInsights.summary.carbon_score}</p></div>
                    <div className="bg-[#1a1a1a] rounded-xl p-4 border border-[#333333]"><span className="text-[#888888] text-sm">Improvement</span><p className="text-xl font-bold text-[#c8f07a]">{aiInsights.summary.improvement_potential}</p></div>
                    <div className="bg-[#1a1a1a] rounded-xl p-4 border border-[#333333]"><span className="text-[#888888] text-sm">Priority</span><p className={`text-xl font-bold ${aiInsights.summary.priority_level === "Critical" ? "text-red-500" : aiInsights.summary.priority_level === "High" ? "text-orange-500" : aiInsights.summary.priority_level === "Medium" ? "text-yellow-500" : "text-green-500"}`}>{aiInsights.summary.priority_level}</p></div>
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
