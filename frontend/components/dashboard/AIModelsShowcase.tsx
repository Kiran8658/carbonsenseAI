import { Brain, TrendingUp, Target, Sparkles } from "lucide-react";

export default function AIModelsShowcase() {
  return (
    <div
      style={{
        background: "linear-gradient(135deg, rgba(34, 197, 94, 0.05), rgba(16, 185, 129, 0.08))",
        border: "1px solid var(--green-dim)",
        borderRadius: 16,
        padding: "24px 28px",
        marginBottom: 32,
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Decorative gradient overlay */}
      <div
        style={{
          position: "absolute",
          top: 0,
          right: 0,
          width: "40%",
          height: "100%",
          background: "radial-gradient(circle at top right, rgba(34, 197, 94, 0.15), transparent)",
          pointerEvents: "none",
        }}
      />

      <div style={{ position: "relative", zIndex: 1 }}>
        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
          <div
            style={{
              width: 48,
              height: 48,
              background: "linear-gradient(135deg, #22c55e, #16a34a)",
              borderRadius: 12,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 4px 12px rgba(34, 197, 94, 0.3)",
            }}
          >
            <Sparkles size={24} color="#fff" />
          </div>
          <div>
            <h2
              style={{
                fontFamily: "Syne, sans-serif",
                fontSize: 22,
                fontWeight: 800,
                color: "var(--text-primary)",
                marginBottom: 2,
                letterSpacing: "-0.02em",
              }}
            >
              Powered by 3 Advanced AI Models
            </h2>
            <p style={{ fontSize: 13, color: "var(--text-muted)", fontFamily: "DM Mono, monospace" }}>
              Machine Learning • Intelligent Forecasting • Real-time Scoring
            </p>
          </div>
        </div>

        {/* AI Models Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
          {/* Model 1: Emissions Predictor */}
          <div
            className="card"
            style={{
              padding: 20,
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
              transition: "all 0.3s ease",
            }}
          >
            <div
              style={{
                width: 40,
                height: 40,
                background: "rgba(34, 197, 94, 0.15)",
                border: "1px solid rgba(34, 197, 94, 0.3)",
                borderRadius: 10,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                marginBottom: 14,
              }}
            >
              <Brain size={20} color="#22c55e" />
            </div>
            <div
              style={{
                display: "inline-block",
                background: "rgba(34, 197, 94, 0.1)",
                border: "1px solid rgba(34, 197, 94, 0.2)",
                padding: "3px 8px",
                borderRadius: 6,
                marginBottom: 10,
              }}
            >
              <span
                style={{
                  fontSize: 10,
                  fontWeight: 700,
                  fontFamily: "Syne, sans-serif",
                  color: "#22c55e",
                  letterSpacing: "0.05em",
                  textTransform: "uppercase",
                }}
              >
                AI Model #1
              </span>
            </div>
            <h3
              style={{
                fontFamily: "Syne, sans-serif",
                fontSize: 16,
                fontWeight: 700,
                color: "var(--text-primary)",
                marginBottom: 8,
              }}
            >
              Emissions Predictor
            </h3>
            <p style={{ fontSize: 12, color: "var(--text-muted)", lineHeight: 1.6, marginBottom: 12 }}>
              Random Forest ML model analyzes electricity & fuel consumption to predict accurate CO₂ emissions
            </p>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                fontSize: 11,
                color: "var(--text-muted)",
                fontFamily: "DM Mono, monospace",
              }}
            >
              <div
                style={{
                  width: 6,
                  height: 6,
                  background: "#22c55e",
                  borderRadius: "50%",
                  boxShadow: "0 0 6px rgba(34, 197, 94, 0.6)",
                }}
              />
              Active & Learning
            </div>
          </div>

          {/* Model 2: Carbon Scorer */}
          <div
            className="card"
            style={{
              padding: 20,
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
              transition: "all 0.3s ease",
            }}
          >
            <div
              style={{
                width: 40,
                height: 40,
                background: "rgba(59, 130, 246, 0.15)",
                border: "1px solid rgba(59, 130, 246, 0.3)",
                borderRadius: 10,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                marginBottom: 14,
              }}
            >
              <Target size={20} color="#3b82f6" />
            </div>
            <div
              style={{
                display: "inline-block",
                background: "rgba(59, 130, 246, 0.1)",
                border: "1px solid rgba(59, 130, 246, 0.2)",
                padding: "3px 8px",
                borderRadius: 6,
                marginBottom: 10,
              }}
            >
              <span
                style={{
                  fontSize: 10,
                  fontWeight: 700,
                  fontFamily: "Syne, sans-serif",
                  color: "#3b82f6",
                  letterSpacing: "0.05em",
                  textTransform: "uppercase",
                }}
              >
                AI Model #2
              </span>
            </div>
            <h3
              style={{
                fontFamily: "Syne, sans-serif",
                fontSize: 16,
                fontWeight: 700,
                color: "var(--text-primary)",
                marginBottom: 8,
              }}
            >
              Carbon Scorer
            </h3>
            <p style={{ fontSize: 12, color: "var(--text-muted)", lineHeight: 1.6, marginBottom: 12 }}>
              Intelligent AI algorithm evaluates emissions against MSME benchmarks to assign performance scores
            </p>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                fontSize: 11,
                color: "var(--text-muted)",
                fontFamily: "DM Mono, monospace",
              }}
            >
              <div
                style={{
                  width: 6,
                  height: 6,
                  background: "#3b82f6",
                  borderRadius: "50%",
                  boxShadow: "0 0 6px rgba(59, 130, 246, 0.6)",
                }}
              />
              Active & Learning
            </div>
          </div>

          {/* Model 3: Trend Forecaster */}
          <div
            className="card"
            style={{
              padding: 20,
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
              transition: "all 0.3s ease",
            }}
          >
            <div
              style={{
                width: 40,
                height: 40,
                background: "rgba(168, 85, 247, 0.15)",
                border: "1px solid rgba(168, 85, 247, 0.3)",
                borderRadius: 10,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                marginBottom: 14,
              }}
            >
              <TrendingUp size={20} color="#a855f7" />
            </div>
            <div
              style={{
                display: "inline-block",
                background: "rgba(168, 85, 247, 0.1)",
                border: "1px solid rgba(168, 85, 247, 0.2)",
                padding: "3px 8px",
                borderRadius: 6,
                marginBottom: 10,
              }}
            >
              <span
                style={{
                  fontSize: 10,
                  fontWeight: 700,
                  fontFamily: "Syne, sans-serif",
                  color: "#a855f7",
                  letterSpacing: "0.05em",
                  textTransform: "uppercase",
                }}
              >
                AI Model #3
              </span>
            </div>
            <h3
              style={{
                fontFamily: "Syne, sans-serif",
                fontSize: 16,
                fontWeight: 700,
                color: "var(--text-primary)",
                marginBottom: 8,
              }}
            >
              Trend Forecaster
            </h3>
            <p style={{ fontSize: 12, color: "var(--text-muted)", lineHeight: 1.6, marginBottom: 12 }}>
              XGBoost & LSTM time-series models predict future emission trends to enable proactive planning
            </p>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                fontSize: 11,
                color: "var(--text-muted)",
                fontFamily: "DM Mono, monospace",
              }}
            >
              <div
                style={{
                  width: 6,
                  height: 6,
                  background: "#a855f7",
                  borderRadius: "50%",
                  boxShadow: "0 0 6px rgba(168, 85, 247, 0.6)",
                }}
              />
              Active & Learning
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
