import { useState, useEffect } from "react";
import { Activity, CheckCircle, XCircle, RefreshCw } from "lucide-react";
import { getHealthStatus } from "../../lib/api";

interface ModelStatus {
  name: string;
  type: string;
  status: "connected" | "disconnected";
  description: string;
}

interface HealthResponse {
  status: string;
  details?: {
    emissions_predictor: ModelStatus;
    carbon_scorer: ModelStatus;
    trend_forecaster: ModelStatus;
  };
  // Alternate backend response shape (sometimes returned instead of `details`)
  models?: {
    emissions_model?: string;
    scorer_model?: string;
    trend_model?: string;
  };
}

export default function SystemStatus() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const checkHealth = async () => {
    try {
      const data = await getHealthStatus();
      setHealth(data);
      setLastChecked(new Date());
    } catch (error) {
      console.error("Health check failed:", error);
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
    // Check health every 10 seconds
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    return status === "connected" ? "#22c55e" : "#ef4444";
  };

  const models = health?.details
    ? [health.details.emissions_predictor, health.details.carbon_scorer, health.details.trend_forecaster]
    : health?.models
      ? [
          {
            name: "AI Model #1: Emissions Predictor",
            type: "RandomForest Regressor",
            description: "Predicts CO₂ emissions from electricity & fuel consumption",
            status: String(health.models.emissions_model || "").startsWith("✅") ? "connected" : "disconnected",
          },
          {
            name: "AI Model #2: Carbon Scorer",
            type: "Smart Scoring Algorithm",
            description: "Evaluates business emissions against MSME benchmarks",
            status: String(health.models.scorer_model || "").startsWith("✅") ? "connected" : "disconnected",
          },
          {
            name: "AI Model #3: Trend Forecaster",
            type: "XGBoost/LSTM",
            description: "Forecasts future emission trends using time-series analysis",
            status: String(health.models.trend_model || "").startsWith("✅") ? "connected" : "disconnected",
          },
        ]
      : [];

  const allConnected = models.every((m) => m.status === "connected");

  return (
    <div
      className="card"
      style={{
        padding: "20px 24px",
        background: "var(--bg-card)",
        border: allConnected ? "1px solid rgba(34, 197, 94, 0.3)" : "1px solid var(--border)",
        marginBottom: 24,
      }}
    >
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 32,
              height: 32,
              background: allConnected ? "rgba(34, 197, 94, 0.15)" : "rgba(239, 68, 68, 0.15)",
              border: `1px solid ${allConnected ? "rgba(34, 197, 94, 0.3)" : "rgba(239, 68, 68, 0.3)"}`,
              borderRadius: 8,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Activity size={16} color={allConnected ? "#22c55e" : "#ef4444"} />
          </div>
          <div>
            <h3
              style={{
                fontFamily: "Syne, sans-serif",
                fontSize: 15,
                fontWeight: 700,
                color: "var(--text-primary)",
                marginBottom: 2,
              }}
            >
              AI System Status
            </h3>
            <p style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "DM Mono, monospace" }}>
              Live model health monitoring
            </p>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ textAlign: "right" }}>
            <p style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 2 }}>Last checked</p>
            <p style={{ fontSize: 11, fontFamily: "DM Mono, monospace", color: "var(--text-secondary)" }}>
              {lastChecked ? lastChecked.toLocaleTimeString() : "—"}
            </p>
          </div>
          <button
            onClick={checkHealth}
            disabled={loading}
            style={{
              background: "transparent",
              border: "1px solid var(--border)",
              borderRadius: 6,
              padding: "6px 8px",
              cursor: loading ? "not-allowed" : "pointer",
              display: "flex",
              alignItems: "center",
              opacity: loading ? 0.5 : 1,
            }}
            title="Refresh status"
          >
            <RefreshCw size={14} color="var(--text-muted)" style={{ animation: loading ? "spin 1s linear infinite" : "none" }} />
          </button>
        </div>
      </div>

      {/* Model Status Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
        {loading ? (
          <>
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                style={{
                  background: "var(--bg-card-hover)",
                  border: "1px solid var(--border)",
                  borderRadius: 10,
                  padding: "12px 14px",
                  height: 90,
                }}
              >
                <div style={{ animation: "pulse 1.5s ease-in-out infinite" }}>
                  <div style={{ width: "60%", height: 10, background: "var(--border)", borderRadius: 4, marginBottom: 8 }} />
                  <div style={{ width: "40%", height: 8, background: "var(--border)", borderRadius: 4, marginBottom: 12 }} />
                  <div style={{ width: "80%", height: 6, background: "var(--border)", borderRadius: 4 }} />
                </div>
              </div>
            ))}
          </>
        ) : (
          models.map((model, idx) => {
            const statusColor = getStatusColor(model.status);
            const isConnected = model.status === "connected";

            return (
              <div
                key={idx}
                style={{
                  background: "var(--bg-card-hover)",
                  border: `1px solid ${isConnected ? "rgba(34, 197, 94, 0.2)" : "rgba(239, 68, 68, 0.2)"}`,
                  borderRadius: 10,
                  padding: "12px 14px",
                  position: "relative",
                  overflow: "hidden",
                  transition: "all 0.3s ease",
                }}
              >
                {/* Status indicator pulse effect */}
                {isConnected && (
                  <div
                    style={{
                      position: "absolute",
                      top: 0,
                      left: 0,
                      right: 0,
                      height: 2,
                      background: statusColor,
                      animation: "pulse-glow 2s ease-in-out infinite",
                    }}
                  />
                )}

                <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 8 }}>
                  <div>
                    <div
                      style={{
                        fontSize: 10,
                        fontWeight: 700,
                        fontFamily: "Syne, sans-serif",
                        color: statusColor,
                        letterSpacing: "0.05em",
                        textTransform: "uppercase",
                        marginBottom: 4,
                      }}
                    >
                      Model #{idx + 1}
                    </div>
                    <h4
                      style={{
                        fontFamily: "Syne, sans-serif",
                        fontSize: 13,
                        fontWeight: 700,
                        color: "var(--text-primary)",
                        marginBottom: 2,
                      }}
                    >
                      {model.name.replace(`AI Model #${idx + 1}: `, "")}
                    </h4>
                  </div>

                  {/* Connection indicator */}
                  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <div
                      style={{
                        width: 8,
                        height: 8,
                        background: statusColor,
                        borderRadius: "50%",
                        boxShadow: `0 0 8px ${statusColor}`,
                        animation: isConnected ? "pulse-dot 2s ease-in-out infinite" : "none",
                      }}
                    />
                    {isConnected ? (
                      <CheckCircle size={14} color={statusColor} />
                    ) : (
                      <XCircle size={14} color={statusColor} />
                    )}
                  </div>
                </div>

                <p style={{ fontSize: 10, color: "var(--text-muted)", fontFamily: "DM Mono, monospace", marginBottom: 6 }}>
                  {model.type}
                </p>

                <div
                  style={{
                    fontSize: 10,
                    color: statusColor,
                    fontWeight: 600,
                    fontFamily: "Syne, sans-serif",
                    display: "flex",
                    alignItems: "center",
                    gap: 4,
                  }}
                >
                  <span style={{ fontSize: 8 }}>●</span>
                  {isConnected ? "ACTIVE" : "OFFLINE"}
                </div>
              </div>
            );
          })
        )}
      </div>

      <style jsx>{`
        @keyframes spin {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }

        @keyframes pulse {
          0%,
          100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }

        @keyframes pulse-glow {
          0%,
          100% {
            opacity: 0.8;
            box-shadow: 0 0 10px var(--green-primary);
          }
          50% {
            opacity: 1;
            box-shadow: 0 0 20px var(--green-primary);
          }
        }

        @keyframes pulse-dot {
          0%,
          100% {
            transform: scale(1);
            opacity: 1;
          }
          50% {
            transform: scale(1.2);
            opacity: 0.8;
          }
        }
      `}</style>
    </div>
  );
}
