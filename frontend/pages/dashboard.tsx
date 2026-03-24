import React, { useEffect, useState } from "react";
import axios from "axios";
import Sidebar from "@/components/Sidebar";
import Navbar from "@/components/Navbar";
import StatCard from "@/components/StatCard";
import ChartCard from "@/components/ChartCard";
import TransactionTable from "@/components/TransactionTable";
import { Activity, Zap, TrendingUp, AlertCircle } from "lucide-react";

interface DashboardData {
  totalEmissions: number;
  monthlyEmissions: number;
  reductionGoal: number;
  sources: any[];
  trend: any[];
  transactions: any[];
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [backendStatus, setBackendStatus] = useState<"online" | "offline">("offline");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("http://localhost:8000/health");
        setBackendStatus("online");

        const dashboardResponse = await axios.get("http://localhost:8000/api/dashboard");
        setData(dashboardResponse.data);
        setLoading(false);
      } catch (error) {
        setBackendStatus("offline");
        setLoading(false);
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  // Mock data for development
  const mockData: DashboardData = {
    totalEmissions: 2456.8,
    monthlyEmissions: 485.2,
    reductionGoal: 20,
    sources: [
      { name: "Transportation", emissions: 800 },
      { name: "Energy", emissions: 900 },
      { name: "Manufacturing", emissions: 450 },
      { name: "Waste", emissions: 306.8 },
    ],
    trend: [
      { name: "Jan", value: 420 },
      { name: "Feb", value: 450 },
      { name: "Mar", value: 480 },
      { name: "Apr", value: 510 },
      { name: "May", value: 490 },
      { name: "Jun", value: 485 },
    ],
    transactions: [
      { id: "1", source: "Company Fleet", type: "Transportation", value: "245.6", date: "Today" },
      { id: "2", source: "Office Building", type: "Energy", value: "156.8", date: "Yesterday" },
      { id: "3", source: "Manufacturing", type: "Production", value: "340.2", date: "2 days ago" },
      { id: "4", source: "Waste Management", type: "Disposal", value: "89.5", date: "3 days ago" },
    ],
  };

  const displayData = data || mockData;

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      <Sidebar />
      <Navbar />

      <main className="ml-64 mt-16 p-8 space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white tracking-tight mb-2">Dashboard</h1>
            <p className="text-[#888888]">
              Carbon emissions tracking & analytics
              {backendStatus === "offline" && (
                <span className="ml-4 inline-flex items-center gap-2 px-3 py-1 bg-[#1a1a1a] border border-[#333333] rounded-lg">
                  <AlertCircle size={14} className="text-white" />
                  <span className="text-xs text-white">Backend Offline</span>
                </span>
              )}
            </p>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <StatCard
            title="Total Emissions"
            value={`${displayData.totalEmissions.toFixed(1)} kg`}
            change="↑ 2.4% from last month"
            isNegative={true}
            icon={<Activity size={32} />}
          />
          <StatCard
            title="This Month"
            value={`${displayData.monthlyEmissions.toFixed(1)} kg`}
            change="↓ 5.1% reduction"
            isNegative={false}
            icon={<TrendingUp size={32} />}
          />
          <StatCard
            title="Reduction Goal"
            value={`${displayData.reductionGoal}%`}
            change="3 months left"
            icon={<Zap size={32} />}
          />
          <StatCard
            title="Next Milestone"
            value="2,200 kg"
            change="256.8 kg remaining"
            icon={<AlertCircle size={32} />}
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartCard
            title="Emissions Trend"
            subtitle="Last 6 months performance"
            data={displayData.trend}
            dataKey="value"
            type="area"
          />
          <ChartCard
            title="Emissions by Source"
            subtitle="Current month breakdown"
            data={displayData.sources}
            dataKey="emissions"
            type="line"
          />
        </div>

        {/* Transactions */}
        <div>
          <TransactionTable data={displayData.transactions} />
        </div>

        {/* Footer Info */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
            <h4 className="text-white font-semibold mb-2">Sustainability Score</h4>
            <p className="text-3xl font-bold text-white">78/100</p>
            <p className="text-[#666666] text-sm mt-2">Well above average</p>
          </div>
          <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
            <h4 className="text-white font-semibold mb-2">Carbon Offset</h4>
            <p className="text-3xl font-bold text-white">425.3 kg</p>
            <p className="text-[#666666] text-sm mt-2">Equivalent to 22 trees</p>
          </div>
          <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6">
            <h4 className="text-white font-semibold mb-2">Monthly Comparison</h4>
            <p className="text-3xl font-bold text-white">↓ 5.1%</p>
            <p className="text-[#666666] text-sm mt-2">vs previous month</p>
          </div>
        </div>
      </main>
    </div>
  );
}
