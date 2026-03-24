import React from 'react';

interface TransactionItem {
  id: string;
  type: string;
  source: string;
  value: string;
  date: string;
}

interface TransactionTableProps {
  data: TransactionItem[];
}

const TransactionTable: React.FC<TransactionTableProps> = ({ data }) => {
  return (
    <div className="bg-[#111111] border border-[#222222] rounded-2xl p-6 hover:border-[#333333] transition-all duration-300 hover:shadow-xl hover:shadow-white/5">
      <h3 className="text-white font-semibold text-lg mb-6">Recent Emissions</h3>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-[#222222]">
              <th className="text-left px-4 py-3 text-[#666666] text-sm font-medium">Source</th>
              <th className="text-left px-4 py-3 text-[#666666] text-sm font-medium">Type</th>
              <th className="text-right px-4 py-3 text-[#666666] text-sm font-medium">CO₂ (kg)</th>
              <th className="text-left px-4 py-3 text-[#666666] text-sm font-medium">Date</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item) => (
              <tr
                key={item.id}
                className="border-b border-[#1a1a1a] hover:bg-[#1a1a1a] transition-all"
              >
                <td className="px-4 py-3 text-white text-sm font-medium">{item.source}</td>
                <td className="px-4 py-3 text-[#888888] text-sm">{item.type}</td>
                <td className="px-4 py-3 text-white text-sm font-semibold text-right">{item.value}</td>
                <td className="px-4 py-3 text-[#666666] text-sm">{item.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TransactionTable;
