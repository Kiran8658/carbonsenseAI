import ConnectionLight from "../ui/ConnectionLight";
import { ModelConnectionStatus } from "../../lib/types";

interface ModelExecutionStep {
  step: number;
  title: string;
  modelName: string;
  modelType: string;
  inputLabel: string;
  outputLabel: string;
  outputValue?: string;
  status: ModelConnectionStatus;
}

interface ModelExecutionBoardProps {
  steps: ModelExecutionStep[];
}

export default function ModelExecutionBoard({ steps }: ModelExecutionBoardProps) {
  return (
    <div className="card" style={{ padding: 22, marginBottom: 18 }}>
      <div style={{ marginBottom: 14 }}>
        <h3
          style={{
            fontFamily: "Syne, sans-serif",
            fontSize: 17,
            fontWeight: 800,
            color: "var(--text-primary)",
            marginBottom: 4,
          }}
        >
          Model Execution Trace
        </h3>
        <p style={{ margin: 0, fontSize: 12, color: "var(--text-muted)" }}>
          Professional visibility into each AI step, model, connection, input, and output
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
        {steps.map((step) => {
          const border =
            step.status === "connected"
              ? "1px solid rgba(34, 197, 94, 0.35)"
              : step.status === "processing"
                ? "1px solid rgba(245, 158, 11, 0.35)"
                : "1px solid rgba(239, 68, 68, 0.35)";

          return (
            <div
              key={step.step}
              style={{
                border,
                borderRadius: 12,
                background: "var(--bg-card-hover)",
                padding: 14,
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                <span
                  style={{
                    fontSize: 11,
                    color: "var(--text-muted)",
                    fontFamily: "DM Mono, monospace",
                  }}
                >
                  STEP {step.step}
                </span>
                <ConnectionLight status={step.status} compact />
              </div>

              <h4 style={{ fontSize: 14, fontWeight: 800, fontFamily: "Syne, sans-serif", marginBottom: 4 }}>{step.title}</h4>
              <p style={{ margin: "0 0 10px 0", fontSize: 11, color: "var(--text-muted)", fontFamily: "DM Mono, monospace" }}>
                {step.modelName} • {step.modelType}
              </p>

              <p style={{ margin: "0 0 5px 0", fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Input
              </p>
              <p style={{ margin: "0 0 10px 0", fontSize: 12, color: "var(--text-secondary)" }}>{step.inputLabel}</p>

              <p style={{ margin: "0 0 5px 0", fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Output
              </p>
              <p style={{ margin: 0, fontSize: 12, color: "var(--text-primary)", fontWeight: 700 }}>
                {step.outputValue || `Waiting for ${step.outputLabel.toLowerCase()}...`}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
