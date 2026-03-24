import { Download, Loader2, CheckCircle, AlertCircle } from "lucide-react";
import { useState } from "react";
import { generateReport, downloadReport } from "../../lib/api";
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
  const [reportId, setReportId] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState("");

  const handleGenerateReport = async () => {
    if (!hasData) {
      alert("Please calculate emissions first");
      return;
    }

    setLoading(true);
    setStatus("generating");
    setErrorMessage("");

    try {
      const response = await generateReport({
        emission_data: emissionData,
        suggestions: suggestions,
        summary: summary,
        history: history,
        forecast: forecast,
        models_used: modelsUsed,
      });

      if (response.success) {
        setStatus("success");
        setReportId(response.report_id);
        
        // Auto-download after 1 second
        setTimeout(() => {
          downloadReport(response.report_id);
        }, 1000);

        // Reset after 3 seconds
        setTimeout(() => {
          setStatus("idle");
          setReportId("");
        }, 3000);
      }
    } catch (error: any) {
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
      <ConnectionLight status={allModelsStatus} label="Report Data Pipeline" compact />
      <button
        className="btn-primary"
        onClick={handleGenerateReport}
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
            Report Ready!
          </>
        ) : status === "error" ? (
          <>
            <AlertCircle size={14} color="#ef4444" />
            Error
          </>
        ) : (
          <>
            <Download size={14} />
            Download PDF Report
          </>
        )}
      </button>

      {status === "error" && (
        <span style={{ fontSize: 12, color: "#ef4444" }}>
          {errorMessage}
        </span>
      )}

      {status === "success" && (
        <span style={{ fontSize: 12, color: "#22c55e" }}>
          ✅ Report generated and downloading...
        </span>
      )}
    </div>
  );
}
