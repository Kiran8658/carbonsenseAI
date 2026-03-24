import React from 'react';
import { TrendingDown, TrendingUp, Zap } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string;
  change?: string;
  isNegative?: boolean;
  icon?: React.ReactNode;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, change, isNegative, icon }) => {
  return (
    <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6 hover:border-[#333333] transition-all duration-300 hover:shadow-xl hover:shadow-white/5">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-[#888888] text-sm font-medium mb-2">{title}</p>
          <p className="text-3xl font-bold text-white mb-4">{value}</p>
          {change && (
            <div className="flex items-center gap-1">
              {isNegative ? (
                <TrendingDown size={16} className="text-white" />
              ) : (
                <TrendingUp size={16} className="text-white" />
              )}
              <span className={`text-sm font-medium ${isNegative ? 'text-white' : 'text-white'}`}>
                {change}
              </span>
            </div>
          )}
        </div>
        {icon && <div className="text-[#333333]">{icon}</div>}
      </div>
    </div>
  );
};

export default StatCard;
