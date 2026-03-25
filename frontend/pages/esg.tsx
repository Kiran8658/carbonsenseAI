import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import ESGScoringDashboard from '../components/ESGScoringDashboard';
import { featureFlagManager, FeatureFlag } from '../lib/featureFlags';
import Navbar from '../components/Navbar';

export default function ESGPage() {
  const router = useRouter();
  const [isEnabled, setIsEnabled] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkFeatureFlag = async () => {
      await featureFlagManager.initialize();
      setIsEnabled(featureFlagManager.isEnabled(FeatureFlag.ESG_SCORING));
      setLoading(false);
    };

    checkFeatureFlag();
  }, []);

  if (loading) {
    return (
      <div className="w-full h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="spinner mb-4"></div>
          <p className="text-gray-600">Loading ESG Scoring Module...</p>
        </div>
      </div>
    );
  }

  if (!isEnabled) {
    return (
      <div className="w-full min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-4xl mx-auto p-6 mt-20 text-center">
          <h1 className="text-3xl font-bold text-gray-800 mb-4">Feature Not Available</h1>
          <p className="text-gray-600 mb-8">
            The ESG Scoring Module is not currently enabled. Please contact the administrator.
          </p>
          <button
            onClick={() => router.push('/')}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full min-h-screen bg-gray-50">
      <Navbar />
      <div className="pt-20">
        <ESGScoringDashboard />
      </div>
    </div>
  );
}
