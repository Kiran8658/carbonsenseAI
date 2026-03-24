import { ReactNode } from "react";

interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  icon?: ReactNode;
  color?: string;
  subtitle?: string;
  delay?: number;
}

export default function MetricCard({
  label,
  value,
  unit,
  icon,
  color = "var(--green-primary)",
  subtitle,
  delay = 0,
}: MetricCardProps) {
  return (
    <div
      className="card animate-count"
      style={{
        padding: "24px",
        animationDelay: `${delay}ms`,
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Top accent line */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: 2,
          background: `linear-gradient(90deg, ${color}, transparent)`,
          opacity: 0.7,
        }}
      />

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div style={{ flex: 1 }}>
          <p
            style={{
              fontSize: 12,
              fontWeight: 600,
              fontFamily: "Syne, sans-serif",
              color: "var(--text-muted)",
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              marginBottom: 8,
            }}
          >
            {label}
          </p>
          <div style={{ display: "flex", alignItems: "baseline", gap: 6 }}>
            <span
              style={{
                fontSize: 32,
                fontWeight: 800,
                fontFamily: "Syne, sans-serif",
                color: "var(--text-primary)",
                lineHeight: 1,
                letterSpacing: "-0.02em",
              }}
            >
              {value}
            </span>
            {unit && (
              <span
                style={{
                  fontSize: 13,
                  color: "var(--text-muted)",
                  fontFamily: "DM Mono, monospace",
                }}
              >
                {unit}
              </span>
            )}
          </div>
          {subtitle && (
            <p style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 6 }}>
              {subtitle}
            </p>
          )}
        </div>

        {icon && (
          <div
            style={{
              width: 44,
              height: 44,
              background: `rgba(${color === "var(--green-primary)" ? "34,197,94" : "59,130,246"}, 0.1)`,
              border: `1px solid ${color}33`,
              borderRadius: 12,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexShrink: 0,
            }}
          >
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}
