/**
 * Feature Flag System for Frontend
 * Manages v2 feature availability in the UI
 */

export enum FeatureFlag {
  ESG_SCORING = 'esg_scoring',
  LSTM_FORECAST = 'lstm_forecast',
  ANOMALY_DETECTION = 'anomaly_detection',
  ADVANCED_SIMULATION = 'advanced_simulation',
  BENCHMARKING = 'benchmarking',
  AI_CHATBOT = 'ai_chatbot',
  ALERT_SYSTEM = 'alert_system',
  CSV_UPLOAD = 'csv_upload',
  ADVANCED_REPORTS = 'advanced_reports',
}

export interface FeatureFlagConfig {
  [key: string]: boolean;
}

class FeatureFlagManager {
  private flags: FeatureFlagConfig = {};
  private initialized = false;

  async initialize(): Promise<void> {
    if (this.initialized) return;

    try {
      // Get feature flags from backend
      const host = process.env.NEXT_PUBLIC_API_HOST || 'localhost';
      const response = await fetch(`http://${host}:8888/api/v2/features`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (response.ok) {
        const data = await response.json();
        this.flags = data.features;
      } else {
        // Fallback to safe defaults if backend call fails
        this._setDefaultFlags();
      }
    } catch (error) {
      // Fallback to safe defaults
      console.warn('Failed to load feature flags from backend, using defaults');
      this._setDefaultFlags();
    }

    this.initialized = true;
  }

  private _setDefaultFlags(): void {
    this.flags = {
      [FeatureFlag.ESG_SCORING]: true,
      [FeatureFlag.LSTM_FORECAST]: false,
      [FeatureFlag.ANOMALY_DETECTION]: false,
      [FeatureFlag.ADVANCED_SIMULATION]: false,
      [FeatureFlag.BENCHMARKING]: false,
      [FeatureFlag.AI_CHATBOT]: false,
      [FeatureFlag.ALERT_SYSTEM]: false,
      [FeatureFlag.CSV_UPLOAD]: false,
      [FeatureFlag.ADVANCED_REPORTS]: false,
    };
  }

  isEnabled(flag: FeatureFlag): boolean {
    return this.flags[flag] ?? false;
  }

  getFlags(): FeatureFlagConfig {
    return { ...this.flags };
  }

  isInitialized(): boolean {
    return this.initialized;
  }
}

export const featureFlagManager = new FeatureFlagManager();
