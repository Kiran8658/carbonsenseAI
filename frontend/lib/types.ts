export type ModelConnectionStatus = "connected" | "disconnected" | "processing";

export interface EmissionData {
  electricity_co2: number;
  fuel_co2: number;
  total_co2: number;
  carbon_score: string;
  carbon_score_value: number;
  breakdown_percentage: {
    electricity: number;
    fuel: number;
  };
}

export interface Suggestion {
  title: string;
  description: string;
  impact: string;
  savings_percentage: number;
  category: string;
  priority: "Low" | "Medium" | "High" | "Critical";
}

export interface SimulatorResult {
  before_co2: number;
  after_co2: number;
  savings_co2: number;
  savings_percentage: number;
  electricity_before: number;
  electricity_after: number;
  fuel_before: number;
  fuel_after: number;
}

export interface HistoryEntry {
  month: string;
  electricity_co2: number;
  fuel_co2: number;
  total_co2: number;
}

export interface HistoryResponse {
  success: boolean;
  history: HistoryEntry[];
  forecast?: number[];
  model_used?: string;
}

export interface BackendModelStatus {
  name: string;
  type: string;
  status: "connected" | "disconnected";
  description: string;
}

export interface HealthResponse {
  status: string;
  details: {
    emissions_predictor: BackendModelStatus;
    carbon_scorer: BackendModelStatus;
    trend_forecaster: BackendModelStatus;
  };
}

export const SCORE_COLORS: Record<string, string> = {
  Excellent: "#22c55e",
  Good: "#84cc16",
  Average: "#f59e0b",
  Poor: "#f97316",
  Critical: "#ef4444",
};
