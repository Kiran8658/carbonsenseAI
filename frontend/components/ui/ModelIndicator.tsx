import { Brain, CheckCircle, XCircle, AlertCircle } from "lucide-react";

interface ModelIndicatorProps {
  modelNumber: 1 | 2 | 3;
  modelName: string;
  status: "connected" | "disconnected" | "processing";
  compact?: boolean;
  showDetails?: boolean;
}

export default function ModelIndicator({
  modelNumber,
  modelName,
  status,
  compact = false,
  showDetails = false
}: ModelIndicatorProps) {
  const getColor = () => {
    switch (status) {
      case "connected": return "#22c55e";
      case "processing": return "#f59e0b";
      case "disconnected": return "#ef4444";
    }
  };

  const getIcon = () => {
    switch (status) {
      case "connected": return <CheckCircle size={compact ? 12 : 14} color={getColor()} />;
      case "processing": return <AlertCircle size={compact ? 12 : 14} color={getColor()} />;
      case "disconnected": return <XCircle size={compact ? 12 : 14} color={getColor()} />;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case "connected": return "ACTIVE";
      case "processing": return "PROCESSING";
      case "disconnected": return "OFFLINE";
    }
  };

  if (compact) {
    return (
      <div
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 6,
          background: `${getColor()}15`,
          border: `1px solid ${getColor()}40`,
          borderRadius: 6,
          padding: "4px 8px",
        }}
      >
        <div
          style={{
            width: 6,
            height: 6,
            background: getColor(),
            borderRadius: "50%",
            boxShadow: `0 0 8px ${getColor()}`,
            animation: status === "connected" ? "pulse-dot 2s ease-in-out infinite" : "none",
          }}
        />
        <span
          style={{
            fontSize: 10,
            fontWeight: 700,
            fontFamily: "Syne, sans-serif",
            color: getColor(),
            letterSpacing: "0.05em",
            textTransform: "uppercase",
          }}
        >
          AI Model #{modelNumber}
        </span>
        {getIcon()}
      </div>
    );
  }

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 10,
        background: `${getColor()}10`,
        border: `1px solid ${getColor()}30`,
        borderRadius: 8,
        padding: "8px 12px",
      }}
    >
      <div
        style={{
          width: 32,
          height: 32,
          background: `${getColor()}20`,
          border: `1px solid ${getColor()}40`,
          borderRadius: 8,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          position: "relative",
        }}
      >
        <Brain size={16} color={getColor()} />
        <div
          style={{
            position: "absolute",
            top: -2,
            right: -2,
            width: 10,
            height: 10,
            background: getColor(),
            borderRadius: "50%",
            border: "2px solid var(--bg-card)",
            boxShadow: `0 0 8px ${getColor()}`,
            animation: status === "connected" ? "pulse-dot 2s ease-in-out infinite" : "none",
          }}
        />
      </div>

      <div style={{ flex: 1 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 2 }}>
          <span
            style={{
              fontSize: 11,
              fontWeight: 700,
              fontFamily: "Syne, sans-serif",
              color: getColor(),
              letterSpacing: "0.05em",
              textTransform: "uppercase",
            }}
          >
            AI Model #{modelNumber}
          </span>
          {getIcon()}
        </div>
        <p
          style={{
            fontSize: 12,
            fontWeight: 600,
            fontFamily: "Syne, sans-serif",
            color: "var(--text-primary)",
            margin: 0,
          }}
        >
          {modelName}
        </p>
        {showDetails && (
          <p
            style={{
              fontSize: 10,
              color: getColor(),
              fontFamily: "DM Mono, monospace",
              margin: "2px 0 0 0",
              fontWeight: 600,
            }}
          >
            {getStatusText()}
          </p>
        )}
      </div>
    </div>
  );
}
