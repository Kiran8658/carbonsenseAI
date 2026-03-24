import { Sparkles, Loader2, Leaf, Zap, Fuel, Settings } from "lucide-react";
import { Suggestion } from "../../lib/types";
import ConnectionLight from "../ui/ConnectionLight";
import { ModelConnectionStatus } from "../../lib/types";

interface AISuggestionsProps {
  suggestions: Suggestion[];
  summary: string;
  estimatedReduction: number;
  loading: boolean;
  onFetch: () => void;
  hasData: boolean;
  modelUsed?: string;
  model2Status?: ModelConnectionStatus;
}

const priorityClass: Record<string, string> = {
  Critical: "badge-critical",
  High: "badge-high",
  Medium: "badge-medium",
  Low: "badge-low",
};

const categoryIcon = (cat: string) => {
  if (cat === "Electricity") return <Zap size={14} color="#f59e0b" />;
  if (cat === "Fuel") return <Fuel size={14} color="#3b82f6" />;
  if (cat === "Offsets") return <Leaf size={14} color="#22c55e" />;
  return <Settings size={14} color="#94a3b8" />;
};

export default function AISuggestions({
  suggestions,
  summary,
  estimatedReduction,
  loading,
  onFetch,
  hasData,
  modelUsed,
  model2Status = "disconnected",
}: AISuggestionsProps) {
  return (
    <div className="card" style={{ padding: "28px" }}>
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: 20,
          flexWrap: "wrap",
          gap: 12,
        }}
      >
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
            <div
              style={{
                width: 32,
                height: 32,
                background: "linear-gradient(135deg, #22c55e22, #16a34a44)",
                border: "1px solid #22c55e44",
                borderRadius: 8,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Sparkles size={16} color="#22c55e" />
            </div>
            <h2
              style={{
                fontFamily: "Syne, sans-serif",
                fontSize: 18,
                fontWeight: 700,
                color: "var(--text-primary)",
              }}
            >
              AI Recommendations {modelUsed && `(${modelUsed})`}
            </h2>
          </div>
          <p style={{ fontSize: 13, color: "var(--text-muted)", marginLeft: 42 }}>
            Personalized strategies to cut your emissions
          </p>
          <div style={{ marginLeft: 42, marginTop: 8 }}>
            <ConnectionLight status={model2Status} label="Model 2" compact />
          </div>
        </div>

        <button
          className="btn-primary"
          onClick={onFetch}
          disabled={loading || !hasData}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            fontSize: 13,
            padding: "10px 18px",
          }}
        >
          {loading ? (
            <>
              <Loader2 size={14} style={{ animation: "spin 1s linear infinite" }} />
              Analyzing...
            </>
          ) : (
            <>
              <Sparkles size={14} />
              Get AI Insights
            </>
          )}
        </button>
      </div>

      {/* Empty state */}
      {!hasData && !loading && suggestions.length === 0 && (
        <div
          style={{
            padding: "40px 24px",
            textAlign: "center",
            border: "1px dashed var(--border)",
            borderRadius: 12,
          }}
        >
          <Sparkles size={32} color="var(--text-muted)" style={{ margin: "0 auto 12px" }} />
          <p style={{ color: "var(--text-muted)", fontSize: 14 }}>
            Calculate your emissions first, then get AI-powered recommendations
          </p>
        </div>
      )}

      {/* Summary banner */}
      {summary && !loading && (
        <div
          style={{
            background: "linear-gradient(135deg, #22c55e0f, #16a34a08)",
            border: "1px solid #22c55e22",
            borderRadius: 12,
            padding: "14px 18px",
            marginBottom: 20,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: 16,
            flexWrap: "wrap",
          }}
        >
          <p style={{ fontSize: 13, color: "var(--text-secondary)", flex: 1 }}>{summary}</p>
          <div style={{ textAlign: "center", flexShrink: 0 }}>
            <div
              style={{
                fontSize: 24,
                fontWeight: 800,
                fontFamily: "Syne, sans-serif",
                color: "#22c55e",
                lineHeight: 1,
              }}
            >
              -{estimatedReduction.toFixed(0)}%
            </div>
            <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
              potential reduction
            </div>
          </div>
        </div>
      )}

      {/* Suggestions list */}
      {suggestions.length > 0 && !loading && (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {suggestions.map((s, i) => (
            <div
              key={i}
              style={{
                background: "#0d1826",
                border: "1px solid var(--border)",
                borderRadius: 12,
                padding: "16px 18px",
                transition: "border-color 0.2s",
                animationDelay: `${i * 80}ms`,
              }}
              className="animate-count"
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLDivElement).style.borderColor = "var(--border-light)";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLDivElement).style.borderColor = "var(--border)";
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                  gap: 12,
                  flexWrap: "wrap",
                }}
              >
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                    {categoryIcon(s.category)}
                    <h4
                      style={{
                        fontFamily: "Syne, sans-serif",
                        fontSize: 14,
                        fontWeight: 700,
                        color: "var(--text-primary)",
                      }}
                    >
                      {s.title}
                    </h4>
                  </div>
                  <p style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.5, marginBottom: 8 }}>
                    {s.description}
                  </p>
                  <p
                    style={{
                      fontSize: 12,
                      color: "#22c55e",
                      fontFamily: "DM Mono, monospace",
                    }}
                  >
                    ↓ {s.impact}
                  </p>
                </div>

                <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 8, flexShrink: 0 }}>
                  <span className={`badge ${priorityClass[s.priority] || "badge-low"}`}>
                    {s.priority}
                  </span>
                  <div
                    style={{
                      background: "#22c55e15",
                      border: "1px solid #22c55e33",
                      borderRadius: 8,
                      padding: "4px 10px",
                      textAlign: "center",
                    }}
                  >
                    <div
                      style={{
                        fontSize: 16,
                        fontWeight: 800,
                        fontFamily: "Syne, sans-serif",
                        color: "#22c55e",
                        lineHeight: 1,
                      }}
                    >
                      -{s.savings_percentage}%
                    </div>
                    <div style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 1 }}>savings</div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
