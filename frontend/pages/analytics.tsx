import React, { useState, useEffect } from "react";
import axios from "axios";
import Sidebar from "../components/Sidebar";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, Area, AreaChart, Legend, ComposedChart
} from "recharts";
import { BarChart3, TrendingUp, TrendingDown, Activity, Zap, Fuel, Calculator, Lightbulb } from "lucide-react";

const API_URL = typeof window !== "undefined"
  ? `http://${window.location.hostname}:8005`
  : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8005");

interface TrendPoint { month: string; emissions?: number; forecast?: number; electricity?: number; fuel?: number; }

const DEMO_DATA: TrendPoint[] = [
  { month: "Aug", emissions: 880, forecast: undefined, electricity: 580, fuel: 300 },
  { month: "Sep", emissions: 830, forecast: undefined, electricity: 540, fuel: 290 },
  { month: "Oct", emissions: 760, forecast: undefined, electricity: 490, fuel: 270 },
  { month: "Nov", emissions: 700, forecast: undefined, electricity: 460, fuel: 240 },
  { month: "Dec", emissions: 660, forecast: undefined, electricity: 430, fuel: 230 },
  { month: "Jan", emissions: 640, forecast: 628, electricity: 410, fuel: 230 },
  { month: "Feb", emissions: undefined, forecast: 620, electricity: undefined, fuel: undefined },
  { month: "Mar", emissions: undefined, forecast: 612, electricity: undefined, fuel: undefined },
  { month: "Apr", emissions: undefined, forecast: 608, electricity: undefined, fuel: undefined },
  { month: "May", emissions: undefined, forecast: 605, electricity: undefined, fuel: undefined },
  { month: "Jun", emissions: undefined, forecast: 604, electricity: undefined, fuel: undefined },
  { month: "Jul", emissions: undefined, forecast: 603, electricity: undefined, fuel: undefined },
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "#111",
      border: "1px solid rgba(34,197,94,0.25)",
      borderRadius: 10,
      padding: "10px 14px",
      fontSize: 12,
    }}>
      <p style={{ color: "#ccc", marginBottom: 6, fontWeight: 600 }}>{label}</p>
      {payload.map((p: any) => (
        <p key={p.name} style={{ color: p.color, margin: "2px 0" }}>
          {p.name}: <b>{p.value?.toFixed(0)} kg</b>
        </p>
      ))}
    </div>
  );
};

export default function AnalyticsPage() {
  const [trendData, setTrendData] = useState<TrendPoint[]>(DEMO_DATA);
  const [backendConnected, setBackendConnected] = useState(false);
  const [electricity, setElectricity] = useState("");
  const [fuel, setFuel] = useState("");
  const [loading, setLoading] = useState(false);
  const [currentCO2, setCurrentCO2] = useState<number | null>(null);
  const [currentScore, setCurrentScore] = useState<string>("");
  const [aiInsights, setAiInsights] = useState<any>(null);
  const [aiLoading, setAiLoading] = useState(false);

  useEffect(() => {
    checkBackend();
    fetchHistory();
    const interval = setInterval(checkBackend, 5000);
    return () => clearInterval(interval);
  }, []);

  const checkBackend = async () => {
    try {
      await axios.get(`${API_URL}/health`, { timeout: 3000 });
      setBackendConnected(true);
    } catch { setBackendConnected(false); }
  };

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API_URL}/api/history`);
      if (res.data?.history?.length > 0) {
        const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        
        // Map historical data
        const mapped = res.data.history.map((h: any) => ({
          month: h.month ? h.month.split(" ")[0] : "?", // Extract just the month name
          emissions: h.total_co2 || 0,
          electricity: h.electricity_co2,
          fuel: h.fuel_co2,
          forecast: undefined, // Will be filled by forecast data
        }));

        // Add forecast data if available
        if (res.data?.forecast && Array.isArray(res.data.forecast) && res.data.forecast.length > 0) {
          // Get the last month from history to calculate next months
          const lastHistoryMonth = mapped[mapped.length - 1]?.month;
          const lastMonthIndex = monthNames.indexOf(lastHistoryMonth);
          
          // Add forecast months
          res.data.forecast.slice(0, 6).forEach((forecastValue: number, index: number) => {
            const nextMonthIndex = (lastMonthIndex + index + 1) % 12;
            const forecastMonth = monthNames[nextMonthIndex];
            
            // Check if this month already exists in history
            const existingIndex = mapped.findIndex((d: TrendPoint) => d.month === forecastMonth);
            if (existingIndex >= 0) {
              mapped[existingIndex].forecast = forecastValue;
            } else {
              // Add new forecast month
              mapped.push({
                month: forecastMonth,
                emissions: undefined,
                electricity: undefined,
                fuel: undefined,
                forecast: forecastValue,
              });
            }
          });
        }

        setTrendData(mapped.length >= 2 ? mapped : DEMO_DATA);
      }
    } catch { /* keep demo data */ }
  };

  const handleCalculate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!electricity || !fuel || !backendConnected) return;
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/api/calculate`, {
        electricity_kwh: parseFloat(electricity), fuel_litres: parseFloat(fuel),
      });
      if (res.data?.data) {
        const d = res.data.data;
        setCurrentCO2(d.total_co2);
        setCurrentScore(d.carbon_score);
        // Add current month to chart
        const now = new Date();
        const label = now.toLocaleString("default", { month: "short" });
        const updated = [...trendData.filter(t => t.month !== label), {
          month: label,
          emissions: d.total_co2,
          electricity: d.electricity_co2,
          fuel: d.fuel_co2,
        }];
        setTrendData(updated);
      }
    } catch { alert("Calculation failed. Check backend."); }
    finally { setLoading(false); }
  };

  const generateInsights = async () => {
    if (!currentCO2 || !backendConnected) return;
    setAiLoading(true);
    try {
      const res = await axios.post(`${API_URL}/api/reports/ai-insights`, {
        emission_data: { total_co2: currentCO2, carbon_score: currentScore },
        suggestions: [], history: trendData.map(t => ({ date: t.month, total_co2: t.emissions })),
        forecast: [],
      });
      if (res.data.success) setAiInsights(res.data);
    } catch (e) { console.error(e); }
    finally { setAiLoading(false); }
  };

  const historicalData = trendData.filter((d: TrendPoint) => d.emissions !== undefined);
  const trendPct = historicalData.length >= 2
    ? ((historicalData[historicalData.length - 1].emissions! - historicalData[0].emissions!) / historicalData[0].emissions! * 100)
    : 0;
  const improving = trendPct < 0;
  const avgEmissions = historicalData.length > 0 
    ? historicalData.reduce((a, d) => a + (d.emissions || 0), 0) / historicalData.length
    : 0;
  const maxEmission = historicalData.length > 0 ? Math.max(...historicalData.map(d => d.emissions || 0)) : 0;
  const minEmission = historicalData.length > 0 ? Math.min(...historicalData.map(d => d.emissions || 0)) : 0;

  return (
    <div className="min-h-screen" style={{ background: "var(--bg-primary)" }}>
      <Sidebar />
      <main className="ml-64 p-8 space-y-8">

        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 style={{ fontSize: 32, fontWeight: 800, fontFamily: "Syne", color: "var(--text-primary)" }}>Analytics</h1>
              <span style={{ fontSize: 11, color: "#22c55e", fontFamily: "DM Mono", background: "rgba(34,197,94,0.1)", border: "1px solid rgba(34,197,94,0.2)", borderRadius: 6, padding: "2px 8px" }}>
                TREND FORECASTING
              </span>
            </div>
            <p style={{ color: "var(--text-muted)", fontSize: 13 }}>AI-powered emission trend analysis with ML forecasting</p>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-2.5 h-2.5 rounded-full ${backendConnected ? "pulse-dot" : ""}`} style={{ background: backendConnected ? "#22c55e" : "#ef4444" }} />
            <span style={{ fontSize: 13, color: backendConnected ? "#22c55e" : "#ef4444" }}>
              {backendConnected ? "Backend ✓" : "Backend ✗"}
            </span>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-4 gap-4">
          {[
            { label: "Avg Monthly", value: `${avgEmissions.toFixed(0)} kg`, icon: Activity, color: "#22c55e" },
            { label: "Highest", value: `${maxEmission.toFixed(0)} kg`, icon: TrendingUp, color: "#f59e0b" },
            { label: "Lowest", value: `${minEmission.toFixed(0)} kg`, icon: TrendingDown, color: "#3b82f6" },
            { label: "6-Mo Trend", value: `${improving ? "▼" : "▲"} ${Math.abs(trendPct).toFixed(1)}%`, icon: BarChart3, color: improving ? "#22c55e" : "#ef4444" },
          ].map(({ label, value, icon: Icon, color }) => (
            <div key={label} className="card-slide-in rounded-2xl p-5" style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
              <div className="flex items-center gap-2 mb-2">
                <Icon size={16} style={{ color }} />
                <span style={{ fontSize: 12, color: "var(--text-muted)", fontFamily: "DM Mono" }}>{label}</span>
              </div>
              <p style={{ fontSize: 22, fontWeight: 700, color, fontFamily: "DM Mono" }}>{value}</p>
            </div>
          ))}
        </div>

        {/* Main Emissions Trend Chart */}
        <div className="rounded-2xl p-6" style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 style={{ fontSize: 18, fontWeight: 700, color: "var(--text-primary)", fontFamily: "Syne" }}>
                CO₂ Emissions Trend
              </h2>
              <p style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>Monthly carbon emissions with ML forecast overlay</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-0.5" style={{ background: "#22c55e" }} />
                <span style={{ fontSize: 11, color: "var(--text-muted)" }}>Actual</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-0.5" style={{ background: "#8b5cf6", borderTop: "2px dashed #8b5cf6" }} />
                <span style={{ fontSize: 11, color: "var(--text-muted)" }}>Forecast</span>
              </div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={trendData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <defs>
                <linearGradient id="emissionsGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22c55e" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                </linearGradient>
                <filter id="glow">
                  <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="month" stroke="#555" tick={{ fill: "#666", fontSize: 11 }} />
              <YAxis stroke="#555" tick={{ fill: "#666", fontSize: 11 }} unit=" kg" width={60} />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                verticalAlign="top" 
                height={36}
                wrapperStyle={{ paddingBottom: "15px" }}
              />
              <ReferenceLine 
                y={avgEmissions} 
                stroke="#f59e0b" 
                strokeDasharray="4 4"
                label={{ value: `Avg: ${avgEmissions.toFixed(0)} kg`, fill: "#f59e0b", fontSize: 10, position: "right" }} 
              />
              
              {/* Actual Emissions: Solid green line */}
              <Line 
                type="linear"
                dataKey="emissions" 
                name="Actual CO₂"
                stroke="#22c55e" 
                strokeWidth={3}
                dot={{ fill: "#22c55e", r: 5, strokeWidth: 2, stroke: "#16a34a" }}
                activeDot={{ r: 7, strokeWidth: 2 }}
                connectNulls={false}
                isAnimationActive={true}
                filter="url(#glow)"
              />
              
              {/* Forecast: Dashed purple line */}
              <Line 
                type="linear"
                dataKey="forecast" 
                name="ML Forecast (Next 6 Mo)"
                stroke="#8b5cf6" 
                strokeWidth={2.5}
                strokeDasharray="8 4"
                dot={{ fill: "#8b5cf6", r: 5, strokeWidth: 2, stroke: "#7c3aed" }}
                activeDot={{ r: 7, strokeWidth: 2 }}
                connectNulls={true}
                isAnimationActive={true}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* ML Forecast Predictions Summary */}
        {trendData.some((d: TrendPoint) => d.forecast !== undefined && d.emissions === undefined) && (
          <div className="rounded-2xl p-6" style={{ background: "linear-gradient(135deg, rgba(139,92,246,0.1), rgba(139,92,246,0.05))", border: "1px solid rgba(139,92,246,0.3)" }}>
            <div className="flex items-center gap-3 mb-4">
              <div style={{ width: 36, height: 36, background: "rgba(139,92,246,0.2)", borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <TrendingUp size={20} style={{ color: "#8b5cf6" }} />
              </div>
              <div>
                <h2 style={{ fontSize: 18, fontWeight: 700, color: "var(--text-primary)", fontFamily: "Syne" }}>
                  📊 ML Model 3: Next 6 Months Prediction
                </h2>
                <p style={{ fontSize: 12, color: "var(--text-muted)" }}>Trend Forecaster - XGBoost Model</p>
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
              {trendData.filter((d: TrendPoint) => d.forecast !== undefined && d.emissions === undefined).map((prediction: TrendPoint, idx: number) => (
                <div key={idx} className="rounded-xl p-4" style={{ background: "rgba(139,92,246,0.1)", border: "1px solid rgba(139,92,246,0.2)" }}>
                  <p style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600, marginBottom: 6 }}>
                    {prediction.month}
                  </p>
                  <p style={{ fontSize: 18, fontWeight: 700, color: "#8b5cf6", fontFamily: "DM Mono" }}>
                    {prediction.forecast?.toFixed(0)} kg
                  </p>
                  <p style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 4 }}>
                    Predicted CO₂
                  </p>
                </div>
              ))}
            </div>
            
            <div style={{ marginTop: 12, padding: "8px 12px", background: "rgba(139,92,246,0.05)", borderRadius: 8, borderLeft: "3px solid #8b5cf6" }}>
              <p style={{ fontSize: 12, color: "var(--text-muted)" }}>
                <span style={{ color: "#8b5cf6", fontWeight: 600 }}>💡 Insight:</span> Model 3 predicts a slight downward trend. Continue monitoring electricity and fuel usage for accurate forecasting.
              </p>
            </div>
          </div>
        )}
        {trendData.some(d => d.electricity != null) && (
          <div className="rounded-2xl p-6" style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
            <h2 style={{ fontSize: 18, fontWeight: 700, color: "var(--text-primary)", fontFamily: "Syne", marginBottom: 16 }}>
              Electricity vs Fuel Split
            </h2>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={trendData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <defs>
                  <linearGradient id="elecGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="fuelGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="month" stroke="#555" tick={{ fill: "#666", fontSize: 11 }} />
                <YAxis stroke="#555" tick={{ fill: "#666", fontSize: 11 }} unit=" kg" width={60} />
                <Tooltip content={<CustomTooltip />} />
                <Legend iconSize={10} wrapperStyle={{ fontSize: 11, color: "#888" }} />
                <Area type="monotone" dataKey="electricity" name="Electricity CO₂"
                  stroke="#3b82f6" strokeWidth={2} fill="url(#elecGrad)"
                  dot={{ fill: "#3b82f6", r: 3 }} connectNulls />
                <Area type="monotone" dataKey="fuel" name="Fuel CO₂"
                  stroke="#f97316" strokeWidth={2} fill="url(#fuelGrad)"
                  dot={{ fill: "#f97316", r: 3 }} connectNulls />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Calculate to add current data */}
        <div className="rounded-2xl p-6" style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
          <h2 style={{ fontSize: 16, fontWeight: 700, color: "var(--text-primary)", fontFamily: "Syne", marginBottom: 16 }}>
            <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <Calculator size={18} style={{ color: "#22c55e" }} />
              Add Current Month Data
            </span>
          </h2>
          <form onSubmit={handleCalculate} className="grid grid-cols-3 gap-6">
            <div>
              <label className="flex items-center gap-2 mb-2" style={{ fontSize: 12, color: "var(--text-muted)" }}>
                <Zap size={14} style={{ color: "#3b82f6" }} /> Electricity (kWh/mo)
              </label>
              <input type="number" value={electricity} onChange={e => setElectricity(e.target.value)}
                placeholder="e.g. 500" min="0" step="0.1"
                style={{ width: "100%", background: "var(--bg-secondary)", border: "1px solid var(--border)", borderRadius: 10, padding: "10px 14px", color: "var(--text-primary)", fontSize: 14, outline: "none" }} />
            </div>
            <div>
              <label className="flex items-center gap-2 mb-2" style={{ fontSize: 12, color: "var(--text-muted)" }}>
                <Fuel size={14} style={{ color: "#f97316" }} /> Fuel (Litres/mo)
              </label>
              <input type="number" value={fuel} onChange={e => setFuel(e.target.value)}
                placeholder="e.g. 100" min="0" step="0.1"
                style={{ width: "100%", background: "var(--bg-secondary)", border: "1px solid var(--border)", borderRadius: 10, padding: "10px 14px", color: "var(--text-primary)", fontSize: 14, outline: "none" }} />
            </div>
            <div className="flex items-end gap-3">
              <button type="submit" disabled={loading || !electricity || !fuel || !backendConnected}
                style={{ flex: 1, background: "linear-gradient(135deg,#22c55e,#4ade80)", color: "#050b12", borderRadius: 10, padding: "10px 0", fontWeight: 700, fontSize: 14, cursor: "pointer", opacity: (loading || !electricity || !fuel || !backendConnected) ? 0.5 : 1, border: "none" }}>
                {loading ? "..." : "Plot on Chart"}
              </button>
              {currentCO2 && (
                <button type="button" onClick={generateInsights} disabled={aiLoading}
                  style={{ padding: "10px 16px", background: "rgba(139,92,246,0.15)", border: "1px solid rgba(139,92,246,0.3)", color: "#8b5cf6", borderRadius: 10, cursor: "pointer", fontSize: 13, fontWeight: 600 }}>
                  {aiLoading ? "..." : "AI Insights"}
                </button>
              )}
            </div>
          </form>
          {currentCO2 && (
            <div className="mt-4 p-3 rounded-xl" style={{ background: "rgba(34,197,94,0.05)", border: "1px solid rgba(34,197,94,0.15)" }}>
              <span style={{ fontSize: 13, color: "#22c55e" }}>
                ✅ Current month: <b>{currentCO2.toFixed(1)} kg CO₂</b> — Score: <b>{currentScore}</b>
              </span>
            </div>
          )}
        </div>

        {/* AI Insights */}
        {aiInsights && (
          <div className="rounded-2xl p-6 card-slide-in" style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
            <div className="flex items-center gap-3 mb-5">
              <div style={{ width: 36, height: 36, background: "rgba(34,197,94,0.1)", borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Lightbulb size={18} style={{ color: "#22c55e" }} />
              </div>
              <div>
                <h2 style={{ fontSize: 16, fontWeight: 700, color: "var(--text-primary)" }}>AI Trend Insights</h2>
                <p style={{ fontSize: 11, color: "var(--text-muted)" }}>Powered by Gemini</p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {aiInsights.insights?.slice(0, 4).map((insight: any, i: number) => (
                <div key={i} className="rounded-xl p-4" style={{ background: "var(--bg-secondary)", border: "1px solid var(--border)" }}>
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-2 h-2 rounded-full" style={{ background: insight.priority === "high" ? "#ef4444" : insight.priority === "medium" ? "#f59e0b" : "#22c55e" }} />
                    <span style={{ fontSize: 10, color: "#22c55e", fontFamily: "DM Mono" }}>{insight.model}</span>
                  </div>
                  <h3 style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)", marginBottom: 4 }}>{insight.title}</h3>
                  <p style={{ fontSize: 12, color: "var(--text-muted)", lineHeight: 1.5 }}>{insight.content}</p>
                  {insight.action && (
                    <p style={{ fontSize: 11, color: "#22c55e", marginTop: 8 }}>→ {insight.action}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
