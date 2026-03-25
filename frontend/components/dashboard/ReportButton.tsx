import { Download, Loader2, CheckCircle, AlertCircle } from "lucide-react";
import { useState } from "react";
import axios from "axios";
import ConnectionLight from "../ui/ConnectionLight";
import { ModelConnectionStatus } from "../../lib/types";

interface ReportButtonProps {
  emissionData: any;
  suggestions: any[];
  summary: string;
  history: any[];
  forecast?: number[];
  modelsUsed?: Record<string, string>;
  hasData: boolean;
  allModelsStatus?: ModelConnectionStatus;
}

const getApiUrl = () => {
  if (typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    return `http://${host}:8888`;
  }
  return "http://localhost:8888";
};

const API_URL = getApiUrl();

export default function ReportButton({
  emissionData,
  suggestions,
  summary,
  history,
  forecast,
  modelsUsed,
  hasData,
  allModelsStatus = "disconnected",
}: ReportButtonProps) {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<"idle" | "generating" | "success" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");

  const handleGenerateAndDownloadReport = async () => {
    if (!hasData) {
      alert("Please calculate emissions first");
      return;
    }

    setLoading(true);
    setStatus("generating");
    setErrorMessage("");

    try {
      const response = await axios.post(
        `${API_URL}/api/reports/generate-download`,
        {
          emission_data: emissionData,
          suggestions: suggestions,
          summary: summary,
          history: history,
          forecast: forecast,
          models_used: modelsUsed,
        },
        {
          responseType: "blob",
          timeout: 30000,
        }
      );

      const blob = response.data;

      if (!blob || blob.size === 0) {
        throw new Error("Received empty PDF");
      }

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `CarbonSense_Report_${new Date().toISOString().split("T")[0]}.pdf`
      );
      document.body.appendChild(link);
      link.click();

      setTimeout(() => {
        link.remove();
        window.URL.revokeObjectURL(url);
      }, 100);

      setStatus("success");
      setTimeout(() => {
        setStatus("idle");
      }, 2000);
    } catch (error: any) {
      console.error("Report generation error:", error);
      setStatus("error");
      setErrorMessage(error.message || "Failed to generate report");

      setTimeout(() => {
        setStatus("idle");
        setErrorMessage("");
      }, 3000);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center" }}>
      <ConnectionLight status={allModelsStatus} label="Report Pipeline" compact />
      <button
        className="btn-primary"
        onClick={handleGenerateAndDownloadReport}
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
            Generating Report...
          </>
        ) : status === "success" ? (
          <>
            <CheckCircle size={14} color="#22c55e" />
            Downloaded!
          </>
        ) : status === "error" ? (
          <>
            <AlertCircle size={14} color="#ef4444" />
            Failed
          </>
        ) : (
          <>
            <Download size={14} />
            Generate & Download PDF
          </>
        )}
      </button>

      {errorMessage && (
        <span style={{ fontSize: 11, color: "#ef4444" }}>
          {errorMessage}
        </span>
      )}
    </div>
  );
}
