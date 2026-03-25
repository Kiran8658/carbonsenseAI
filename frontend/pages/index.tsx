import React, { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import Sidebar from "../components/Sidebar";
import {
  Activity, Zap, Fuel, Lightbulb, TrendingUp, TrendingDown,
  Calculator, BarChart3, Leaf, Sparkles, Award, DollarSign,
  Shield, Target, ChevronRight, RefreshCw, Download, TreePine
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8005";

interface EmissionData {
  total_co2: number;
  electricity_co2: number;
  fuel_co2: number;
  carbon_score: string;
  carbon_score_value: number;
  breakdown_percentage: { electricity: number; fuel: number };
  confidence_score?: number;
  prediction_range?: { low: number; high: number };
  industry_benchmark?: {
    sector: string; avg_monthly_co2: number; your_co2: number;
    percentile: number; is_above_average: boolean;
    reduction_to_average: number; rating: string;
    p25_benchmark: number; p75_benchmark: number;
  };
  cost_savings?: {
    current_monthly_cost_inr: number; electricity_cost_inr: number;
    fuel_cost_inr: number; potential_monthly_savings_inr: number;
    annual_savings_inr: number; savings_from_efficiency_pct: number;
  };
  ml_model_used?: string;
  data_quality_flags?: string[];
}

// ── Animated Score Ring ───────────────────────────────────────────────────────
function ScoreRing({ value, label, color }: { value: number; label: string; color: string }) {
  const [displayVal, setDisplayVal] = useState(0);
  const radius = 54;
  const circ   = 2 * Math.PI * radius;
  const offset = circ - (displayVal / 100) * circ;

  useEffect(() => {
    let start = 0;
    const step = value / 60;
    const id = setInterval(() => {
      start += step;
      if (start >= value) { setDisplayVal(value); clearInterval(id); }
      else setDisplayVal(Math.round(start));
    }, 16);
    return () => clearInterval(id);
  }, [value]);

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative" style={{ width: 140, height: 140 }}>
        {/* Pulsing outer ring */}
        <div
          className="absolute inset-0 rounded-full"
          style={{
            background: `radial-gradient(circle, ${color}18 0%, transparent 70%)`,
            animation: "breathe-glow 2.5s ease-in-out infinite",
          }}
        />
        <svg width="140" height="140" className="score-breathe">
          <defs>
            <linearGradient id="scoreGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor={color} stopOpacity={0.3} />
              <stop offset="100%" stopColor={color} stopOpacity={0.05} />
            </linearGradient>
          </defs>
          {/* Background track */}
          <circle cx="70" cy="70" r={radius} fill="url(#scoreGrad)"
            stroke="var(--border)" strokeWidth="10" />
          {/* Animated filled arc */}
          <circle
            className="score-ring"
            cx="70" cy="70" r={radius}
            fill="none"
            stroke={color}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circ}
            strokeDashoffset={offset}
            transform="rotate(-90 70 70)"
            style={{ filter: `drop-shadow(0 0 8px ${color})` }}
          />
          {/* Centre text */}
          <text x="70" y="65" textAnchor="middle"
            style={{ fontFamily: "DM Mono", fontSize: 26, fontWeight: 700, fill: color }}>
            {displayVal}
          </text>
          <text x="70" y="82" textAnchor="middle"
            style={{ fontFamily: "Syne", fontSize: 10, fill: "var(--text-muted)", letterSpacing: 1 }}>
            /100
          </text>
        </svg>
        {/* Orbiting dot */}
        <div style={{
          position: "absolute", top: 0, left: 0, width: "100%", height: "100%",
          animation: "orbit 4s linear infinite",
          transformOrigin: "50% 50%",
        }}>
          <div style={{
            position: "absolute", top: 4, left: "50%", marginLeft: -4,
            width: 8, height: 8, borderRadius: "50%",
            background: color, boxShadow: `0 0 8px ${color}`,
          }} />
        </div>
      </div>
      <span className="text-lg font-bold" style={{ color, fontFamily: "Syne" }}>{label}</span>
    </div>
  );
}

// ── Animated Counter ──────────────────────────────────────────────────────────
function AnimatedNumber({ value, decimals = 1, suffix = "" }: { value: number; decimals?: number; suffix?: string }) {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    let start = 0;
    const duration = 900;
    const steps = 50;
    const increment = value / steps;
    const interval = duration / steps;
    const id = setInterval(() => {
      start += increment;
      if (start >= value) { setDisplay(value); clearInterval(id); }
      else setDisplay(start);
    }, interval);
    return () => clearInterval(id);
  }, [value]);
  return <span className="ticker-value">{display.toFixed(decimals)}{suffix}</span>;
}

// ── Industry Benchmark Bar ────────────────────────────────────────────────────
function BenchmarkBar({ benchmark }: { benchmark: NonNullable<EmissionData["industry_benchmark"]> }) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setTimeout(() => setMounted(true), 300); }, []);

  const maxVal  = benchmark.p75_benchmark * 1.2;
  const userPct = Math.min(100, (benchmark.your_co2      / maxVal) * 100);
  const avgPct  = Math.min(100, (benchmark.avg_monthly_co2 / maxVal) * 100);
  const isGood  = !benchmark.is_above_average;

  return (
    <div className="card p-5 slide-in slide-in-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-lg flex items-center justify-center"
            style={{ background: "rgba(139,92,246,0.15)" }}>
            <Target size={18} className="text-purple-400" />
          </div>
          <div>
            <h3 style={{ fontFamily: "Syne", fontSize: 14, color: "var(--text-primary)" }}>
              Industry Benchmark
            </h3>
            <p style={{ fontSize: 11, color: "var(--text-muted)" }}>{benchmark.sector}</p>
          </div>
        </div>
        <span
          className="badge"
          style={{
            background: isGood ? "rgba(34,197,94,0.12)" : "rgba(239,68,68,0.12)",
            color: isGood ? "var(--green-primary)" : "var(--red)",
            border: `1px solid ${isGood ? "rgba(34,197,94,0.3)" : "rgba(239,68,68,0.3)"}`,
          }}
        >
          {benchmark.percentile.toFixed(0)}th %ile
        </span>
      </div>

      {/* You vs average */}
      <div className="space-y-3">
        <div>
          <div className="flex justify-between text-xs mb-1"
            style={{ color: "var(--text-muted)", fontFamily: "DM Mono" }}>
            <span>You</span>
            <span style={{ color: isGood ? "#22c55e" : "#ef4444" }}>
              {benchmark.your_co2.toFixed(0)} kg
            </span>
          </div>
          <div className="benchmark-bar">
            <div
              className="benchmark-fill"
              style={{
                width: mounted ? `${userPct}%` : "0%",
                background: isGood
                  ? "linear-gradient(90deg,#22c55e,#4ade80)"
                  : "linear-gradient(90deg,#ef4444,#f87171)",
              }}
            />
          </div>
        </div>
        <div>
          <div className="flex justify-between text-xs mb-1"
            style={{ color: "var(--text-muted)", fontFamily: "DM Mono" }}>
            <span>Sector Average</span>
            <span>{benchmark.avg_monthly_co2.toFixed(0)} kg</span>
          </div>
          <div className="benchmark-bar">
            <div
              className="benchmark-fill"
              style={{
                width: mounted ? `${avgPct}%` : "0%",
                background: "linear-gradient(90deg,#3b82f6,#60a5fa)",
              }}
            />
          </div>
        </div>
      </div>

      <p className="mt-3 text-xs" style={{ color: "var(--text-secondary)" }}>
        {benchmark.rating}
        {benchmark.is_above_average && benchmark.reduction_to_average > 0 && (
          <span style={{ color: "#f59e0b" }}>
            {" — "}Reduce by {benchmark.reduction_to_average.toFixed(0)} kg to reach average
          </span>
        )}
      </p>
    </div>
  );
}

// ── Cost Savings Card ─────────────────────────────────────────────────────────
function CostSavingsCard({ cost }: { cost: NonNullable<EmissionData["cost_savings"]> }) {
  return (
    <div className="card p-5 slide-in slide-in-4">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-9 h-9 rounded-lg flex items-center justify-center"
          style={{ background: "rgba(245,158,11,0.15)" }}>
          <DollarSign size={18} className="text-amber-400" />
        </div>
        <div>
          <h3 style={{ fontFamily: "Syne", fontSize: 14, color: "var(--text-primary)" }}>
            Cost Analysis
          </h3>
          <p style={{ fontSize: 11, color: "var(--text-muted)" }}>at 20% efficiency gain</p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        {[
          { label: "Monthly Cost", val: `₹${cost.current_monthly_cost_inr.toLocaleString("en-IN")}`, color: "var(--text-secondary)" },
          { label: "Monthly Savings", val: `₹${cost.potential_monthly_savings_inr.toLocaleString("en-IN")}`, color: "#22c55e" },
          { label: "Annual Savings", val: `₹${cost.annual_savings_inr.toLocaleString("en-IN")}`, color: "#f59e0b" },
          { label: "Electricity Cost", val: `₹${cost.electricity_cost_inr.toLocaleString("en-IN")}`, color: "#3b82f6" },
        ].map(({ label, val, color }) => (
          <div key={label} className="rounded-lg p-3" style={{ background: "rgba(255,255,255,0.02)", border: "1px solid var(--border)" }}>
            <p style={{ fontSize: 10, color: "var(--text-muted)", marginBottom: 4 }}>{label}</p>
            <p style={{ fontFamily: "DM Mono", fontSize: 13, fontWeight: 600, color }}>{val}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Main Dashboard ────────────────────────────────────────────────────────────
export default function DashboardPage() {
  const [electricity, setElectricity] = useState("");
  const [fuel, setFuel] = useState("");
  const [sector, setSector] = useState("General MSME");
  const [sectors, setSectors] = useState<string[]>([]);
  const [emissionData, setEmissionData] = useState<EmissionData | null>(null);
  const [backendConnected, setBackendConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState<any[]>([]);
  const [aiInsights, setAiInsights] = useState<any>(null);
  const [dataKey, setDataKey] = useState(0); // force re-animation

  const scoreColor = {
    Excellent: "#22c55e", Good: "#84cc16",
    Average: "#f59e0b", Poor: "#f97316", Critical: "#ef4444",
  };

  const checkBackend = useCallback(async () => {
    try {
      const r = await axios.get(`${API_URL}/health`, { timeout: 3000 });
      setBackendConnected(true);
    } catch { setBackendConnected(false); }
  }, []);

  useEffect(() => {
    checkBackend();
    const id = setInterval(checkBackend, 8000);
    return () => clearInterval(id);
  }, [checkBackend]);

  useEffect(() => {
    axios.get(`${API_URL}/api/sectors`).then(r => {
      if (r.data?.sectors) setSectors(r.data.sectors);
    }).catch(() => {});
  }, []);

  const handleCalculate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!electricity || !fuel || !backendConnected) return;
    setLoading(true);
    try {
      const r = await axios.post(`${API_URL}/api/calculate`, {
        electricity_kwh: parseFloat(electricity),
        fuel_litres:     parseFloat(fuel),
        industry_sector: sector,
      });
      if (r.data?.data) {
        setEmissionData(r.data.data);
        setDataKey(k => k + 1);
        fetchAISuggestions(r.data.data);
      }
    } catch { alert("Failed to calculate — check backend connection."); }
    finally { setLoading(false); }
  };

  const fetchAISuggestions = async (data: EmissionData) => {
    try {
      const r = await axios.post(`${API_URL}/api/ai-suggestions`, {
        electricity_kwh: parseFloat(electricity),
        fuel_litres:     parseFloat(fuel),
        total_co2:       data.total_co2,
        business_type:   sector || "General MSME",
        industry_sector: sector,
      });
      if (r.data?.suggestions) setAiSuggestions(r.data.suggestions);
    } catch {}
  };

  const generateAIInsights = async () => {
    if (!emissionData || !backendConnected) return;
    setAiLoading(true);
    try {
      const r = await axios.post(`${API_URL}/api/reports/ai-insights`, {
        emission_data: emissionData, suggestions: aiSuggestions, history: [], forecast: [],
      });
      if (r.data) setAiInsights(r.data);
    } catch {}
    finally { setAiLoading(false); }
  };

  const currentScore  = emissionData?.carbon_score ?? "Average";
  const currentColor  = (scoreColor as any)[currentScore] ?? "#f59e0b";
  const confidence    = emissionData?.confidence_score ?? 0;
  const confPct       = Math.round(confidence * 100);

  return (
    <div className="min-h-screen grid-bg" style={{ background: "var(--bg-primary)" }}>
      <Sidebar />

      <main className="ml-64 p-8 space-y-7">
        {/* ── Header ────────────────────────────────────── */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-4xl font-bold gradient-text">Dashboard</h1>
              <div className="flex items-center gap-2 px-3 py-1 rounded-full"
                style={{ background: "rgba(200,240,122,0.12)", border: "1px solid rgba(200,240,122,0.25)" }}>
                <Sparkles size={13} style={{ color: "#c8f07a" }} />
                <span style={{ fontSize: 11, fontWeight: 700, color: "#c8f07a", fontFamily: "Syne", letterSpacing: 1 }}>
                  ML PIPELINE v2
                </span>
              </div>
              {/* Live dot */}
              <div className="flex items-center gap-1.5">
                <div className="w-2 h-2 rounded-full live-blink" style={{ background: "#22c55e" }} />
                <span style={{ fontSize: 11, color: "#22c55e", fontFamily: "DM Mono" }}>LIVE</span>
              </div>
            </div>
            <p style={{ color: "var(--text-muted)", fontSize: 14 }}>
              Real-time carbon tracking · Ensemble ML · Industry Benchmarks · ESG Insights
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg"
              style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
              <div className={`w-2.5 h-2.5 rounded-full ${backendConnected ? "status-connected" : ""}`}
                style={{ background: backendConnected ? "#22c55e" : "#ef4444" }} />
              <span style={{ fontSize: 12, color: backendConnected ? "#22c55e" : "#ef4444", fontFamily: "DM Mono" }}>
                {backendConnected ? "Backend ✓" : "Backend ✗"}
              </span>
            </div>
          </div>
        </div>

        {/* ── Input Form ────────────────────────────────── */}
        <div className="card p-6">
          <div className="flex items-center gap-2 mb-5">
            <Calculator size={18} style={{ color: "#c8f07a" }} />
            <h2 style={{ fontFamily: "Syne", fontSize: 17, color: "var(--text-primary)" }}>Data Input</h2>
            <span className="ml-auto text-xs" style={{ color: "var(--text-muted)", fontFamily: "DM Mono" }}>
              {/* Emission factors */}
              Elec: 0.82 kg/kWh · Diesel: 2.3 kg/L
            </span>
          </div>

          <form onSubmit={handleCalculate} className="grid grid-cols-1 md:grid-cols-4 gap-5">
            <div>
              <label className="flex items-center gap-2 text-sm font-medium mb-2"
                style={{ color: "var(--text-muted)" }}>
                <Zap size={14} className="text-blue-400" /> Electricity (kWh/mo)
              </label>
              <input type="number" value={electricity}
                onChange={e => setElectricity(e.target.value)}
                placeholder="e.g. 500" className="cs-input" min="0" step="0.1" required />
              {electricity && (
                <p className="text-xs mt-1.5" style={{ color: "#3b82f6", fontFamily: "DM Mono" }}>
                  ≈ {(parseFloat(electricity) * 0.82).toFixed(1)} kg CO₂
                </p>
              )}
            </div>

            <div>
              <label className="flex items-center gap-2 text-sm font-medium mb-2"
                style={{ color: "var(--text-muted)" }}>
                <Fuel size={14} className="text-orange-400" /> Fuel (Litres/mo)
              </label>
              <input type="number" value={fuel}
                onChange={e => setFuel(e.target.value)}
                placeholder="e.g. 100" className="cs-input" min="0" step="0.1" required />
              {fuel && (
                <p className="text-xs mt-1.5" style={{ color: "#f97316", fontFamily: "DM Mono" }}>
                  ≈ {(parseFloat(fuel) * 2.3).toFixed(1)} kg CO₂
                </p>
              )}
            </div>

            <div>
              <label className="flex items-center gap-2 text-sm font-medium mb-2"
                style={{ color: "var(--text-muted)" }}>
                <Award size={14} className="text-purple-400" /> Industry Sector
              </label>
              <select value={sector} onChange={e => setSector(e.target.value)}
                className="cs-input" style={{ cursor: "pointer" }}>
                {(sectors.length ? sectors : [
                  "General MSME","Manufacturing","Retail","Food & Beverage",
                  "IT & Services","Healthcare","Transportation"
                ]).map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>

            <div className="flex items-end">
              <button type="submit" disabled={loading || !electricity || !fuel || !backendConnected}
                className="btn-primary w-full flex items-center justify-center gap-2">
                {loading ? (
                  <><Activity size={17} style={{ animation: "spin 1s linear infinite" }} /> Analysing...</>
                ) : (
                  <><Calculator size={17} /> Calculate & Analyse</>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* ── Results ───────────────────────────────────── */}
        {emissionData && (
          <div key={dataKey} className="space-y-6">
            {/* Score Ring + Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-5">
              {/* Score Ring */}
              <div className="card p-6 flex flex-col items-center justify-center gap-2 slide-in slide-in-1"
                style={{ gridColumn: "span 1" }}>
                <ScoreRing
                  value={emissionData.carbon_score_value}
                  label={emissionData.carbon_score}
                  color={currentColor}
                />
                {confidence > 0 && (
                  <div className="mt-2 w-full">
                    <div className="flex justify-between mb-1"
                      style={{ fontSize: 10, color: "var(--text-muted)", fontFamily: "DM Mono" }}>
                      <span>ML Confidence</span>
                      <span style={{ color: "#8b5cf6" }}>{confPct}%</span>
                    </div>
                    <div className="confidence-bar" style={{ "--w": `${confPct}%` } as any} />
                  </div>
                )}
                {emissionData.ml_model_used && (
                  <p style={{ fontSize: 10, color: "var(--text-muted)", fontFamily: "DM Mono", textAlign: "center", marginTop: 4 }}>
                    {emissionData.ml_model_used}
                  </p>
                )}
              </div>

              {/* 4 metric cards */}
              <div className="grid grid-cols-2 gap-4" style={{ gridColumn: "span 4" }}>
                {[
                  {
                    label: "Total CO₂", val: emissionData.total_co2, unit: "kg",
                    icon: <Activity size={18} style={{ color: "#c8f07a" }} />,
                    bg: "rgba(200,240,122,0.1)", sub: emissionData.prediction_range
                      ? `Range: ${emissionData.prediction_range.low.toFixed(0)}–${emissionData.prediction_range.high.toFixed(0)} kg`
                      : "CO₂ equivalent", delay: "slide-in-1"
                  },
                  {
                    label: "Electricity CO₂", val: emissionData.electricity_co2, unit: "kg",
                    icon: <Zap size={18} className="text-blue-400" />,
                    bg: "rgba(59,130,246,0.1)", sub: `${emissionData.breakdown_percentage.electricity}% of total`,
                    delay: "slide-in-2"
                  },
                  {
                    label: "Fuel CO₂", val: emissionData.fuel_co2, unit: "kg",
                    icon: <Fuel size={18} className="text-orange-400" />,
                    bg: "rgba(249,115,22,0.1)", sub: `${emissionData.breakdown_percentage.fuel}% of total`,
                    delay: "slide-in-3"
                  },
                  {
                    label: "Monthly Cost", val: emissionData.cost_savings?.current_monthly_cost_inr ?? 0, unit: "",
                    icon: <DollarSign size={18} className="text-amber-400" />,
                    bg: "rgba(245,158,11,0.1)",
                    sub: `Save ₹${emissionData.cost_savings?.potential_monthly_savings_inr?.toLocaleString("en-IN") ?? 0}/mo`,
                    prefix: "₹", delay: "slide-in-4"
                  },
                ].map(({ label, val, unit, icon, bg, sub, prefix, delay }) => (
                  <div key={label} className={`card p-5 metric-card slide-in ${delay}`}>
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: bg }}>
                        {icon}
                      </div>
                      <span style={{ color: "var(--text-muted)", fontSize: 13 }}>{label}</span>
                    </div>
                    <p className="text-2xl font-bold" style={{ color: "var(--text-primary)", fontFamily: "DM Mono" }}>
                      {prefix ?? ""}<AnimatedNumber value={val} decimals={1} suffix={unit ? ` ${unit}` : ""} />
                    </p>
                    <p className="text-xs mt-1.5" style={{ color: "var(--text-secondary)" }}>{sub}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Benchmark + Cost grid */}
            {(emissionData.industry_benchmark || emissionData.cost_savings) && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {emissionData.industry_benchmark && <BenchmarkBar benchmark={emissionData.industry_benchmark} />}
                {emissionData.cost_savings && <CostSavingsCard cost={emissionData.cost_savings} />}
              </div>
            )}

            {/* Data quality flags */}
            {emissionData.data_quality_flags && emissionData.data_quality_flags.length > 0 && (
              <div className="card p-4 flex flex-wrap gap-2 slide-in slide-in-3"
                style={{ borderColor: "rgba(245,158,11,0.25)", background: "rgba(245,158,11,0.04)" }}>
                <Shield size={14} className="text-amber-400 mt-0.5" />
                <div className="flex flex-wrap gap-2">
                  {emissionData.data_quality_flags.map((f, i) => (
                    <span key={i} style={{ fontSize: 12, color: "#f59e0b" }}>{f}</span>
                  ))}
                </div>
              </div>
            )}

            {/* AI Suggestions */}
            {aiSuggestions.length > 0 && (
              <div className="card p-6 slide-in slide-in-2">
                <div className="flex items-center gap-3 mb-5">
                  <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: "rgba(34,197,94,0.12)" }}>
                    <Lightbulb size={18} style={{ color: "#22c55e" }} />
                  </div>
                  <div>
                    <h2 style={{ fontFamily: "Syne", fontSize: 16, color: "var(--text-primary)" }}>AI Recommendations</h2>
                    <p style={{ fontSize: 12, color: "var(--text-muted)" }}>Personalised reduction strategies with cost impact</p>
                  </div>
                  <button onClick={generateAIInsights} disabled={aiLoading || !backendConnected}
                    className="ml-auto flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all"
                    style={{ background: "rgba(200,240,122,0.12)", color: "#c8f07a", border: "1px solid rgba(200,240,122,0.25)" }}>
                    {aiLoading
                      ? <><RefreshCw size={14} style={{ animation: "spin 1s linear infinite" }} /> Generating...</>
                      : <><Sparkles size={14} /> Deep AI Analysis</>
                    }
                  </button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {aiSuggestions.slice(0, 6).map((s: any, i: number) => {
                    const prioColor: any = { Critical: "#ef4444", High: "#f59e0b", Medium: "#3b82f6", Low: "#22c55e" };
                    const prioClass: any = { Critical: "badge-critical", High: "badge-high", Medium: "badge-medium", Low: "badge-low" };
                    return (
                      <div key={i} className="rounded-xl p-4 transition-all"
                        style={{ background: "rgba(255,255,255,0.02)", border: "1px solid var(--border)" }}
                        onMouseEnter={e => (e.currentTarget.style.borderColor = "var(--border-light)")}
                        onMouseLeave={e => (e.currentTarget.style.borderColor = "var(--border)")}>
                        <div className="flex items-start justify-between gap-2 mb-2">
                          <h3 style={{ fontFamily: "Syne", fontSize: 14, color: "var(--text-primary)" }}>{s.title}</h3>
                          <span className={`badge ${prioClass[s.priority] || "badge-medium"}`}>{s.priority}</span>
                        </div>
                        <p style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.5 }}>{s.description}</p>
                        <div className="flex flex-wrap items-center gap-3 mt-3">
                          <span style={{ fontSize: 12, color: "#22c55e", fontFamily: "DM Mono" }}>
                            -{s.savings_percentage}% CO₂
                          </span>
                          {s.cost_savings_inr > 0 && (
                            <span style={{ fontSize: 12, color: "#f59e0b", fontFamily: "DM Mono" }}>
                              ₹{s.cost_savings_inr.toLocaleString("en-IN")}/mo saved
                            </span>
                          )}
                          {s.payback_months > 0 && (
                            <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
                              {s.payback_months}mo payback
                            </span>
                          )}
                          {s.confidence && (
                            <span className="badge badge-confidence" style={{ fontSize: 10 }}>
                              {Math.round(s.confidence * 100)}% conf
                            </span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Deep AI Insights */}
            {aiInsights && (
              <div className="card p-6 slide-in slide-in-1"
                style={{ borderColor: "rgba(200,240,122,0.2)", background: "rgba(200,240,122,0.02)" }}>
                <div className="flex items-center gap-3 mb-5">
                  <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: "rgba(200,240,122,0.15)" }}>
                    <Sparkles size={18} style={{ color: "#c8f07a" }} />
                  </div>
                  <div>
                    <h2 style={{ fontFamily: "Syne", fontSize: 16, color: "var(--text-primary)" }}>Deep AI Insights</h2>
                    <p style={{ fontSize: 12, color: "var(--text-muted)" }}>
                      {aiInsights.api_used === "gemini" ? "⚡ Gemini Flash" : aiInsights.api_used === "openai" ? "🤖 GPT-4o-mini" : "📊 Rule-based Engine"}
                      {aiInsights.fallback ? " (fallback)" : ""}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {aiInsights.insights?.map((ins: any, i: number) => (
                    <div key={i} className="rounded-xl p-4"
                      style={{ background: "rgba(255,255,255,0.02)", border: "1px solid var(--border)" }}>
                      <p style={{ fontSize: 10, color: "#c8f07a", fontFamily: "DM Mono", marginBottom: 4 }}>{ins.model}</p>
                      <h3 style={{ fontFamily: "Syne", fontSize: 14, color: "var(--text-primary)", marginBottom: 6 }}>{ins.title}</h3>
                      <p style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.5 }}>{ins.content}</p>
                      {ins.action && <p style={{ fontSize: 12, color: "#c8f07a", marginTop: 8 }}>→ {ins.action}</p>}
                    </div>
                  ))}
                </div>

                {aiInsights.summary && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-5">
                    {[
                      { label: "Total Emissions", val: `${aiInsights.summary.total_emissions?.toFixed(1)} kg` },
                      { label: "Carbon Score", val: aiInsights.summary.carbon_score },
                      { label: "Improvement", val: aiInsights.summary.improvement_potential, color: "#22c55e" },
                      { label: "Priority", val: aiInsights.summary.priority_level,
                        color: aiInsights.summary.priority_level === "Critical" ? "#ef4444" :
                          aiInsights.summary.priority_level === "High" ? "#f97316" :
                          aiInsights.summary.priority_level === "Medium" ? "#f59e0b" : "#22c55e" },
                    ].map(({ label, val, color }) => (
                      <div key={label} className="rounded-lg p-4"
                        style={{ background: "rgba(255,255,255,0.02)", border: "1px solid var(--border)" }}>
                        <p style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 4 }}>{label}</p>
                        <p style={{ fontFamily: "DM Mono", fontSize: 14, fontWeight: 700, color: color ?? "var(--text-primary)" }}>{val}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
