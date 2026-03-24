import { ArrowRight, Zap, Target, TrendingUp } from "lucide-react";
import ModelIndicator from "../ui/ModelIndicator";

interface AIPipelineProps {
  step1Status: "connected" | "disconnected" | "processing";
  step2Status: "connected" | "disconnected" | "processing";
  step3Status: "connected" | "disconnected" | "processing";
  step1Result?: string;
  step2Result?: string;
  step3Result?: string;
}

export default function AIPipeline({
  step1Status,
  step2Status,
  step3Status,
  step1Result,
  step2Result,
  step3Result,
}: AIPipelineProps) {
  return (
    <div
      style={{
        background: "linear-gradient(135deg, rgba(34, 197, 94, 0.05), rgba(59, 130, 246, 0.05))",
        border: "1px solid var(--border)",
        borderRadius: 16,
        padding: 24,
        marginBottom: 24,
      }}
    >
      <div style={{ marginBottom: 20 }}>
        <h3
          style={{
            fontFamily: "Syne, sans-serif",
            fontSize: 18,
            fontWeight: 800,
            color: "var(--text-primary)",
            marginBottom: 6,
          }}
        >
          AI Processing Pipeline
        </h3>
        <p style={{ fontSize: 13, color: "var(--text-muted)", margin: 0 }}>
          Real-time 3-stage ML inference with live model status monitoring
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr auto 1fr auto 1fr", gap: 16, alignItems: "center" }}>
        {/* Step 1: Emissions Predictor */}
        <div
          className="card"
          style={{
            padding: 16,
            background: "var(--bg-card)",
            border: step1Status === "connected" ? "1px solid rgba(34, 197, 94, 0.3)" : "1px solid var(--border)",
            position: "relative",
            overflow: "hidden",
          }}
        >
          {step1Status === "processing" && (
            <div
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                right: 0,
                height: 2,
                background: "linear-gradient(90deg, #22c55e, #86efac, #22c55e)",
                backgroundSize: "200% 100%",
                animation: "gradient-flow 2s linear infinite",
              }}
            />
          )}

          <div style={{ marginBottom: 12 }}>
            <ModelIndicator
              modelNumber={1}
              modelName="Emissions Predictor"
              status={step1Status}
              compact
            />
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
            <div
              style={{
                width: 32,
                height: 32,
                background: "rgba(34, 197, 94, 0.15)",
                borderRadius: 8,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Zap size={16} color="#22c55e" />
            </div>
            <div>
              <p style={{ fontSize: 11, color: "var(--text-muted)", margin: 0, fontFamily: "DM Mono, monospace" }}>
                RandomForest ML
              </p>
            </div>
          </div>

          {step1Result ? (
            <div
              style={{
                background: "rgba(34, 197, 94, 0.1)",
                border: "1px solid rgba(34, 197, 94, 0.2)",
                borderRadius: 8,
                padding: "8px 12px",
              }}
            >
              <p style={{ fontSize: 10, color: "var(--text-muted)", margin: "0 0 4px 0" }}>Prediction:</p>
              <p
                style={{
                  fontSize: 16,
                  fontWeight: 800,
                  fontFamily: "Syne, sans-serif",
                  color: "#22c55e",
                  margin: 0,
                }}
              >
                {step1Result}
              </p>
            </div>
          ) : (
            <div
              style={{
                background: "var(--bg-card-hover)",
                borderRadius: 8,
                padding: "8px 12px",
                textAlign: "center",
              }}
            >
              <p style={{ fontSize: 11, color: "var(--text-muted)", margin: 0 }}>Awaiting input...</p>
            </div>
          )}
        </div>

        {/* Arrow 1 */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
          <ArrowRight
            size={24}
            color={step1Status === "connected" && step1Result ? "var(--green-primary)" : "var(--text-muted)"}
            style={{ opacity: step1Status === "connected" && step1Result ? 1 : 0.3 }}
          />
        </div>

        {/* Step 2: Carbon Scorer */}
        <div
          className="card"
          style={{
            padding: 16,
            background: "var(--bg-card)",
            border: step2Status === "connected" ? "1px solid rgba(59, 130, 246, 0.3)" : "1px solid var(--border)",
            position: "relative",
            overflow: "hidden",
          }}
        >
          {step2Status === "processing" && (
            <div
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                right: 0,
                height: 2,
                background: "linear-gradient(90deg, #3b82f6, #93c5fd, #3b82f6)",
                backgroundSize: "200% 100%",
                animation: "gradient-flow 2s linear infinite",
              }}
            />
          )}

          <div style={{ marginBottom: 12 }}>
            <ModelIndicator
              modelNumber={2}
              modelName="Carbon Scorer"
              status={step2Status}
              compact
            />
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
            <div
              style={{
                width: 32,
                height: 32,
                background: "rgba(59, 130, 246, 0.15)",
                borderRadius: 8,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Target size={16} color="#3b82f6" />
            </div>
            <div>
              <p style={{ fontSize: 11, color: "var(--text-muted)", margin: 0, fontFamily: "DM Mono, monospace" }}>
                Smart Algorithm
              </p>
            </div>
          </div>

          {step2Result ? (
            <div
              style={{
                background: "rgba(59, 130, 246, 0.1)",
                border: "1px solid rgba(59, 130, 246, 0.2)",
                borderRadius: 8,
                padding: "8px 12px",
              }}
            >
              <p style={{ fontSize: 10, color: "var(--text-muted)", margin: "0 0 4px 0" }}>Score:</p>
              <p
                style={{
                  fontSize: 16,
                  fontWeight: 800,
                  fontFamily: "Syne, sans-serif",
                  color: "#3b82f6",
                  margin: 0,
                }}
              >
                {step2Result}
              </p>
            </div>
          ) : (
            <div
              style={{
                background: "var(--bg-card-hover)",
                borderRadius: 8,
                padding: "8px 12px",
                textAlign: "center",
              }}
            >
              <p style={{ fontSize: 11, color: "var(--text-muted)", margin: 0 }}>Awaiting data...</p>
            </div>
          )}
        </div>

        {/* Arrow 2 */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
          <ArrowRight
            size={24}
            color={step2Status === "connected" && step2Result ? "var(--green-primary)" : "var(--text-muted)"}
            style={{ opacity: step2Status === "connected" && step2Result ? 1 : 0.3 }}
          />
        </div>

        {/* Step 3: Trend Forecaster */}
        <div
          className="card"
          style={{
            padding: 16,
            background: "var(--bg-card)",
            border: step3Status === "connected" ? "1px solid rgba(168, 85, 247, 0.3)" : "1px solid var(--border)",
            position: "relative",
            overflow: "hidden",
          }}
        >
          {step3Status === "processing" && (
            <div
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                right: 0,
                height: 2,
                background: "linear-gradient(90deg, #a855f7, #d8b4fe, #a855f7)",
                backgroundSize: "200% 100%",
                animation: "gradient-flow 2s linear infinite",
              }}
            />
          )}

          <div style={{ marginBottom: 12 }}>
            <ModelIndicator
              modelNumber={3}
              modelName="Trend Forecaster"
              status={step3Status}
              compact
            />
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
            <div
              style={{
                width: 32,
                height: 32,
                background: "rgba(168, 85, 247, 0.15)",
                borderRadius: 8,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <TrendingUp size={16} color="#a855f7" />
            </div>
            <div>
              <p style={{ fontSize: 11, color: "var(--text-muted)", margin: 0, fontFamily: "DM Mono, monospace" }}>
                XGBoost/LSTM
              </p>
            </div>
          </div>

          {step3Result ? (
            <div
              style={{
                background: "rgba(168, 85, 247, 0.1)",
                border: "1px solid rgba(168, 85, 247, 0.2)",
                borderRadius: 8,
                padding: "8px 12px",
              }}
            >
              <p style={{ fontSize: 10, color: "var(--text-muted)", margin: "0 0 4px 0" }}>Forecast:</p>
              <p
                style={{
                  fontSize: 16,
                  fontWeight: 800,
                  fontFamily: "Syne, sans-serif",
                  color: "#a855f7",
                  margin: 0,
                }}
              >
                {step3Result}
              </p>
            </div>
          ) : (
            <div
              style={{
                background: "var(--bg-card-hover)",
                borderRadius: 8,
                padding: "8px 12px",
                textAlign: "center",
              }}
            >
              <p style={{ fontSize: 11, color: "var(--text-muted)", margin: 0 }}>Awaiting data...</p>
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        @keyframes gradient-flow {
          0% {
            background-position: 0% 50%;
          }
          100% {
            background-position: 200% 50%;
          }
        }

        @keyframes pulse-dot {
          0%, 100% {
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
