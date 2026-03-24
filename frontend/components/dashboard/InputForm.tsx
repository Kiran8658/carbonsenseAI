import { useState } from "react";
import { Zap, Fuel, Calculator, Loader2 } from "lucide-react";
import ConnectionLight from "../ui/ConnectionLight";
import { ModelConnectionStatus } from "../../lib/types";

interface InputFormProps {
  onSubmit: (electricity: number, fuel: number) => void;
  loading: boolean;
  model1Status?: ModelConnectionStatus;
  model2Status?: ModelConnectionStatus;
}

export default function InputForm({ onSubmit, loading, model1Status = "disconnected", model2Status = "disconnected" }: InputFormProps) {
  const [electricity, setElectricity] = useState("");
  const [fuel, setFuel] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!electricity || !fuel) return;
    onSubmit(parseFloat(electricity), parseFloat(fuel));
  };

  const presets = [
    { label: "Small Shop", electricity: 180, fuel: 40 },
    { label: "Mid Factory", electricity: 850, fuel: 200 },
    { label: "Large MSME", electricity: 2400, fuel: 600 },
  ];

  return (
    <div className="card" style={{ padding: "28px" }}>
      <div style={{ marginBottom: 24 }}>
        <h2
          style={{
            fontFamily: "Syne, sans-serif",
            fontSize: 20,
            fontWeight: 700,
            color: "var(--text-primary)",
            marginBottom: 4,
          }}
        >
          Calculate Emissions
        </h2>
        <p style={{ fontSize: 13, color: "var(--text-muted)" }}>
          Enter monthly consumption to get your carbon footprint
        </p>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 10 }}>
          <ConnectionLight status={model1Status} label="Model 1" compact />
          <ConnectionLight status={model2Status} label="Model 2" compact />
        </div>
      </div>

      {/* Quick presets */}
      <div style={{ marginBottom: 20 }}>
        <p
          style={{
            fontSize: 11,
            fontWeight: 600,
            fontFamily: "Syne, sans-serif",
            color: "var(--text-muted)",
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            marginBottom: 10,
          }}
        >
          Quick Presets
        </p>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {presets.map((p) => (
            <button
              key={p.label}
              onClick={() => {
                setElectricity(String(p.electricity));
                setFuel(String(p.fuel));
              }}
              style={{
                background: "var(--bg-card-hover)",
                border: "1px solid var(--border)",
                borderRadius: 8,
                padding: "6px 14px",
                color: "var(--text-secondary)",
                fontSize: 12,
                fontFamily: "Syne, sans-serif",
                fontWeight: 600,
                cursor: "pointer",
                transition: "all 0.15s",
              }}
              onMouseEnter={(e) => {
                (e.target as HTMLButtonElement).style.borderColor = "var(--green-primary)";
                (e.target as HTMLButtonElement).style.color = "var(--green-primary)";
              }}
              onMouseLeave={(e) => {
                (e.target as HTMLButtonElement).style.borderColor = "var(--border)";
                (e.target as HTMLButtonElement).style.color = "var(--text-secondary)";
              }}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 18 }}>
        {/* Electricity */}
        <div>
          <label
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              fontSize: 13,
              fontWeight: 600,
              fontFamily: "Syne, sans-serif",
              color: "var(--text-secondary)",
              marginBottom: 8,
            }}
          >
            <Zap size={14} color="#f59e0b" />
            Electricity Usage
            <span style={{ color: "var(--text-muted)", fontWeight: 400 }}>(kWh / month)</span>
          </label>
          <input
            type="number"
            min="0"
            step="0.1"
            value={electricity}
            onChange={(e) => setElectricity(e.target.value)}
            placeholder="e.g. 500"
            className="cs-input"
            required
          />
          {electricity && (
            <p style={{ fontSize: 12, color: "var(--green-primary)", marginTop: 6, fontFamily: "DM Mono, monospace" }}>
              → {(parseFloat(electricity) * 0.82).toFixed(1)} kg CO₂
            </p>
          )}
        </div>

        {/* Fuel */}
        <div>
          <label
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              fontSize: 13,
              fontWeight: 600,
              fontFamily: "Syne, sans-serif",
              color: "var(--text-secondary)",
              marginBottom: 8,
            }}
          >
            <Fuel size={14} color="#3b82f6" />
            Fuel Consumption
            <span style={{ color: "var(--text-muted)", fontWeight: 400 }}>(litres / month)</span>
          </label>
          <input
            type="number"
            min="0"
            step="0.1"
            value={fuel}
            onChange={(e) => setFuel(e.target.value)}
            placeholder="e.g. 100"
            className="cs-input"
            required
          />
          {fuel && (
            <p style={{ fontSize: 12, color: "#3b82f6", marginTop: 6, fontFamily: "DM Mono, monospace" }}>
              → {(parseFloat(fuel) * 2.3).toFixed(1)} kg CO₂
            </p>
          )}
        </div>

        <button
          type="submit"
          className="btn-primary"
          disabled={loading || !electricity || !fuel}
          style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8 }}
        >
          {loading ? (
            <>
              <Loader2 size={16} className="animate-spin" style={{ animation: "spin 1s linear infinite" }} />
              Calculating...
            </>
          ) : (
            <>
              <Calculator size={16} />
              Calculate Carbon Footprint
            </>
          )}
        </button>
      </form>

      {/* Formula hint */}
      <div
        style={{
          marginTop: 20,
          padding: "12px 16px",
          background: "#0d1826",
          borderRadius: 10,
          border: "1px solid var(--border)",
        }}
      >
        <p
          style={{
            fontSize: 11,
            fontFamily: "DM Mono, monospace",
            color: "var(--text-muted)",
            lineHeight: 1.8,
          }}
        >
          <span style={{ color: "#f59e0b" }}>electricity</span> × 0.82 kg/kWh
          <br />
          <span style={{ color: "#3b82f6" }}>fuel</span> × 2.3 kg/litre
        </p>
      </div>
    </div>
  );
}
