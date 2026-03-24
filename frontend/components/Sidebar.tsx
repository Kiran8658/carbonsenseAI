import React from 'react';
import { BarChart3, Activity, TrendingUp, Settings, LogOut, Home } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/router';

const Sidebar: React.FC = () => {
  const router = useRouter();

  const navItems = [
    { icon: Home, label: 'Dashboard', href: '/' },
    { icon: Activity, label: 'Emissions', href: '/emissions' },
    { icon: BarChart3, label: 'Analytics', href: '/analytics' },
    { icon: TrendingUp, label: 'Reports', href: '/reports' },
  ];

  const isActive = (href: string) => router.pathname === href;

  return (
    <div className="w-64 bg-[#0a0a0a] border-r border-[#222222] h-screen fixed left-0 top-0 flex flex-col">
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-[#222222]">
        <h1 className="text-xl font-bold text-white tracking-tighter">CarbonSense</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-8 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                  active
                    ? 'bg-[#1a1a1a] border border-[#333333] text-white shadow-lg'
                    : 'text-[#888888] hover:text-white hover:bg-[#111111]'
                }`}
              >
                <Icon size={20} />
                <span className="text-sm font-medium">{item.label}</span>
              </Link>
            );
        })}
      </nav>

      {/* Bottom Actions */}
      <div className="px-4 py-6 border-t border-[#222222] space-y-2">
        <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-[#888888] hover:text-white hover:bg-[#111111] transition-all">
          <Settings size={20} />
          <span className="text-sm font-medium">Settings</span>
        </button>
        <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-[#888888] hover:text-white hover:bg-[#111111] transition-all">
          <LogOut size={20} />
          <span className="text-sm font-medium">Logout</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
