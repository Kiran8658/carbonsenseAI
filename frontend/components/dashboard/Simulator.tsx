import { useState, useEffect } from "react";
import { SlidersHorizontal, Loader2, TrendingDown } from "lucide-react";
import { simulateReduction } from "../../lib/api";
import { SimulatorResult, ModelConnectionStatus } from "../../lib/types";
import ConnectionLight from "../ui/ConnectionLight";

interface SimulatorProps {
  electricity_kwh: number;
  fuel_litres: number;
  initialTotal: number;
  model1Status?: ModelConnectionStatus;
}

export default function Simulator({ electricity_kwh, fuel_litres, initialTotal, model1Status = "disconnected" }: SimulatorProps) {
  const [elecPct, setElecPct] = useState(0);
  const [fuelPct, setFuelPct] = useState(0);
  const [result, setResult] = useState<SimulatorResult | null>(null);
  const [loading, setLoading] = useState(false);

  const runSimulation = async () => {
    if (!electricity_kwh || !fuel_litres) return;
    setLoading(true);
    try {
      const data = await simulateReduction({
        electricity_kwh,
        fuel_litres,
        electricity_reduction_pct: elecPct,
        fuel_reduction_pct: fuelPct,
      });
      setResult(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  // Auto-run whenever sliders change
  useEffect(() => {
    if (electricity_kwh > 0 && fuel_litres > 0) {
      const timer = setTimeout(runSimulation, 300);
      return () => clearTimeout(timer);
    }
  }, [elecPct, fuelPct, electricity_kwh, fuel_litres]);

  const beforeTotal = result?.before_co2 ?? initialTotal;
  const afterTotal = result?.after_co2 ?? initialTotal;
  const savingsPct = result?.savings_percentage ?? 0;

  const barWidth = beforeTotal > 0 ? (afterTotal / beforeTotal) * 100 : 100;

  return (
    <div className="card" style={{ padding: "28px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
        <SlidersHorizontal size={18} color="var(--green-primary)" />
        <h2
          style={{
            fontFamily: "Syne, sans-serif",
            fontSize: 18,
            fontWeight: 700,
            color: "var(--text-primary)",
          }}
        >
          Emission Simulator
        </h2>
      </div>
      <p style={{ fontSize: 13, color: "var(--text-muted)", marginBottom: 28 }}>
        Drag sliders to see the impact of reducing energy consumption
      </p>
      <div style={{ marginBottom: 16 }}>
        <ConnectionLight status={model1Status} label="Simulation Engine" compact />
      </div>

      {/* Sliders */}
      <div style={{ display: "flex", flexDirection: "column", gap: 24, marginBottom: 28 }}>
        {/* Electricity slider */}
        <div>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 10 }}>
            <label
              style={{
                fontSize: 13,
                fontWeight: 600,
                fontFamily: "Syne, sans-serif",
                color: "#f59e0b",
              }}
            >
              ⚡ Electricity Reduction
            </label>
            <span
              style={{
                fontFamily: "DM Mono, monospace",
                fontSize: 15,
                fontWeight: 600,
                color: "#f59e0b",
              }}
            >
              {elecPct}%
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            value={elecPct}
            onChange={(e) => setElecPct(Number(e.target.value))}
            className="cs-slider"
            style={{
              background: `linear-gradient(to right, #f59e0b ${elecPct}%, var(--border) ${elecPct}%)`,
            } as React.CSSProperties}
          />
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 4 }}>
            <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "DM Mono, monospace" }}>0%</span>
            <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "DM Mono, monospace" }}>100%</span>
          </div>
        </div>

        {/* Fuel slider */}
        <div>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 10 }}>
            <label
              style={{
                fontSize: 13,
                fontWeight: 600,
                fontFamily: "Syne, sans-serif",
                color: "#3b82f6",
              }}
            >
              ⛽ Fuel Reduction
            </label>
            <span
              style={{
                fontFamily: "DM Mono, monospace",
                fontSize: 15,
                fontWeight: 600,
                color: "#3b82f6",
              }}
            >
              {fuelPct}%
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            value={fuelPct}
            onChange={(e) => setFuelPct(Number(e.target.value))}
            className="cs-slider"
            style={{
              background: `linear-gradient(to right, #3b82f6 ${fuelPct}%, var(--border) ${fuelPct}%)`,
            } as React.CSSProperties}
          />
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 4 }}>
            <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "DM Mono, monospace" }}>0%</span>
            <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "DM Mono, monospace" }}>100%</span>
          </div>
        </div>
      </div>

      {/* Before vs After */}
      <div
        style={{
          background: "#0d1826",
          border: "1px solid var(--border)",
          borderRadius: 14,
          padding: "20px",
        }}
      >
        <div style={{ display: "grid", gridTemplateColumns: "1fr auto 1fr", gap: 16, alignItems: "center", marginBottom: 20 }}>
          {/* Before */}
          <div style={{ textAlign: "center" }}>
            <p style={{ fontSize: 11, fontFamily: "Syne, sans-serif", fontWeight: 700, color: "var(--text-muted)", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 6 }}>
              Before
            </p>
            <p
              style={{
                fontSize: 28,
                fontWeight: 800,
                fontFamily: "Syne, sans-serif",
                color: "#ef4444",
                lineHeight: 1,
              }}
            >
              {beforeTotal.toFixed(0)}
            </p>
            <p style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "DM Mono, monospace", marginTop: 2 }}>
              kg CO₂
            </p>
          </div>

          {/* Arrow */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
            <TrendingDown size={22} color="#22c55e" />
          </div>

          {/* After */}
          <div style={{ textAlign: "center" }}>
            <p style={{ fontSize: 11, fontFamily: "Syne, sans-serif", fontWeight: 700, color: "var(--text-muted)", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 6 }}>
              After
            </p>
            <p
              style={{
                fontSize: 28,
                fontWeight: 800,
                fontFamily: "Syne, sans-serif",
                color: "#22c55e",
                lineHeight: 1,
              }}
            >
              {loading ? "..." : afterTotal.toFixed(0)}
            </p>
            <p style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "DM Mono, monospace", marginTop: 2 }}>
              kg CO₂
            </p>
          </div>
        </div>

        {/* Progress bar */}
        <div style={{ marginBottom: 12 }}>
          <div
            style={{
              height: 10,
              background: "var(--border)",
              borderRadius: 5,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: `${barWidth}%`,
                height: "100%",
                background: savingsPct > 30 ? "#22c55e" : savingsPct > 15 ? "#f59e0b" : "#3b82f6",
                borderRadius: 5,
                transition: "width 0.4s ease",
                boxShadow: "0 0 8px rgba(34,197,94,0.4)",
              }}
            />
          </div>
        </div>

        {/* Savings */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>
            CO₂ savings:{" "}
            <strong style={{ color: "#22c55e", fontFamily: "DM Mono, monospace" }}>
              {result ? `-${result.savings_co2.toFixed(1)} kg` : "0 kg"}
            </strong>
          </span>
          <div
            style={{
              background: "#22c55e15",
              border: "1px solid #22c55e33",
              borderRadius: 8,
              padding: "4px 14px",
            }}
          >
            <span
              style={{
                fontFamily: "Syne, sans-serif",
                fontWeight: 800,
                fontSize: 18,
                color: "#22c55e",
              }}
            >
              -{savingsPct.toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      {!electricity_kwh && (
        <p style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 16, textAlign: "center" }}>
          ↑ Calculate your emissions first to activate the simulator
        </p>
      )}
    </div>
  );
}
