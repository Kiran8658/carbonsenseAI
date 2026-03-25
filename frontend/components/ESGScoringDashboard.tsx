import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';

interface ESGScoreData {
  environmental_score: number;
  social_score: number;
  governance_score: number;
  overall_score: number;
  grade: string;
  recommendations: Array<{
    category: string;
    priority: string;
    action: string;
    impact: string;
  }>;
}

interface ESGBenchmark {
  industry: string;
  your_score: number;
  industry_average: number;
  industry_leader_score: number;
  percentile: number;
  vs_average: number;
  performance: string;
}

export default function ESGScoringDashboard() {
  const [loading, setLoading] = useState(false);
  const [esgData, setEsgData] = useState<ESGScoreData | null>(null);
  const [benchmark, setBenchmark] = useState<ESGBenchmark | null>(null);
  
  const [formData, setFormData] = useState({
    co2_kg: 500,
    annual_savings_reduction: 15,
    renewable_usage_pct: 20,
    carbon_offset_tons: 5,
    employees: 25,
    industry_sector: 'Retail',
    certified_emissions_plan: false,
    esg_report_published: false,
    third_party_audit: false,
    sustainability_commitment: false,
    community_programs: false,
    dei_programs: false,
    data_transparency: false,
  });

  const calculateESGScore = async () => {
    setLoading(true);
    try {
      const host = process.env.NEXT_PUBLIC_API_HOST || 'localhost';
      const response = await fetch(`http://${host}:8888/api/v2/esg-score`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const data = await response.json();
        setEsgData(data.data);
        setBenchmark(data.benchmark);
      } else {
        console.error('Failed to calculate ESG score');
      }
    } catch (error) {
      console.error('Error calculating ESG score:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, type, value } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : parseFloat(value) || value,
    });
  };

  const radarData = esgData ? [
    { category: 'Environmental', value: esgData.environmental_score },
    { category: 'Social', value: esgData.social_score },
    { category: 'Governance', value: esgData.governance_score },
  ] : [];

  const getGradeColor = (grade: string) => {
    const colorMap: { [key: string]: string } = {
      'A+': 'text-green-600 bg-green-50',
      'A': 'text-green-500 bg-green-50',
      'B+': 'text-blue-600 bg-blue-50',
      'B': 'text-blue-500 bg-blue-50',
      'C+': 'text-yellow-600 bg-yellow-50',
      'C': 'text-yellow-500 bg-yellow-50',
      'D': 'text-orange-600 bg-orange-50',
      'F': 'text-red-600 bg-red-50',
    };
    return colorMap[grade] || 'text-gray-600 bg-gray-50';
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-6 bg-white">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">ESG Scoring Module (Beta)</h1>
        <p className="text-gray-600">Calculate your organization's Environmental, Social & Governance score</p>
      </div>

      {/* Input Form */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8 p-6 bg-gray-50 rounded-lg">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">CO₂ Emissions (kg/year)</label>
          <input
            type="number"
            name="co2_kg"
            value={formData.co2_kg}
            onChange={handleInputChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Annual Reduction Target (%)</label>
          <input
            type="number"
            name="annual_savings_reduction"
            value={formData.annual_savings_reduction}
            onChange={handleInputChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Renewable Energy (%)</label>
          <input
            type="number"
            name="renewable_usage_pct"
            value={formData.renewable_usage_pct}
            onChange={handleInputChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Carbon Offset (tons)</label>
          <input
            type="number"
            name="carbon_offset_tons"
            value={formData.carbon_offset_tons}
            onChange={handleInputChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Number of Employees</label>
          <input
            type="number"
            name="employees"
            value={formData.employees}
            onChange={handleInputChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Industry Sector</label>
          <select
            name="industry_sector"
            value={formData.industry_sector}
            onChange={handleInputChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value="Retail">Retail</option>
            <option value="Manufacturing">Manufacturing</option>
            <option value="Tech">Tech</option>
            <option value="Energy">Energy</option>
            <option value="Finance">Finance</option>
            <option value="General">General</option>
          </select>
        </div>

        {/* Checkboxes */}
        <div className="md:col-span-2 grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { name: 'certified_emissions_plan', label: 'Certified Emissions Plan' },
            { name: 'esg_report_published', label: 'ESG Report Published' },
            { name: 'third_party_audit', label: 'Third-party Audit' },
            { name: 'sustainability_commitment', label: 'Sustainability Commitment' },
            { name: 'community_programs', label: 'Community Programs' },
            { name: 'dei_programs', label: 'D&I Programs' },
            { name: 'data_transparency', label: 'Data Transparency' },
          ].map((checkbox) => (
            <label key={checkbox.name} className="flex items-center">
              <input
                type="checkbox"
                name={checkbox.name}
                checked={formData[checkbox.name as keyof typeof formData] as boolean}
                onChange={handleInputChange}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">{checkbox.label}</span>
            </label>
          ))}
        </div>

        <button
          onClick={calculateESGScore}
          disabled={loading}
          className="md:col-span-2 w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Calculating...' : 'Calculate ESG Score'}
        </button>
      </div>

      {/* Results */}
      {esgData && (
        <div className="space-y-8">
          {/* Score Summary */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="p-4 bg-cyan-50 rounded-lg border border-cyan-200">
              <p className="text-gray-600 text-sm mb-1">Environmental</p>
              <p className="text-3xl font-bold text-cyan-600">{esgData.environmental_score}</p>
            </div>

            <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
              <p className="text-gray-600 text-sm mb-1">Social</p>
              <p className="text-3xl font-bold text-purple-600">{esgData.social_score}</p>
            </div>

            <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
              <p className="text-gray-600 text-sm mb-1">Governance</p>
              <p className="text-3xl font-bold text-orange-600">{esgData.governance_score}</p>
            </div>

            <div className={`p-4 rounded-lg border-2 ${getGradeColor(esgData.grade)}`}>
              <p className="text-gray-600 text-sm mb-1">Overall Score</p>
              <p className="text-3xl font-bold">{esgData.overall_score}</p>
              <p className={`text-4xl font-bold mt-2 ${getGradeColor(esgData.grade).split(' ')[0]}`}>{esgData.grade}</p>
            </div>
          </div>

          {/* Radar Chart */}
          {radarData.length > 0 && (
            <div className="p-6 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">ESG Score Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="category" />
                  <PolarRadiusAxis angle={90} domain={[0, 100]} />
                  <Radar name="Score" dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Benchmark Comparison */}
          {benchmark && (
            <div className="p-6 bg-blue-50 rounded-lg border border-blue-200">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Industry Benchmark</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-gray-600 text-sm">Your Score</p>
                  <p className="text-2xl font-bold text-blue-600">{benchmark.your_score}</p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm">Industry Average</p>
                  <p className="text-2xl font-bold text-gray-600">{benchmark.industry_average}</p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm">vs Average</p>
                  <p className={`text-2xl font-bold ${benchmark.vs_average > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {benchmark.vs_average > 0 ? '+' : ''}{benchmark.vs_average.toFixed(1)}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm">Percentile</p>
                  <p className="text-2xl font-bold text-purple-600">{benchmark.percentile.toFixed(0)}%</p>
                </div>
              </div>
            </div>
          )}

          {/* Recommendations */}
          {esgData.recommendations.length > 0 && (
            <div className="p-6 bg-green-50 rounded-lg border border-green-200">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Recommendations</h3>
              <div className="space-y-3">
                {esgData.recommendations.map((rec, idx) => (
                  <div key={idx} className="p-4 bg-white rounded border-l-4 border-green-600">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-semibold text-gray-800">{rec.action}</h4>
                      <span className={`px-2 py-1 text-xs font-bold rounded ${
                        rec.priority === 'HIGH' ? 'bg-red-100 text-red-800' :
                        rec.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {rec.priority}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{rec.impact}</p>
                    <p className="text-xs text-gray-500">Category: {rec.category}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
