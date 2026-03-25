"""
Feature Flag System for CarbonSense v2 Features
Allows safe gradual rollout of new features without modifying v1
"""

from enum import Enum
from typing import Dict
import os
import json

class FeatureFlag(Enum):
    """Available feature flags. Default: DISABLED for safety"""
    ESG_SCORING = "esg_scoring"
    LSTM_FORECAST = "lstm_forecast"
    ANOMALY_DETECTION = "anomaly_detection"
    ADVANCED_SIMULATION = "advanced_simulation"
    BENCHMARKING = "benchmarking"
    AI_CHATBOT = "ai_chatbot"
    ALERT_SYSTEM = "alert_system"
    CSV_UPLOAD = "csv_upload"
    ADVANCED_REPORTS = "advanced_reports"


class FeatureFlagManager:
    """Manage feature flags with environment variable overrides"""
    
    def __init__(self):
        # Default: all features disabled (safe default)
        self._flags: Dict[str, bool] = {
            FeatureFlag.ESG_SCORING.value: True,  # Enabled for Phase 1
            FeatureFlag.LSTM_FORECAST.value: True,  # Enabled for Phase 3
            FeatureFlag.ANOMALY_DETECTION.value: True,  # Enabled for Phase 4
            FeatureFlag.ADVANCED_SIMULATION.value: True,  # Enabled for Phase 5
            FeatureFlag.BENCHMARKING.value: True,  # Enabled for Phase 2
            FeatureFlag.CSV_UPLOAD.value: True,  # Enabled for Phase 6
            FeatureFlag.AI_CHATBOT.value: False,
            FeatureFlag.ALERT_SYSTEM.value: False,
            FeatureFlag.ADVANCED_REPORTS.value: False,
        }
        
        # Override from environment variables (if set)
        self._load_from_env()
    
    def _load_from_env(self):
        """Load feature flags from environment variables (FEATURE_FLAG_*)"""
        for flag in FeatureFlag:
            env_key = f"FEATURE_FLAG_{flag.value.upper()}"
            if env_key in os.environ:
                value = os.environ[env_key].lower() in ['true', '1', 'yes', 'enabled']
                self._flags[flag.value] = value
    
    def is_enabled(self, flag: FeatureFlag) -> bool:
        """Check if a feature is enabled"""
        return self._flags.get(flag.value, False)
    
    def enable(self, flag: FeatureFlag) -> None:
        """Manually enable a feature"""
        self._flags[flag.value] = True
    
    def disable(self, flag: FeatureFlag) -> None:
        """Manually disable a feature"""
        self._flags[flag.value] = False
    
    def get_status(self) -> Dict[str, bool]:
        """Get all feature flags status"""
        return self._flags.copy()
    
    def set_status(self, flags: Dict[str, bool]) -> None:
        """Set multiple feature flags at once"""
        for flag_name, value in flags.items():
            if flag_name in self._flags:
                self._flags[flag_name] = value


# Global feature flag manager instance
_feature_manager = FeatureFlagManager()


def get_feature_manager() -> FeatureFlagManager:
    """Get the global feature flag manager"""
    return _feature_manager


def is_feature_enabled(flag: FeatureFlag) -> bool:
    """Convenience function to check if a feature is enabled"""
    return _feature_manager.is_enabled(flag)


def get_enabled_features():
    """Get list of enabled features"""
    return {k: v for k, v in _feature_manager.get_status().items() if v}
