import React from 'react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface ChartCardProps {
  title: string;
  subtitle?: string;
  data: any[];
  dataKey: string;
  type?: 'line' | 'area';
}

const ChartCard: React.FC<ChartCardProps> = ({ title, subtitle, data, dataKey, type = 'line' }) => {
  return (
    <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6 hover:border-[#333333] transition-all duration-300 hover:shadow-xl hover:shadow-white/5">
      <div className="mb-6">
        <h3 className="text-white font-semibold text-lg">{title}</h3>
        {subtitle && <p className="text-[#666666] text-sm mt-1">{subtitle}</p>}
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          {type === 'area' ? (
            <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ffffff" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#ffffff" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#222222" vertical={false} />
              <XAxis dataKey="name" stroke="#666666" style={{ fontSize: '12px' }} />
              <YAxis stroke="#666666" style={{ fontSize: '12px' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1a1a1a',
                  border: '1px solid #222222',
                  borderRadius: '8px',
                  color: '#ffffff',
                }}
              />
              <Area
                type="monotone"
                dataKey={dataKey}
                stroke="#ffffff"
                fillOpacity={1}
                fill="url(#colorValue)"
                strokeWidth={2}
              />
            </AreaChart>
          ) : (
            <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#222222" vertical={false} />
              <XAxis dataKey="name" stroke="#666666" style={{ fontSize: '12px' }} />
              <YAxis stroke="#666666" style={{ fontSize: '12px' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1a1a1a',
                  border: '1px solid #222222',
                  borderRadius: '8px',
                  color: '#ffffff',
                }}
              />
              <Line
                type="monotone"
                dataKey={dataKey}
                stroke="#ffffff"
                dot={false}
                strokeWidth={2}
              />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ChartCard;
