import React from 'react';
import { Search, Bell, User } from 'lucide-react';

const Navbar: React.FC = () => {
  return (
    <nav className="ml-64 h-16 bg-[#0a0a0a] border-b border-[#222222] flex items-center justify-between px-8 sticky top-0 z-40">
      {/* Search Bar */}
      <div className="flex-1 max-w-md">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#666666]" size={18} />
          <input
            type="text"
            placeholder="Search emissions, reports..."
            className="w-full bg-[#111111] border border-[#222222] rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder-[#666666] focus:outline-none focus:border-[#333333] transition-all"
          />
        </div>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-4 ml-8">
        {/* Notifications */}
        <button className="relative p-2 rounded-lg hover:bg-[#111111] transition-all text-[#888888] hover:text-white">
          <Bell size={20} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-white rounded-full"></span>
        </button>

        {/* Profile */}
        <button className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-[#111111] transition-all">
          <div className="w-8 h-8 bg-[#222222] rounded-lg flex items-center justify-center">
            <User size={16} className="text-[#888888]" />
          </div>
          <span className="text-sm text-white font-medium hidden sm:block">Profile</span>
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
