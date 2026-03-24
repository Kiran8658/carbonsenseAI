import { useState, useEffect } from "react";
import Head from "next/head";
import { Zap, Fuel, Leaf, Activity, Sparkles } from "lucide-react";
import Navbar from "../components/ui/Navbar";
import SystemStatus from "../components/dashboard/SystemStatus";
import AIPipeline from "../components/dashboard/AIPipeline";
import ModelIndicator from "../components/ui/ModelIndicator";
import InputForm from "../components/dashboard/InputForm";
import MetricCard from "../components/ui/MetricCard";
import ScoreRing from "../components/ui/ScoreRing";
import PieBreakdown from "../components/charts/PieBreakdown";
import TrendChart from "../components/charts/TrendChart";
import AISuggestions from "../components/dashboard/AISuggestions";
import Simulator from "../components/dashboard/Simulator";
import ReportButton from "../components/dashboard/ReportButton";
import { calculateEmissions, getAISuggestions, getHealthStatus, getHistory } from "../lib/api";
import { EmissionData, Suggestion, HistoryEntry } from "../lib/types";

export default function Home() {
  const [emissionData, setEmissionData] = useState<EmissionData | null>(null);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [summary, setSummary] = useState("");
  const [estimatedReduction, setEstimatedReduction] = useState(0);
  const [suggestionsModelUsed, setSuggestionsModelUsed] = useState<string>("");
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [forecast, setForecast] = useState<number[]>([]);
  const [trendModelUsed, setTrendModelUsed] = useState<string>("");
  const [calcLoading, setCalcLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [inputs, setInputs] = useState({ electricity: 0, fuel: 0 });

  // Model status states
  const [model1Status, setModel1Status] = useState<"connected" | "disconnected" | "processing">("disconnected");
  const [model2Status, setModel2Status] = useState<"connected" | "disconnected" | "processing">("disconnected");
  const [model3Status, setModel3Status] = useState<"connected" | "disconnected" | "processing">("disconnected");

  useEffect(() => {
    // Check backend health on mount
    checkModelsHealth();

    getHistory()
      .then((d) => {
        setHistory(d.history);
        setForecast(d.forecast || []);
        setTrendModelUsed(d.model_used || "");
        if (d.forecast && d.forecast.length > 0) {
          setModel3Status("connected");
        }
      })
      .catch(() => {});
  }, []);

  const checkModelsHealth = async () => {
    try {
      const data = await getHealthStatus();

      setModel1Status(data.details.emissions_predictor.status === "connected" ? "connected" : "disconnected");
      setModel2Status(data.details.carbon_scorer.status === "connected" ? "connected" : "disconnected");
      setModel3Status(data.details.trend_forecaster.status === "connected" ? "connected" : "disconnected");
    } catch (error) {
      console.error("Health check failed:", error);
      setModel1Status("disconnected");
      setModel2Status("disconnected");
      setModel3Status("disconnected");
    }
  };

  const handleCalculate = async (electricity: number, fuel: number) => {
    setCalcLoading(true);
    setInputs({ electricity, fuel });

    // Set models to processing state
    setModel1Status("processing");
    setModel2Status("processing");

    try {
      const res = await calculateEmissions(electricity, fuel);
      setEmissionData(res.data);

      // Models succeeded
      setModel1Status("connected");
      setModel2Status("connected");
    } catch (e) {
      console.error(e);
      alert("Could not connect to backend. Make sure FastAPI is running on port 8000.");
      setModel1Status("disconnected");
      setModel2Status("disconnected");
    } finally {
      setCalcLoading(false);
    }
  };

  const handleAISuggestions = async () => {
    if (!emissionData) return;
    setAiLoading(true);
    try {
      const res = await getAISuggestions({
        electricity_kwh: inputs.electricity,
        fuel_litres: inputs.fuel,
        total_co2: emissionData.total_co2,
      });
      setSuggestions(res.suggestions);
      setSummary(res.summary);
      setEstimatedReduction(res.estimated_reduction);
      setSuggestionsModelUsed(res.model_used || "");
    } catch (e) {
      console.error(e);
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>CarbonSense AI — Professional MSME Carbon Tracker</title>
        <meta name="description" content="3 AI models for intelligent carbon footprint tracking" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🌿</text></svg>" />
      </Head>

      <div style={{ minHeight: "100vh", background: "var(--bg-primary)" }} className="dot-pattern">
        <Navbar />

        <main style={{ maxWidth: 1400, margin: "0 auto", padding: "24px 24px 64px" }}>
          {/* Header */}
          <div style={{ marginBottom: 24 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
                  <div
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 8,
                      background: "var(--green-glow)",
                      border: "1px solid var(--green-dim)",
                      borderRadius: 20,
                      padding: "4px 14px",
                    }}
                  >
                    <Sparkles size={12} color="var(--green-primary)" />
                    <span
                      style={{
                        fontSize: 11,
                        fontFamily: "Syne, sans-serif",
                        fontWeight: 700,
                        color: "var(--green-primary)",
                        letterSpacing: "0.08em",
                        textTransform: "uppercase",
                      }}
                    >
                      Hackathon Demo • 3 AI Models
                    </span>
                  </div>
                </div>
                <h1
                  style={{
                    fontFamily: "Syne, sans-serif",
                    fontSize: "clamp(32px, 5vw, 48px)",
                    fontWeight: 800,
                    color: "var(--text-primary)",
                    lineHeight: 1.1,
                    letterSpacing: "-0.03em",
                    marginBottom: 8,
                  }}
                >
                  CarbonSense AI{" "}
                  <span
                    style={{
                      background: "linear-gradient(135deg, #22c55e, #3b82f6, #a855f7)",
                      WebkitBackgroundClip: "text",
                      WebkitTextFillColor: "transparent",
                    }}
                  >
                    Dashboard
                  </span>
                </h1>
                <p style={{ fontSize: 15, color: "var(--text-secondary)", maxWidth: 600, lineHeight: 1.6 }}>
                  Professional AI-powered carbon tracking with real-time model monitoring, intelligent predictions, and actionable insights for MSMEs.
                </p>
              </div>

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  background: "var(--bg-card)",
                  border: "1px solid var(--border)",
                  borderRadius: 12,
                  padding: "12px 16px",
                }}
              >
                <Activity size={20} color="var(--green-primary)" />
                <div>
                  <p style={{ fontSize: 11, color: "var(--text-muted)", margin: 0 }}>System Status</p>
                  <p
                    style={{
                      fontSize: 14,
                      fontWeight: 700,
                      fontFamily: "Syne, sans-serif",
                      color: "var(--green-primary)",
                      margin: 0,
                    }}
                  >
                    {model1Status === "connected" && model2Status === "connected" && model3Status === "connected"
                      ? "All Systems Online"
                      : "Checking..."}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* System Status Dashboard */}
          <SystemStatus />

          {/* AI Processing Pipeline */}
          <AIPipeline
            step1Status={model1Status}
            step2Status={model2Status}
            step3Status={model3Status}
            step1Result={emissionData ? `${emissionData.total_co2.toFixed(1)} kg CO₂` : undefined}
            step2Result={emissionData ? `${emissionData.carbon_score} (${emissionData.carbon_score_value}/100)` : undefined}
            step3Result={forecast.length > 0 ? `${forecast.length} months` : undefined}
          />

          {/* Main Grid: Input + Results */}
          <div style={{ display: "grid", gridTemplateColumns: "380px 1fr", gap: 20, marginBottom: 20 }}>
            {/* Left: Input Form */}
            <div>
              <div
                className="card"
                style={{
                  padding: "20px 24px",
                  marginBottom: 16,
                  border: "1px solid var(--border)",
                }}
              >
                <div style={{ marginBottom: 16 }}>
                  <h3
                    style={{
                      fontFamily: "Syne, sans-serif",
                      fontSize: 18,
                      fontWeight: 700,
                      color: "var(--text-primary)",
                      marginBottom: 6,
                    }}
                  >
                    Data Input
                  </h3>
                  <p style={{ fontSize: 12, color: "var(--text-muted)", margin: 0 }}>
                    Enter monthly consumption to analyze with AI
                  </p>
                </div>
                <InputForm onSubmit={handleCalculate} loading={calcLoading} />
              </div>

              {/* Model 1 Indicator */}
              <div style={{ marginBottom: 16 }}>
                <ModelIndicator
                  modelNumber={1}
                  modelName="Emissions Predictor"
                  status={model1Status}
                  showDetails
                />
              </div>

              {/* Model 2 Indicator */}
              <div style={{ marginBottom: 16 }}>
                <ModelIndicator
                  modelNumber={2}
                  modelName="Carbon Scorer"
                  status={model2Status}
                  showDetails
                />
              </div>

              {/* Model 3 Indicator */}
              <ModelIndicator
                modelNumber={3}
                modelName="Trend Forecaster"
                status={model3Status}
                showDetails
              />
            </div>

            {/* Right: Results */}
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              {/* Metrics Row */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14 }}>
                <div style={{ position: "relative" }}>
                  <div style={{ position: "absolute", top: 8, right: 8, zIndex: 10 }}>
                    <ModelIndicator modelNumber={1} modelName="" status={model1Status} compact />
                  </div>
                  <MetricCard
                    label="Total CO₂"
                    value={emissionData ? emissionData.total_co2.toFixed(1) : "—"}
                    unit="kg/mo"
                    icon={<Leaf size={20} color="var(--green-primary)" />}
                    subtitle={emissionData ? "AI Predicted" : "Awaiting input"}
                    delay={0}
                  />
                </div>

                <div style={{ position: "relative" }}>
                  <div style={{ position: "absolute", top: 8, right: 8, zIndex: 10 }}>
                    <ModelIndicator modelNumber={1} modelName="" status={model1Status} compact />
                  </div>
                  <MetricCard
                    label="Electricity"
                    value={emissionData ? emissionData.electricity_co2.toFixed(1) : "—"}
                    unit="kg CO₂"
                    icon={<Zap size={20} color="#f59e0b" />}
                    color="#f59e0b"
                    subtitle={emissionData ? `${emissionData.breakdown_percentage.electricity}% share` : ""}
                    delay={100}
                  />
                </div>

                <div style={{ position: "relative" }}>
                  <div style={{ position: "absolute", top: 8, right: 8, zIndex: 10 }}>
                    <ModelIndicator modelNumber={1} modelName="" status={model1Status} compact />
                  </div>
                  <MetricCard
                    label="Fuel"
                    value={emissionData ? emissionData.fuel_co2.toFixed(1) : "—"}
                    unit="kg CO₂"
                    icon={<Fuel size={20} color="#3b82f6" />}
                    color="#3b82f6"
                    subtitle={emissionData ? `${emissionData.breakdown_percentage.fuel}% share` : ""}
                    delay={200}
                  />
                </div>
              </div>

              {/* Score + Pie */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1.6fr", gap: 14 }}>
                <div style={{ position: "relative" }}>
                  <div style={{ position: "absolute", top: 12, right: 12, zIndex: 10 }}>
                    <ModelIndicator modelNumber={2} modelName="" status={model2Status} compact />
                  </div>
                  {emissionData ? (
                    <ScoreRing score={emissionData.carbon_score} value={emissionData.carbon_score_value} />
                  ) : (
                    <div
                      className="card"
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "center",
                        padding: 24,
                        gap: 12,
                        minHeight: 200,
                      }}
                    >
                      <div
                        style={{
                          width: 80,
                          height: 80,
                          borderRadius: "50%",
                          border: "8px solid var(--border)",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                        }}
                      >
                        <span style={{ fontFamily: "Syne, sans-serif", fontSize: 20, fontWeight: 800, color: "var(--text-muted)" }}>
                          ?
                        </span>
                      </div>
                      <p style={{ fontSize: 12, color: "var(--text-muted)", textAlign: "center", fontFamily: "Syne, sans-serif", fontWeight: 600 }}>
                        Carbon Score
                      </p>
                    </div>
                  )}
                </div>

                <div style={{ position: "relative" }}>
                  <div style={{ position: "absolute", top: 12, right: 12, zIndex: 10 }}>
                    <ModelIndicator modelNumber={1} modelName="" status={model1Status} compact />
                  </div>
                  {emissionData ? (
                    <PieBreakdown data={emissionData} />
                  ) : (
                    <div
                      className="card"
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        padding: 24,
                        minHeight: 200,
                      }}
                    >
                      <p style={{ fontSize: 13, color: "var(--text-muted)", textAlign: "center" }}>
                        Calculate emissions to see AI-powered breakdown
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Trend Chart with Model Indicator */}
          <div style={{ marginBottom: 20, position: "relative" }}>
            <div style={{ position: "absolute", top: 20, right: 20, zIndex: 10 }}>
              <ModelIndicator modelNumber={3} modelName="" status={model3Status} compact />
            </div>
            <TrendChart
              history={history}
              forecast={forecast}
              modelUsed={trendModelUsed}
              currentMonth={
                emissionData
                  ? {
                      electricity_co2: emissionData.electricity_co2,
                      fuel_co2: emissionData.fuel_co2,
                      total_co2: emissionData.total_co2,
                    }
                  : undefined
              }
            />
          </div>

          {/* Bottom: Suggestions + Simulator */}
          <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 20, marginBottom: 20 }}>
            <AISuggestions
              suggestions={suggestions}
              summary={summary}
              estimatedReduction={estimatedReduction}
              loading={aiLoading}
              onFetch={handleAISuggestions}
              hasData={!!emissionData}
              modelUsed={suggestionsModelUsed}
            />
            <Simulator
              electricity_kwh={inputs.electricity}
              fuel_litres={inputs.fuel}
              initialTotal={emissionData?.total_co2 ?? 0}
            />
          </div>

          {/* Report */}
          <div
            style={{
              padding: "16px",
              background: "linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(168, 85, 247, 0.1))",
              border: "1px solid var(--border)",
              borderRadius: 12,
            }}
          >
            <div style={{ marginBottom: 12 }}>
              <p style={{ fontSize: 13, color: "var(--text-muted)", margin: 0 }}>
                Generate a comprehensive PDF report with AI insights and ROI analysis
              </p>
            </div>
            <ReportButton
              emissionData={emissionData}
              suggestions={suggestions}
              summary={summary}
              history={history}
              forecast={forecast}
              modelsUsed={{
                emissions_model: "RandomForest ML",
                trend_model: trendModelUsed,
              }}
              hasData={!!emissionData}
            />
          </div>

          {/* Footer */}
          <div
            style={{
              marginTop: 48,
              paddingTop: 24,
              borderTop: "1px solid var(--border)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <Leaf size={14} color="var(--green-primary)" />
              <span style={{ fontFamily: "Syne, sans-serif", fontWeight: 700, fontSize: 14, color: "var(--text-muted)" }}>
                CarbonSense AI • Powered by 3 ML Models
              </span>
            </div>
            <p style={{ fontSize: 12, color: "var(--text-muted)", fontFamily: "DM Mono, monospace" }}>
              Real-time AI predictions • Live model monitoring
            </p>
          </div>
        </main>
      </div>
    </>
  );
}
