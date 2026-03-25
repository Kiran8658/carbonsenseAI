import axios from "axios";

// Dynamically set API URL based on current host (supports localhost and local network)
const getApiUrl = () => {
  if (typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    return `http://${host}:8005`;
  }
  return "http://localhost:8005";
};

const API_URL = getApiUrl();

const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
});

export async function calculateEmissions(electricity_kwh: number, fuel_litres: number) {
  const { data } = await api.post("/api/calculate", { electricity_kwh, fuel_litres });
  return data;
}

export async function getAISuggestions(payload: {
  electricity_kwh: number;
  fuel_litres: number;
  total_co2: number;
  business_type?: string;
}) {
  const { data } = await api.post("/api/ai-suggestions", payload);
  return data;
}

export async function simulateReduction(payload: {
  electricity_kwh: number;
  fuel_litres: number;
  electricity_reduction_pct: number;
  fuel_reduction_pct: number;
}) {
  const { data } = await api.post("/api/simulate", payload);
  return data;
}

export async function getHistory() {
  const { data } = await api.get("/api/history");
  return data;
}

export async function generateReport(payload: {
  emission_data: any;
  suggestions: any[];
  summary: string;
  history: any[];
  forecast?: number[];
  models_used?: Record<string, string>;
}) {
  const { data } = await api.post("/api/reports/generate", payload);
  return data;
}

export async function listReports() {
  const { data } = await api.get("/api/reports/list");
  return data;
}

export async function downloadReport(reportId: string) {
  // This triggers a browser download
  window.location.href = `${API_URL}/api/reports/download/${reportId}`;
}

export async function deleteReport(reportId: string) {
  const { data } = await api.delete(`/api/reports/delete/${reportId}`);
  return data;
}

export async function getHealthStatus() {
  const { data } = await api.get("/health");
  return data;
}

export async function getAIInsights(payload: {
  emission_data: any;
  suggestions: any[];
  history: any[];
  forecast?: number[];
}) {
  const { data } = await api.post("/api/reports/ai-insights", payload);
  return data;
}

export default api;
