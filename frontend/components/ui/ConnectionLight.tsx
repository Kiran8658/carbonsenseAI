interface ConnectionLightProps {
  status: "connected" | "disconnected" | "processing";
  label?: string;
  compact?: boolean;
}

export default function ConnectionLight({ status, label, compact = false }: ConnectionLightProps) {
  const color = status === "connected" ? "#22c55e" : status === "processing" ? "#f59e0b" : "#ef4444";
  const text = status === "connected" ? "Connected" : status === "processing" ? "Processing" : "Disconnected";

  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: compact ? 6 : 8,
        padding: compact ? "4px 8px" : "6px 10px",
        borderRadius: 999,
        border: `1px solid ${color}55`,
        background: `${color}1a`,
      }}
    >
      <span
        style={{
          width: compact ? 7 : 8,
          height: compact ? 7 : 8,
          borderRadius: "50%",
          background: color,
          boxShadow: `0 0 8px ${color}`,
          animation: status === "connected" ? "pulse-dot 2s ease-in-out infinite" : "none",
        }}
      />
      <span
        style={{
          fontSize: compact ? 10 : 11,
          color,
          fontFamily: "Syne, sans-serif",
          fontWeight: 700,
          letterSpacing: "0.04em",
          textTransform: "uppercase",
        }}
      >
        {label ? `${label}: ${text}` : text}
      </span>
    </div>
  );
}
