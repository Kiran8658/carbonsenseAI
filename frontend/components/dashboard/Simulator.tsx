import React, { useState, useEffect } from "react";
import axios from "axios";
import { Sliders, TrendingDown, TreePine, Home, Zap, Fuel } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8004";

interface SimulatorProps {
  electricityKwh: number;
  fuelLitres: number;
}

interface SimResult {
  before_co2: number;
  after_co2: number;
  savings_co2: number;
  savings_percentage: number;
  electricity_before: number;
  electricity_after: number;
  fuel_before: number;
  fuel_after: number;
  yearly_co2_savings?: number;
  yearly_cost_savings_inr?: number;
  trees_equivalent?: number;
  homes_powered_equivalent?: number;
}

export default function Simulator({ electricityKwh, fuelLitres }: SimulatorProps) {
  const [elecPct, setElecPct] = useState(20);
  const [fuelPct, setFuelPct] = useState(15);
  const [result, setResult] = useState<SimResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => { setMounted(true); }, []);

  const handleSimulate = async () => {
    if (!electricityKwh && !fuelLitres) return;
    setLoading(true);
    try {
      const r = await axios.post(`${API_URL}/api/simulate`, {
        electricity_kwh: electricityKwh,
        fuel_litres: fuelLitres,
        electricity_reduction_pct: elecPct,
        fuel_reduction_pct: fuelPct,
      });
      setResult(r.data);
      setMounted(false);
      setTimeout(() => setMounted(true), 50);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  return (
    <div className="card p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-9 h-9 rounded-lg flex items-center justify-center"
          style={{ background: "rgba(139,92,246,0.15)" }}>
          <Sliders size={18} className="text-purple-400" />
        </div>
        <div>
          <h2 style={{ fontFamily: "Syne", fontSize: 17, color: "var(--text-primary)" }}>Emission Simulator</h2>
          <p style={{ fontSize: 12, color: "var(--text-muted)" }}>Model yearly impact of reduction strategies</p>
        </div>
      </div>

      {/* Sliders */}
      <div className="space-y-5 mb-6">
        <div>
          <div className="flex justify-between mb-2">
            <label className="flex items-center gap-2 text-sm" style={{ color: "var(--text-muted)" }}>
              <Zap size={13} className="text-blue-400" /> Electricity Reduction
            </label>
            <span style={{ fontFamily: "DM Mono", fontSize: 14, color: "#3b82f6" }}>{elecPct}%</span>
          </div>
          <input type="range" min={0} max={80} value={elecPct}
            onChange={e => setElecPct(+e.target.value)} className="cs-slider" />
        </div>
        <div>
          <div className="flex justify-between mb-2">
            <label className="flex items-center gap-2 text-sm" style={{ color: "var(--text-muted)" }}>
              <Fuel size={13} className="text-orange-400" /> Fuel Reduction
            </label>
            <span style={{ fontFamily: "DM Mono", fontSize: 14, color: "#f97316" }}>{fuelPct}%</span>
          </div>
          <input type="range" min={0} max={80} value={fuelPct}
            onChange={e => setFuelPct(+e.target.value)} className="cs-slider" />
        </div>
      </div>

      <button onClick={handleSimulate} disabled={loading || (!electricityKwh && !fuelLitres)}
        className="btn-primary w-full flex items-center justify-center gap-2 mb-6">
        {loading ? "Simulating..." : <><TrendingDown size={16} /> Simulate Impact</>}
      </button>

      {result && (
        <div className={mounted ? "slide-in" : ""}>
          {/* Before / After */}
          <div className="grid grid-cols-2 gap-3 mb-4">
            {[
              { label: "Before", val: result.before_co2.toFixed(1), color: "#ef4444" },
              { label: "After",  val: result.after_co2.toFixed(1),  color: "#22c55e" },
            ].map(({ label, val, color }) => (
              <div key={label} className="rounded-xl p-4"
                style={{ background: "rgba(255,255,255,0.02)", border: `1px solid ${color}30` }}>
                <p style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 4 }}>{label}</p>
                <p style={{ fontFamily: "DM Mono", fontSize: 22, fontWeight: 700, color }}>{val} kg</p>
              </div>
            ))}
          </div>

          {/* Savings badge */}
          <div className="rounded-xl p-4 mb-4 text-center"
            style={{ background: "rgba(34,197,94,0.08)", border: "1px solid rgba(34,197,94,0.2)" }}>
            <p style={{ fontSize: 28, fontWeight: 800, color: "#22c55e", fontFamily: "DM Mono" }}>
              -{result.savings_percentage.toFixed(1)}%
            </p>
            <p style={{ fontSize: 13, color: "var(--text-secondary)" }}>
              You save {result.savings_co2.toFixed(1)} kg CO₂/month
            </p>
          </div>

          {/* Yearly impact */}
          <div className="grid grid-cols-2 gap-3">
            {[
              {
                icon: <TrendingDown size={16} className="text-green-400" />,
                label: "Yearly CO₂ Saved",
                val: result.yearly_co2_savings ? `${result.yearly_co2_savings.toFixed(0)} kg` : `${(result.savings_co2 * 12).toFixed(0)} kg`,
                color: "#22c55e"
              },
              {
                icon: <span style={{ fontSize: 14 }}>₹</span>,
                label: "Yearly Cost Savings",
                val: result.yearly_cost_savings_inr
                  ? `₹${result.yearly_cost_savings_inr.toLocaleString("en-IN")}`
                  : "—",
                color: "#f59e0b"
              },
              {
                icon: <TreePine size={16} className="text-emerald-400" />,
                label: "Trees Equivalent",
                val: result.trees_equivalent ? `${result.trees_equivalent} trees` : "—",
                color: "#34d399"
              },
              {
                icon: <Home size={16} className="text-blue-400" />,
                label: "Homes Powered",
                val: result.homes_powered_equivalent
                  ? `${result.homes_powered_equivalent.toFixed(1)} homes`
                  : "—",
                color: "#60a5fa"
              },
            ].map(({ icon, label, val, color }) => (
              <div key={label} className="rounded-lg p-3"
                style={{ background: "rgba(255,255,255,0.02)", border: "1px solid var(--border)" }}>
                <div className="flex items-center gap-2 mb-1">
                  {icon}
                  <p style={{ fontSize: 10, color: "var(--text-muted)" }}>{label}</p>
                </div>
                <p style={{ fontFamily: "DM Mono", fontSize: 14, fontWeight: 700, color }}>{val}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
