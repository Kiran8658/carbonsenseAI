import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { EmissionData } from "../../lib/types";
import ConnectionLight from "../ui/ConnectionLight";
import { ModelConnectionStatus } from "../../lib/types";

interface PieBreakdownProps {
  data: EmissionData;
  model1Status?: ModelConnectionStatus;
}

const COLORS = ["#f59e0b", "#3b82f6"];

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    return (
      <div
        style={{
          background: "var(--bg-card)",
          border: "1px solid var(--border-light)",
          borderRadius: 10,
          padding: "10px 16px",
        }}
      >
        <p style={{ color: payload[0].fill, fontFamily: "Syne, sans-serif", fontWeight: 700, fontSize: 13 }}>
          {payload[0].name}
        </p>
        <p style={{ color: "var(--text-primary)", fontFamily: "DM Mono, monospace", fontSize: 14, marginTop: 2 }}>
          {payload[0].value.toFixed(1)} kg CO₂
        </p>
        <p style={{ color: "var(--text-muted)", fontSize: 12, marginTop: 2 }}>
          {payload[0].payload.pct}% of total
        </p>
      </div>
    );
  }
  return null;
};

export default function PieBreakdown({ data, model1Status = "disconnected" }: PieBreakdownProps) {
  const chartData = [
    {
      name: "Electricity",
      value: data.electricity_co2,
      pct: data.breakdown_percentage.electricity,
    },
    {
      name: "Fuel",
      value: data.fuel_co2,
      pct: data.breakdown_percentage.fuel,
    },
  ];

  return (
    <div className="card" style={{ padding: "24px" }}>
      <div style={{ marginBottom: 20 }}>
        <h3
          style={{
            fontFamily: "Syne, sans-serif",
            fontSize: 16,
            fontWeight: 700,
            color: "var(--text-primary)",
            marginBottom: 2,
          }}
        >
          Emission Breakdown
        </h3>
        <p style={{ fontSize: 12, color: "var(--text-muted)" }}>By source this month</p>
        <div style={{ marginTop: 8 }}>
          <ConnectionLight status={model1Status} label="Model 1 source attribution" compact />
        </div>
      </div>

      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={4}
            dataKey="value"
            strokeWidth={0}
          >
            {chartData.map((entry, index) => (
              <Cell
                key={entry.name}
                fill={COLORS[index]}
                style={{ filter: `drop-shadow(0 0 6px ${COLORS[index]}66)` }}
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            iconType="circle"
            iconSize={8}
            formatter={(value) => (
              <span style={{ color: "var(--text-secondary)", fontFamily: "Syne, sans-serif", fontSize: 12 }}>
                {value}
              </span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>

      {/* Stats row */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 8 }}>
        {chartData.map((item, i) => (
          <div
            key={item.name}
            style={{
              background: "#0d1826",
              borderRadius: 10,
              padding: "12px 14px",
              border: `1px solid ${COLORS[i]}33`,
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                marginBottom: 4,
              }}
            >
              <div
                style={{ width: 8, height: 8, borderRadius: "50%", background: COLORS[i] }}
              />
              <span
                style={{
                  fontSize: 11,
                  fontFamily: "Syne, sans-serif",
                  fontWeight: 700,
                  color: COLORS[i],
                  letterSpacing: "0.06em",
                  textTransform: "uppercase",
                }}
              >
                {item.name}
              </span>
            </div>
            <p
              style={{
                fontSize: 20,
                fontWeight: 800,
                fontFamily: "Syne, sans-serif",
                color: "var(--text-primary)",
                lineHeight: 1,
              }}
            >
              {item.value.toFixed(1)}
              <span style={{ fontSize: 11, color: "var(--text-muted)", fontWeight: 400, marginLeft: 4 }}>
                kg CO₂
              </span>
            </p>
            <p style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
              {item.pct}% share
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
