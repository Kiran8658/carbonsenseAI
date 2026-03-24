import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
} from "recharts";
import { HistoryEntry } from "../../lib/types";
import ConnectionLight from "../ui/ConnectionLight";
import { ModelConnectionStatus } from "../../lib/types";

interface TrendChartProps {
  history: HistoryEntry[];
  forecast?: number[];
  modelUsed?: string;
  currentMonth?: { electricity_co2: number; fuel_co2: number; total_co2: number };
  model3Status?: ModelConnectionStatus;
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div
        style={{
          background: "var(--bg-card)",
          border: "1px solid var(--border-light)",
          borderRadius: 10,
          padding: "12px 16px",
        }}
      >
        <p
          style={{
            fontFamily: "Syne, sans-serif",
            fontWeight: 700,
            fontSize: 13,
            color: "var(--text-primary)",
            marginBottom: 8,
          }}
        >
          {label}
        </p>
        {payload.map((p: any) => (
          <div
            key={p.dataKey}
            style={{ display: "flex", justifyContent: "space-between", gap: 20, marginBottom: 4 }}
          >
            <span style={{ color: p.color, fontSize: 12, fontFamily: "Syne, sans-serif" }}>
              {p.name}
            </span>
            <span style={{ color: "var(--text-primary)", fontFamily: "DM Mono, monospace", fontSize: 12 }}>
              {p.value.toFixed(0)} kg
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export default function TrendChart({ history, forecast, modelUsed, currentMonth, model3Status = "disconnected" }: TrendChartProps) {
  // Inject the current calculation as the last data point
  const chartData = history.map((h) => ({
    month: h.month.replace(" 2024", "").replace(" 2025", ""),
    electricity: h.electricity_co2,
    fuel: h.fuel_co2,
    total: h.total_co2,
    isForecast: false,
  }));

  if (currentMonth && currentMonth.total_co2 > 0) {
    chartData[chartData.length - 1] = {
      month: "Jan ★",
      electricity: currentMonth.electricity_co2,
      fuel: currentMonth.fuel_co2,
      total: currentMonth.total_co2,
      isForecast: false,
    };
  }

  // Add forecast data from Model 3 if available
  if (forecast && forecast.length > 0) {
    const forecastMonths = ["Feb", "Mar", "Apr", "May", "Jun", "Jul"];
    forecast.slice(0, 6).forEach((value, index) => {
      chartData.push({
        month: forecastMonths[index] || `M${index + 2}`,
        electricity: 0,
        fuel: 0,
        total: typeof value === "number" ? value : 0,
        isForecast: true,
      });
    });
  }

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
          Emission Trend {modelUsed && `(${modelUsed})`}
        </h3>
        <p style={{ fontSize: 12, color: "var(--text-muted)" }}>
          6-month historical view + {forecast?.length || 0} months forecast (kg CO₂)
        </p>
        <div style={{ marginTop: 8 }}>
          <ConnectionLight status={model3Status} label="Model 3 forecast engine" compact />
        </div>
      </div>

      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={chartData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="gradTotal" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#22c55e" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="gradElec" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.15} />
              <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="gradForecast" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="month"
            tick={{ fill: "var(--text-muted)", fontSize: 11, fontFamily: "DM Mono, monospace" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "var(--text-muted)", fontSize: 11, fontFamily: "DM Mono, monospace" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            iconType="circle"
            iconSize={7}
            formatter={(value) => (
              <span style={{ color: "var(--text-secondary)", fontFamily: "Syne, sans-serif", fontSize: 11 }}>
                {value}
              </span>
            )}
          />
          <Area
            type="monotone"
            dataKey="total"
            name="Total"
            stroke="#22c55e"
            strokeWidth={2.5}
            fill="url(#gradTotal)"
            dot={{ fill: "#22c55e", r: 3, strokeWidth: 0 }}
            activeDot={{ r: 5, fill: "#22c55e", stroke: "#0a0f1a", strokeWidth: 2 }}
          />
          <Area
            type="monotone"
            dataKey="electricity"
            name="Electricity"
            stroke="#f59e0b"
            strokeWidth={1.5}
            strokeDasharray="4 2"
            fill="url(#gradElec)"
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="fuel"
            name="Fuel"
            stroke="#3b82f6"
            strokeWidth={1.5}
            strokeDasharray="4 2"
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>

      {forecast && forecast.length > 0 && (
        <div
          style={{
            marginTop: 16,
            padding: "12px 16px",
            background: "#8b5cf615",
            border: "1px solid #8b5cf633",
            borderRadius: 8,
            fontSize: 12,
            color: "var(--text-secondary)",
          }}
        >
          ✨ <strong>ML Forecast:</strong> Next {forecast.length} months predicted using {modelUsed || "Model 3"}
        </div>
      )}
    </div>
  );
}
