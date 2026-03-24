import { SCORE_COLORS } from "../../lib/types";

interface ScoreRingProps {
  score: string;
  value: number;
}

export default function ScoreRing({ score, value }: ScoreRingProps) {
  const color = SCORE_COLORS[score] || "#22c55e";
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;

  return (
    <div
      className="card"
      style={{
        padding: "28px 24px",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 16,
        position: "relative",
        overflow: "hidden",
      }}
    >
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

      <p
        style={{
          fontSize: 12,
          fontWeight: 600,
          fontFamily: "Syne, sans-serif",
          color: "var(--text-muted)",
          letterSpacing: "0.08em",
          textTransform: "uppercase",
          alignSelf: "flex-start",
        }}
      >
        Carbon Score
      </p>

      <div style={{ position: "relative", width: 140, height: 140 }}>
        {/* Glow */}
        <div
          style={{
            position: "absolute",
            inset: 20,
            borderRadius: "50%",
            background: `${color}18`,
            filter: "blur(8px)",
          }}
        />
        <svg width="140" height="140" style={{ transform: "rotate(-90deg)" }}>
          {/* Track */}
          <circle
            cx="70" cy="70" r={radius}
            fill="none"
            stroke="var(--border)"
            strokeWidth="10"
          />
          {/* Progress */}
          <circle
            cx="70" cy="70" r={radius}
            fill="none"
            stroke={color}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="score-ring"
            style={{ filter: `drop-shadow(0 0 6px ${color}88)` }}
          />
        </svg>
        {/* Center text */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <span
            style={{
              fontSize: 28,
              fontWeight: 800,
              fontFamily: "Syne, sans-serif",
              color,
              lineHeight: 1,
            }}
          >
            {value}
          </span>
          <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "DM Mono, monospace" }}>
            /100
          </span>
        </div>
      </div>

      <div style={{ textAlign: "center" }}>
        <div
          style={{
            display: "inline-block",
            background: `${color}1a`,
            border: `1px solid ${color}44`,
            borderRadius: 20,
            padding: "4px 16px",
          }}
        >
          <span
            style={{
              color,
              fontFamily: "Syne, sans-serif",
              fontWeight: 700,
              fontSize: 14,
              letterSpacing: "0.04em",
            }}
          >
            {score}
          </span>
        </div>
        <p
          style={{
            marginTop: 8,
            fontSize: 12,
            color: "var(--text-muted)",
            maxWidth: 140,
            textAlign: "center",
          }}
        >
          {score === "Excellent" && "Minimal impact — keep it up!"}
          {score === "Good" && "Below average — small wins ahead"}
          {score === "Average" && "Room to improve significantly"}
          {score === "Poor" && "Urgent action recommended"}
          {score === "Critical" && "Immediate intervention needed"}
        </p>
      </div>
    </div>
  );
}
