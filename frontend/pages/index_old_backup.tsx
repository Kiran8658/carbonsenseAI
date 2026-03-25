import { useState, useEffect } from "react";
import Head from "next/head";
import { Zap, Fuel, Leaf, TrendingDown, Wind } from "lucide-react";
import Navbar from "../components/ui/Navbar";
import MetricCard from "../components/ui/MetricCard";
import ScoreRing from "../components/ui/ScoreRing";
import InputForm from "../components/dashboard/InputForm";
import PieBreakdown from "../components/charts/PieBreakdown";
import TrendChart from "../components/charts/TrendChart";
import AISuggestions from "../components/dashboard/AISuggestions";
import ReportButton from "../components/dashboard/ReportButton";
import Simulator from "../components/dashboard/Simulator";
import AIModelsShowcase from "../components/dashboard/AIModelsShowcase";
import { calculateEmissions, getAISuggestions, getHistory } from "../lib/api";
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

  useEffect(() => {
    getHistory()
      .then((d) => {
        setHistory(d.history);
        setForecast(d.forecast || []);
        setTrendModelUsed(d.model_used || "");
      })
      .catch(() => {});
  }, []);

  const handleCalculate = async (electricity: number, fuel: number) => {
    setCalcLoading(true);
    setInputs({ electricity, fuel });
    try {
      const res = await calculateEmissions(electricity, fuel);
      setEmissionData(res.data);
    } catch (e) {
      console.error(e);
      alert("Could not connect to backend. Make sure FastAPI is running on port 8005.");
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
        <title>CarbonSense AI — MSME Carbon Tracker</title>
        <meta name="description" content="AI-powered carbon footprint tracker for MSMEs" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🌿</text></svg>" />
      </Head>

      <div style={{ minHeight: "100vh", background: "var(--bg-primary)" }} className="dot-pattern">
        <Navbar />

        <main style={{ maxWidth: 1280, margin: "0 auto", padding: "32px 24px 64px" }}>

          {/* Hero section */}
          <div style={{ marginBottom: 40, maxWidth: 600 }}>
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                background: "var(--green-glow)",
                border: "1px solid var(--green-dim)",
                borderRadius: 20,
                padding: "4px 14px",
                marginBottom: 16,
              }}
            >
              <Wind size={12} color="var(--green-primary)" />
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
                Hackathon Demo — CarbonSense AI
              </span>
            </div>
            <h1
              style={{
                fontFamily: "Syne, sans-serif",
                fontSize: "clamp(28px, 4vw, 44px)",
                fontWeight: 800,
                color: "var(--text-primary)",
                lineHeight: 1.1,
                letterSpacing: "-0.03em",
                marginBottom: 12,
              }}
            >
              Track & Reduce Your
              <br />
              <span
                style={{
                  background: "linear-gradient(135deg, #22c55e, #86efac)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}
              >
                Carbon Footprint
              </span>
            </h1>
            <p style={{ fontSize: 15, color: "var(--text-secondary)", maxWidth: 480, lineHeight: 1.6 }}>
              AI-powered emission tracking for MSMEs. Calculate, visualize, and act on your carbon data — in minutes.
            </p>
          </div>

          {/* AI Models Showcase - Prominent display for hackathon judges */}
          <AIModelsShowcase />

          {/* Top grid: Form + Metrics */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "340px 1fr",
              gap: 20,
              marginBottom: 20,
            }}
          >
            {/* Input Form */}
            <div>
              <InputForm onSubmit={handleCalculate} loading={calcLoading} />
            </div>

            {/* Metrics + Score */}
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              {/* Metric cards row */}
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(3, 1fr)",
                  gap: 14,
                }}
              >
                <MetricCard
                  label="Total CO₂"
                  value={emissionData ? emissionData.total_co2.toFixed(1) : "—"}
                  unit="kg/mo"
                  icon={<Leaf size={20} color="var(--green-primary)" />}
                  subtitle={emissionData ? "Monthly footprint" : "Awaiting input"}
                  delay={0}
                />
                <MetricCard
                  label="Electricity"
                  value={emissionData ? emissionData.electricity_co2.toFixed(1) : "—"}
                  unit="kg CO₂"
                  icon={<Zap size={20} color="#f59e0b" />}
                  color="#f59e0b"
                  subtitle={emissionData ? `${emissionData.breakdown_percentage.electricity}% share` : ""}
                  delay={100}
                />
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

              {/* Score + Pie row */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1.6fr", gap: 14, flex: 1 }}>
                {emissionData ? (
                  <ScoreRing
                    score={emissionData.carbon_score}
                    value={emissionData.carbon_score_value}
                  />
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
                      <span
                        style={{
                          fontFamily: "Syne, sans-serif",
                          fontSize: 20,
                          fontWeight: 800,
                          color: "var(--text-muted)",
                        }}
                      >
                        ?
                      </span>
                    </div>
                    <p
                      style={{
                        fontSize: 12,
                        color: "var(--text-muted)",
                        textAlign: "center",
                        fontFamily: "Syne, sans-serif",
                        fontWeight: 600,
                      }}
                    >
                      Carbon Score
                    </p>
                  </div>
                )}

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
                    }}
                  >
                    <p style={{ fontSize: 13, color: "var(--text-muted)", textAlign: "center" }}>
                      Calculate emissions to see breakdown chart
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Trend Chart - full width */}
          <div style={{ marginBottom: 20 }}>
            <TrendChart
              history={history}
              forecast={forecast}
              modelUsed={trendModelUsed}
              currentMonth={emissionData ? {
                electricity_co2: emissionData.electricity_co2,
                fuel_co2: emissionData.fuel_co2,
                total_co2: emissionData.total_co2,
              } : undefined}
            />
          </div>

          {/* Bottom grid: AI Suggestions + Simulator */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1.4fr 1fr",
              gap: 20,
            }}
          >
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
              electricityKwh={inputs.electricity}
              fuelLitres={inputs.fuel}
            />
          </div>

          {/* Report Button */}
          <div
            style={{
              marginTop: 20,
              padding: "16px",
              background: "linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(168, 85, 247, 0.1))",
              border: "1px solid var(--border)",
              borderRadius: 12,
            }}
          >
            <div style={{ marginBottom: 12 }}>
              <p style={{ fontSize: 13, color: "var(--text-muted)", margin: 0 }}>
                Ready to take action? Generate a comprehensive PDF report with ROI analysis.
              </p>
            </div>
            <ReportButton
              emissionData={emissionData}
              suggestions={suggestions}
              summary={summary}
              history={history}
              forecast={forecast}
              modelsUsed={{
                emissions_model: suggestionsModelUsed,
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
              flexWrap: "wrap",
              gap: 12,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <Leaf size={14} color="var(--green-primary)" />
              <span
                style={{
                  fontFamily: "Syne, sans-serif",
                  fontWeight: 700,
                  fontSize: 14,
                  color: "var(--text-muted)",
                }}
              >
                CarbonSense AI
              </span>
            </div>
            <p style={{ fontSize: 12, color: "var(--text-muted)", fontFamily: "DM Mono, monospace" }}>
              Emission factors: Electricity 0.82 kg/kWh · Fuel 2.3 kg/litre (India grid)
            </p>
          </div>
        </main>
      </div>
    </>
  );
}
